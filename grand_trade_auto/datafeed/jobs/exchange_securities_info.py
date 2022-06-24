



import logging

from grand_trade_auto.datafeed.jobs import datafeed_job
from grand_trade_auto.general import config
from grand_trade_auto.general import utils as gen_utils
from grand_trade_auto.model import model_meta
from grand_trade_auto.model.datafeed_src import DatafeedSrc
from grand_trade_auto.model.exchange import Exchange
from grand_trade_auto.model.security import Security



logger = logging.getLogger(__name__)



class ExchangesSecuritiesInfoJob(datafeed_job.DatafeedJob):
    """
    """

    @classmethod
    def load_data_from_config(cls, df_cp, df_id):
        """
        """
        # Confirm this category as sanity check
        if df_cp.get(df_id, 'data category', fallback=None) \
                not in cls.get_dc_names():
            raise Exception('Programming error: Should not be here')

        data = {}
        data['env'] = df_cp[df_id]['env'].strip()
        data['apic_src'] = df_cp[df_id]['apic src'].strip()
        data['database_dst'] = df_cp[df_id]['database dst'].strip()
        data['dependent_datafeeds'] = config.parse_list_from_conf_string(
                df_cp.get(df_id, 'dependent datafeeds', fallback=None),
                config.CastType.STRING, delim_newlines=True, strip_quotes=True)

        data['data_category'] = cls.get_dc_names()[0]
        data['when_to_run'] = datafeed_job.WhenToRun(
                df_cp[df_id]['when to run'])
        data['include_fk_datafeeds'] = config.parse_list_from_conf_string(
                df_cp.get(df_id, 'include fk_datafeeds', fallback=None),
                config.CastType.STRING, delim_newlines=True, strip_quotes=True)
        data['exclude_fk_datafeeds'] = config.parse_list_from_conf_string(
                df_cp.get(df_id, 'exclude fk datafeeds', fallback=None),
                config.CastType.STRING, delim_newlines=True, strip_quotes=True)

        data['start_datetime'] = config.get_parsed_datetime_from_confg(df_cp,
                df_id, 'start datetime')
        data['end_datetime'] = config.get_parsed_datetime_from_confg(df_cp,
                df_id, 'end datetime')
        if data['end_datetime'] is not None \
                and data['start_datetime'] is None:
            raise Exception('If end datetime defined, must define start'
                    f' datetime in datafeed config section: {df_id}')

        data['run_interval'] = datafeed_job.RunInterval(
                df_cp[df_id]['run interval'])
        data['run_offset'] = config.get_parsed_time_from_config(df_cp, df_id,
                'run offset')
        # TODO: Combine when to run, run interval, run offset into a run config data struct (with better name??)

        for option in ['include exchanges', 'include tickers',
                'exclude exchanges', 'exclude tickers']:
            data[option.replace(' ', '_')] = config.parse_list_from_conf_string(
                    option, config.CastType.STRING, delim_newlines=True,
                    strip_quotes=True)

        return data



    @classmethod
    def get_dc_names(cls):
        """
        The first will be used as storage for official reference and reporting.
        """
        return ['exchanges and securities info']



    def execute(self, df):
        """
        """
        if self.config_data['include_fk_datafeeds'] is not None \
                or self.config_data['exclude_fk_datafeeds'] is not None:
            dfs_allowed, include_dfs_missing = DatafeedSrc.get_by_column(
                    df._db.orm, 'name',
                    self.config_data['include_fk_datafeeds'],
                    include_missing=True)
            dfs_disallowed, exclude_dfs_missing = DatafeedSrc.get_by_column(
                    df._db.orm, 'name',
                    exclude_vals=self.config_data['exclude_fk_datafeeds'],
                    include_missing=True)
            if include_dfs_missing:
                logger.warning('Skipping missing include fk datafeeds for'
                        f" datafeed '{df._id}': "
                        # ", ".join([f"'{d.name}'" for d in include_dfs_missing])
                        + gen_utils.list_to_quoted_element_str(
                            [d.name for d in include_dfs_missing])
                        + ".")
            if include_dfs_missing:
                logger.warning('Skipping missing exclude fk datafeeds for'
                        f" datafeed '{df._id}': "
                        # ", ".join([f"'{d.name}'" for d in exclude_dfs_missing])
                        + gen_utils.list_to_quoted_element_str(
                            [d.name for d in exclude_dfs_missing])
                        + ".")

            where_df_ids = DatafeedSrc.build_where_for_column('id',
                    [d.id for d in dfs_allowed],
                    [d.id for d in dfs_disallowed])
        else:
            where_df_ids = None
        where_this_df = ('id', model_meta.LogicOp.EQ, df.id)

        # TODO: Should have separate job that reviews list/delist
        #       ...and then this would not need to query exchanges from df
        #      Should basically do below, but also review ones in db regardless
        #        to catch delistings

        # If already in db, will have an id set; if not, will be missing
        # TODO: Check if any in include and exclude, raise error (also for tickers)
        exchanges_in_db, exchanges_not_in_db = Exchange.get_by_column(
                df._db.orm, 'acronym', self.config_data['include_exchanges'],
                self.config_data['exclude_exchanges'], where_df_ids, True)
        exchanges_matched, exchanges_missing, exchanges_extra = df.query_exchanges(
                include=exchanges_not_in_db, exclude=exchanges_in_db, include_missing=True,
                include_extras=not bool(self.config_data['include_exchanges']))
        for exchange in exchanges_matched + exchanges_extra:
            exchange.add()
        if exchanges_missing:
            logger.warning("Exchanges not in database could not be found in"
                    f" datafeed.  Datafeed section: '{df._id}'.  Exchanges: "
                    # ", ".join([f"'{e.acronym}'" for e in exchanges_missing])
                    + gen_utils.list_to_quoted_element_str(
                        [e.acronym for e in exchanges_missing])
                    + ".  These have been skipped.")
        # exchanges = [e for e in exchanges if e.id is not None] + new_exchanges
        exchanges = Exchange.get_by_column(df._db.orm, 'acronym',
                self.config_data['include_exchanges'],
                self.config_data['exclude_exchanges'], where_df_ids)

        # If no include/exclude or only exclude, will get all securities from
        #   apic for all possible exchanges, add missing to db
        # If include, will get only those securities from apic for possible
        #   exchanges (or exact exchanges), add missing to db
        # Any not found on apic will be a warning if explicit in config;
        #   but verbose only if missing due to possible exchanges and include tickers
        securities = self.parse_securities(df, exchanges, where_df_ids)
        # TODO: Also need to add company

        self.finish(df) # Remove job from queue, save to db



    def parse_securities(self, df, exchanges_allowed, where_and):
        """
        """
        exchanges_allowed_by_acronym = {e.acronym:e for e in exchanges_allowed}
        include_with_exchange = [t
                for t in self.config_data['include_tickers']
                if ':' in t]
        include_without_exchange = [t
                for t in self.config_data['include_tickers']
                if ':' not in t]
        exclude_with_exchange = [t
                for t in self.config_data['exclude_tickers']
                if ':' in t]
        exclude_without_exchange = [t
                for t in self.config_data['exclude_tickers']
                if ':' not in t]

        include_exact_val_sets = []
        include_exact_missing_exchange = []
        for t in include_with_exchange:
            e_acronym, t_name = [x.strip() for x in t.split(':')]
            try:
                e_id = exchanges_allowed_by_acronym[e_acronym]
            except KeyError:
                include_exact_missing_exchange.append(t)
                continue

            val_set = (e_id, t_name)
            include_exact_val_sets.append(val_set)
        exclude_exact_val_sets = []
        exclude_exact_missing_exchange = []
        for t in exclude_with_exchange:
            e_acronym, t_name = [x.strip() for x in t.split(':')]
            try:
                e_id = exchanges_allowed_by_acronym[e_acronym]
            except KeyError:
                exclude_exact_missing_exchange.append(t)
                continue

            val_set = (e_id, t_name)
            exclude_exact_val_sets.append(val_set)

        exact_in_db, exact_not_in_db = \
                Security.get_by_columns(df._db.orm, ('exchange_id', 'ticker'),
                    include_exact_val_sets, exclude_exact_val_sets, where_and,
                    True)

        where_exchanges = Exchange.build_where_for_column('id',
                exchanges_allowed_by_acronym.values())
        where_combined = Exchange.combine_wheres([where_and, where_exchanges],
                model_meta.LogicCombo.AND)

        vague_in_db = Security.get_by_column(df._db.orm, 'ticker',
                include_without_exchange, exclude_without_exchange,
                where_combined)
        vague_in_db = [v for v in vague_in_db
                if v.id not in [e.id for e in exact_in_db]]
        vague_not_in_db = []
        for e_id in [e.id for e in exchanges_allowed_by_acronym.values()]:
            for t_name in include_without_exchange:
                if (e_id, t_name) not in [(s.exchange_id, s.ticker)
                        for s in vague_in_db + exact_in_db]:
                    vague_not_in_db.append(Security(df._db.orm,
                            {'exchange_id': e_id, 'ticker': t_name}))

        securities_in_db = exact_in_db + vague_in_db
        securities_not_in_db = exact_not_in_db + vague_not_in_db

        securities_matched, securities_missing, securities_extra = \
                df.query_securities(include=securities_not_in_db,
                exclude=securities_in_db, include_missing=True,
                include_extras=not bool(self.config_data['include_tickers']),
                exchanges_allowed_by_acronym=exchanges_allowed_by_acronym)

        securities_missing_exact = [s for s in securities_missing
                if s in exact_not_in_db]
        securities_missing_vague = [s for s in securities_missing
                if s in vague_not_in_db]

        for security in securities_matched + securities_extra:
            security.add()
        if securities_missing_exact:
            e_by_id = {e.id: e for e in exchanges_allowed_by_acronym.values()}
            error_list = [e_by_id[s.exchange_id].acronym + ':' + s.ticker
                    for s in securities_missing_exact]
            logger.warning("Fully qualified tickers not in database could not"
                    f" be found in datafeed.  Datafeed section: '{df._id}'."
                    + "  Tickers: "
                    + gen_utils.list_to_quoted_element_str(error_list)
                    + ".  These have been skipped.")
        if securities_missing_vague:
            ticker_names = []
            for s in securities_missing_vague:
                if s.ticker not in ticker_names:
                    ticker_names.append(s.ticker)
            fully_missing = [t for t in ticker_names
                    if t not in [s.ticker
                        for s in securities_matched + securities_extra]]
            partial_missing = [t for t in ticker_names
                    if t not in fully_missing]
            logger.debug("Name-only tickers not in database could not be"
                    " found in datafeed for some exchanges.  Datafeed section:"
                    f" '{df._id}'.  Tickers completely missing: "
                    + gen_utils.list_to_quoted_element_str(fully_missing)
                    + ".  Tickers partially missing: "
                    + gen_utils.list_to_quoted_element_str(partial_missing)
                    + ".  For partial missing, these succeeded at least 1"
                    " possible exchange, but have been skipped for other"
                    " exchanges.  To mute this message, include tickers with"
                    " fully qualified using exchange:ticker, such as"
                    " 'NASDAQ:AAPL'.")

        exact_in_db = \
                Security.get_by_columns(df._db.orm, ('exchange_id', 'ticker'),
                    include_exact_val_sets, exclude_exact_val_sets, where_and)
        vague_in_db = Security.get_by_column(df._db.orm, 'ticker',
                include_without_exchange, exclude_without_exchange,
                where_combined)

        return exact_in_db + vague_in_db



datafeed_job.register_datafeed_job_cls(ExchangesSecuritiesInfoJob)
