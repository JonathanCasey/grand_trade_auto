



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
        cls._load_from_config_id(df_cp, df_id, data, True)
        cls._load_from_config_data_category(df_cp, df_id, data)
        cls._load_from_config_run_options(df_cp, df_id, data, True)
        # TODO: Fill in default start/end datetime somewhere?  In resume data?
        cls._load_from_config_exchanges_tickers(df_cp, df_id, data, True)
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
        where_df_ids = self._build_where_for_df_ids(df,
                self.config_data['include_fk_datafeeds'],
                self.config_data['exclude_fk_datafeeds'])
        where_this_df = ('id', model_meta.LogicOp.EQ, df.id)

        # TODO: Should have separate job that reviews list/delist
        #       ...and then this would not need to query exchanges from df
        #      Should basically do below, but also review ones in db regardless
        #        to catch delistings
        exchanges = self._execute_exchanges_task(df, where_df_ids)

        self._execute_securities_task(df, exchanges, where_df_ids)
        # TODO: Also need to add company

        self.finish(df) # Remove job from queue, save to db



    def _execute_exchanges_task(self, df, where_df_ids):
        """
        """
        exchanges_in_db, exchanges_not_in_db = Exchange.get_by_column(
                df.db.orm, 'acronym', self.config_data['include_exchanges'],
                self.config_data['exclude_exchanges'], where_df_ids, True)
        exchanges_matched, exchanges_missing, exchanges_extra = \
                df.query_exchanges(include=exchanges_not_in_db,
                exclude=exchanges_in_db, include_missing=True,
                include_extras=not bool(self.config_data['include_exchanges']))
        # If already in db, will have an id set; if not, will be missing
        for exchange in exchanges_matched + exchanges_extra:
            exchange.add()
        if exchanges_missing:
            logger.warning("Exchanges not in database could not be found in"
                    f" datafeed.  Datafeed section: '{df.df_id}'.  Exchanges: "
                    + gen_utils.list_to_quoted_element_str(
                        [e.acronym for e in exchanges_missing])
                    + ".  These have been skipped.")
        exchanges = Exchange.get_by_column(df.db.orm, 'acronym',
                self.config_data['include_exchanges'],
                self.config_data['exclude_exchanges'], where_df_ids)

        return exchanges



    def _parse_config_tickers(self):
        """
        """
        tickers = {
            'include': {},
            'exclude': {},
        }
        tickers['include']['exact'] = [t
                for t in self.config_data['include_tickers']
                if ':' in t]
        tickers['include']['vague'] = [t
                for t in self.config_data['include_tickers']
                if ':' not in t]
        tickers['exclude']['exact'] = [t
                for t in self.config_data['exclude_tickers']
                if ':' in t]
        tickers['exclude']['vague'] = [t
                for t in self.config_data['exclude_tickers']
                if ':' not in t]

        return tickers



    @staticmethod
    def _build_ticker_exact_value_sets(tickers_exact, exchanges_by_acronym,
            log_missing=False, include_missing=False):
        val_sets = []
        missing_exchange = []
        for t in tickers_exact:
            e_acronym, t_name = [x.strip() for x in t.split(':')]
            try:
                e_id = exchanges_by_acronym[e_acronym]
            except KeyError:
                if include_missing:
                    missing_exchange.append(t)
                if log_missing:
                    logger.info('Skipping fully qualified ticker due to'
                            f' unallowed exchange: {t}')
                continue

            val_set = (e_id, t_name)
            val_sets.append(val_set)

        if include_missing:
            return val_sets, missing_exchange
        return val_sets



    @classmethod
    def _build_all_ticker_exact_value_sets(cls, config_tickers,
            exchanges_allowed_by_acronym):
        """
        """
        exact_val_sets = {}
        exact_val_sets['include'] = cls._build_ticker_exact_value_sets(
                config_tickers['include']['exact'],
                exchanges_allowed_by_acronym)
        exact_val_sets['exclude'] = cls._build_ticker_exact_value_sets(
                config_tickers['exclude']['exact'],
                exchanges_allowed_by_acronym)
        return exact_val_sets


    @staticmethod
    def _get_vague_securities_in_db(df, include_vague=None, exclude_vague=None,
            where=None, exact_in_db=None, exchanges_allowed=None):
        """
        """
        vague_in_db = Security.get_by_column(df.db.orm, 'ticker',
                include_vague, exclude_vague, where)
        if exact_in_db is not None:
            vague_in_db = [vague for vague in vague_in_db
                    if vague.id not in [exact.id for exact in exact_in_db]]

        if exchanges_allowed is not None:
            vague_not_in_db = []
            for e_id in [e.id for e in exchanges_allowed]:
                for t_name in include_vague:
                    if (e_id, t_name) not in [(s.exchange_id, s.ticker)
                            for s in vague_in_db + exact_in_db]:
                        vague_not_in_db.append(Security(df.db.orm,
                                {'exchange_id': e_id, 'ticker': t_name}))
            return vague_in_db, vague_not_in_db
        return vague_in_db



    @staticmethod
    def _add_and_review_queried_securities(df, securities_new_expected,
            securities_new_extra=None, securities_missing_exact=None,
            securities_missing_vague=None, exchanges_allowed=None):
        """
        """
        securities_to_add = securities_new_expected
        if securities_new_extra is not None:
            securities_to_add += securities_new_extra
        for security in securities_to_add:
            security.add()

        if securities_missing_exact:
            e_by_id = {e.id: e for e in exchanges_allowed}
            error_list = [e_by_id[s.exchange_id].acronym + ':' + s.ticker
                    for s in securities_missing_exact]
            logger.warning("Fully qualified tickers not in database could not"
                    f" be found in datafeed.  Datafeed section: '{df.df_id}'."
                    + "  Tickers: "
                    + gen_utils.list_to_quoted_element_str(error_list)
                    + ".  These have been skipped.")
        if securities_missing_vague:
            ticker_names = []
            for s in securities_missing_vague:
                if s.ticker not in ticker_names:
                    ticker_names.append(s.ticker)
            fully_missing = [t for t in ticker_names
                    if t not in [s.ticker for s in securities_to_add]]
            partial_missing = [t for t in ticker_names
                    if t not in fully_missing]
            logger.debug("Name-only tickers not in database could not be"
                    " found in datafeed for some exchanges.  Datafeed section:"
                    f" '{df.df_id}'.  Tickers completely missing: "
                    + gen_utils.list_to_quoted_element_str(fully_missing)
                    + ".  Tickers partially missing: "
                    + gen_utils.list_to_quoted_element_str(partial_missing)
                    + ".  For partial missing, these succeeded at least 1"
                    " possible exchange, but have been skipped for other"
                    " exchanges.  To mute this message, include tickers with"
                    " fully qualified using exchange:ticker, such as"
                    " 'NASDAQ:AAPL'.")



    @classmethod
    def _query_and_process_securities_based_on_db(cls, df, exact_in_db,
            exact_not_in_db, vague_in_db, vague_not_in_db,
            exchanges_allowed_by_acronym, did_config_any_include_tickers):
        """
        """
        securities_in_db = exact_in_db + vague_in_db
        securities_not_in_db = exact_not_in_db + vague_not_in_db

        securities_matched, securities_missing, securities_extra = \
                df.query_securities(include=securities_not_in_db,
                exclude=securities_in_db, include_missing=True,
                include_extras=did_config_any_include_tickers,
                exchanges_allowed_by_acronym=exchanges_allowed_by_acronym)

        securities_missing_exact = [s for s in securities_missing
                if s in exact_not_in_db]
        securities_missing_vague = [s for s in securities_missing
                if s in vague_not_in_db]

        cls._add_and_review_queried_securities(df, securities_matched,
                securities_extra, securities_missing_exact,
                securities_missing_vague, exchanges_allowed_by_acronym.values())



    def _execute_securities_task(self, df, exchanges_allowed, where_and):
        """
        """
        # If no include/exclude or only exclude, will get all securities from
        #   apic for all possible exchanges, add missing to db
        # If include, will get only those securities from apic for possible
        #   exchanges (or exact exchanges), add missing to db
        # Any not found on apic will be a warning if explicit in config;
        #   but verbose only if missing due to possible exchanges and include tickers
        exchanges_allowed_by_acronym = {e.acronym:e for e in exchanges_allowed}
        where_exchanges = Exchange.build_where_for_column('id',
                exchanges_allowed)
        where_combined = Exchange.combine_wheres([where_and, where_exchanges],
                model_meta.LogicCombo.AND)

        config_tickers = self._parse_config_tickers()
        exact_val_sets = self._build_all_ticker_exact_value_sets(config_tickers,
                exchanges_allowed_by_acronym)

        exact_in_db, exact_not_in_db = Security.get_by_columns(df.db.orm,
                ('exchange_id', 'ticker'), exact_val_sets['include'],
                exact_val_sets['exclude'], where_and, True)
        vague_in_db, vague_not_in_db = self._get_vague_securities_in_db(df,
                config_tickers['include']['vague'],
                config_tickers['exclude']['vague'], where_combined, exact_in_db,
                exchanges_allowed)

        self._query_and_process_securities_based_on_db(df, exact_in_db,
                exact_not_in_db, vague_in_db, vague_not_in_db,
                exchanges_allowed_by_acronym,
                not bool(self.config_data['include_tickers']))

        # Must re-query so get data with id's for db
        exact_in_db = Security.get_by_columns(df.db.orm,
                ('exchange_id', 'ticker'), exact_val_sets['include'],
                exact_val_sets['exclude'], where_and, False)
        vague_in_db = self._get_vague_securities_in_db(df,
                config_tickers['include']['vague'],
                config_tickers['exclude']['vague'], where_combined)

        return exact_in_db + vague_in_db



datafeed_job.register_datafeed_job_cls(ExchangesSecuritiesInfoJob)
