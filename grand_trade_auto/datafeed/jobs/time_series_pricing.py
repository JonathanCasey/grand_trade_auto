


import logging

from grand_trade_auto.datafeed.jobs import datafeed_job
from grand_trade_auto.general import config
from grand_trade_auto.general import utils as gen_utils
from grand_trade_auto.model import model_meta
from grand_trade_auto.model.datafeed_src import DatafeedSrc
from grand_trade_auto.model.exchange import Exchange
from grand_trade_auto.model.security import Security
from grand_trade_auto.model.security_price import SecurityPrice





logger = logging.getLogger(__name__)





class TimeSeriesPricingJob(datafeed_job.DatafeedJob):

    # primary_model:model_meta.Model # TODO: Should this be plural?

    # TODO: Model should define these dependencies
    # model_and_dependencies = {
    #     SecurityPrice : {
    #         Security : {
    #         },
    #         DatafeedSrc : {}, # Or None?
    #     }
    # }

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

        data['data_category'] = cls.get_dc_names()[0]
        data['when_to_run'] = datafeed_job.WhenToRun(
                df_cp[df_id]['when to run'])
        data['include_fk_datafeeds'] = config.parse_list_from_conf_string(
                df_cp.get(df_id, 'include_fk_datafeeds', fallback=None),
                config.CastType.STRING, delim_newlines=True, strip_quotes=True)
        data['exclude_fk_datafeeds'] = config.parse_list_from_conf_string(
                df_cp.get(df_id, 'exclude_fk_datafeeds', fallback=None),
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

        data['should_save_raw'] = df_cp.getboolean(df_id, 'save raw prices',
                fallback=True)
        data['should_save_adjusted'] = df_cp.getboolean(df_id,
                'save adjusted prices', fallback=True)
        data['data_interval'] = model_meta.PriceFrequency(
                df_cp[df_id]['data interval'])

        for option in ['include exchanges', 'include tickers',
                'exclude exchanges', 'exclude tickers']:
            data[option.replace(' ', '_')] = config.parse_list_from_conf_string(
                    option, config.CastType.STRING, delim_newlines=True,
                    strip_quotes=True)

        return data



    # def load_datafeed_src(self, apic_src, database_dst, env):
    #     """
    #     """





    # @classmethod
    # def load_from_config_into_job(cls, df_cp, df_id):
    #     """
    #     Loads config into a standardized job format.
    #     """
    #     if df_cp.get(df_id, 'data category', fallback=None) \
    #             not in cls.get_dc_names():
    #         raise Exception('Programming error: Should not be here')

    #     data = {}
    #     data['env'] = df_cp[df_id]['env'].strip()
    #     data['apic_src'] = df_cp[df_id]['apic src'].strip()
    #     data['database_dst'] = df_cp[df_id]['database dst'].strip()

    #     data['data_category'] = cls.get_dc_names()[0]
    #     data['when_to_run'] = WhenToRun(df_cp[df_id]['when to run'])
    #     # data['pk_this_df_only'] = df_cp.getboolean(df_id,
    #     #         'pk this datafeed only', fallback=True)
    #     # data['fk_this_df_only'] = df_cp.getboolean(df_id,
    #     #         'fk this datafeed only', fallback=False)

    #     data['start_datetime'] = get_parsed_datetime_from_confg(df_cp, df_id,
    #             'start datetime')
    #     data['end_datetime'] = get_parsed_datetime_from_confg(df_cp, df_id,
    #             'end datetime')
    #     if data['end_datetime'] is not None \
    #             and data['start_datetime'] is None:
    #         raise Exception('If end datetime defined, must define start'
    #                 f' datetime in datafeed config section: {df_id}')

    #     data['run_interval'] = RunInterval(df_cp[df_id]['run interval'])
    #     data['run_offset'] = get_parsed_time_from_config(df_cp, df_id,
    #             'run offset')
    #     # TODO: Combine when to run, run interval, run offset into a run config data struct (with better name??)

    #     data['should_save_raw'] = df_cp.getboolean(df_id, 'save raw prices',
    #             fallback=True)
    #     data['should_save_adjusted'] = df_cp.getboolean(df_id,
    #             'save adjusted prices', fallback=True)
    #     data['data_interval'] = model_meta.PriceFrequency(
    #             df_cp[df_id]['data interval'])

    #     for option in ['include exchanges', 'include tickers',
    #             'exclude exchanges', 'exclude tickers']:
    #         data[option.replace(' ', '_')] = config.parse_list_from_conf_string(
    #                 option, config.CastType.STRING, delim_newlines=True,
    #                 strip_quotes=True)

    #     # TODO: Pass to job
    #     # TODO: When job loaded, can figure out class to use based on data category


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

        for security in securities:
            if self.resume_data['last_security_id'] is not None \
                    and security.id \
                        < self.resume_data['last_security_id']:
                continue
            # Starting next security -- update id, reset resume_data
            # Otherwise, let resume_data stay as it is
            # Not worth saving this to db yet -- would recover gracefully
            if security.id != self.resume_data['last_security_id']:
                self.resume_data['last_security_id'] = security.id
                self.resume_data['datafeed_resume_data'] = None

            security_finished = False
            while not security_finished:
                # Passing None for resume_data means start from beginning
                # Getting None returned for resume_data means done
                # Otherwise, do not care what resume_data is -- that's for df

                # TODO: For this, want to add direct -- add flag as arg to
                #        query_security_prices()
                price_data, self.resume_data['datafeed_resume_data'] = \
                        df.query_security_prices(security,
                        self.config_data['start_datetime,'],
                        self.config_data['end_datetime'],
                        exchanges=exchanges,
                        allow_chunking=True,
                        resume_data=self.resume_data['datafeed_resume_data'])
                for price_entry in price_data:
                    # TODO: Catch if db add fails due to unique key, log warning
                    #     With this, will make start/end inclusive (user should pick different run time)
                    SecurityPrice.add_direct(df._db.orm, price_entry,
                            commit=False)
                # Do want the following db op to commit
                DatafeedSrc.update_direct(df._db.orm,
                        {'resume_data': self.resume_data}, where=where_this_df)
                if self.resume_data['datafeed_resume_data'] is None:
                    security_finished = True
                    # Leave resume data as None for start of next security

        self.finish() # Remove job from queue, save to db




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



















        # tickers = build_tickers(job.exchanges, job.tickers)








    @classmethod
    def get_dc_names(cls):
        """
        The first will be used as storage for official reference and reporting.
        """
        ['time series pricing']


    # def do_something(self, db, df):
    #     add_exchange(existing_data)
    #     or_exchange_conds = [('acronym', model_meta.LogicOp.EQ, e)
    #             for e in self.exchanges]
    #     where = {
    #         model_meta.LogicCombo.OR: or_exchange_conds,
    #     }
    #     if self.fk_this_datafeed_only:
    #         where = {
    #             model_meta.LogicCombo.AND: [
    #                 where,
    #                 ('datafeed_src', model_meta.LogicOp.EQ, df.id),
    #             ],
    #         }
    #     exchange_db_data = exchange_mod.Exchange.query_direct(db.orm,
    #             model_meta.ReturnAs.DICT, ['id', 'acronym'], where)
    #     exchange_acronyms_to_ids = {}
    #     for e in exchange_db_data:
    #         exchange_acronyms_to_ids[e['acronym']] = e['id']


    #     exchanges_to_add = []
    #     for e in self.exchanges:
    #         if e not in exchange_acronyms_to_ids:
    #             exchanges_to_add.append(e)

    #     for e in exchanges_to_add:
    #         data = {
    #             'acronym': e,
    #             'datafeed_src_id': df.id,
    #         }
    #         exchange.Exchange.add_direct(db.orm, data)

    #     or_exchange_conds = [('acronym', model_meta.LogicOp.EQ, e)
    #             for e in exchanges_to_add]
    #     where = {
    #         model_meta.LogicCombo.OR: or_exchange_conds,
    #     }
    #     if self.fk_this_datafeed_only:
    #         where = {
    #             model_meta.LogicCombo.AND: [
    #                 where,
    #                 ('datafeed_src', model_meta.LogicOp.EQ, df.id),
    #             ],
    #         }
    #     exchange_db_data = exchange_mod.Exchange.query_direct(db.orm,
    #             model_meta.ReturnAs.DICT, ['id', 'acronym'], where)
    #     for e in exchange_db_data:
    #         exchange_acronyms_to_ids[e['acronym']] = e['id']

    #     return exchange_acronyms_to_ids




    # def add_security_prices(ticker_names, exchange_names=None):
    #     if pk_this_datafeed_only:
    #         pk_df_ids = [df.id]
    #     else:
    #         pk_df_ids = None
    #     if fk_this_datafeed_only:
    #         fk_df_ids = [df.id]
    #     else:
    #         fk_df_ids = None
    #     if ticker_names is None:
    #         ticker_names = get_all_ticker_names(exchange_names,
    #                 exchange_qualified=True, datafeed_src_ids=fk_df_ids)
    #         if ticker_names is None:
    #             init_tickers(exchange_names, df.id)
    #             ticker_names = get_all_ticker_names(exchange_names,
    #                     exchange_qualified=True, datafeed_src_ids=fk_df_ids)
    #     for ticker in ticker_names:
    #         if ':' in ticker:
    #             exchange_name, ticker_name = ticker.split(':')
    #             security = get_security(ticker_name, exchange_name, fk_df_ids)
    #             securities = [security]
    #         else:
    #             securities = get_securities(ticker, fk_df_ids,
    #                     possible_exchanges=exchange_names)
    #         for security in securities:
    #             exchange = get_exchange(security.exchange_id, fk_df_ids)
    #             all_dates_retrieved = False
    #             while not all_dates_retrieved:
    #                 data_to_add, progress_marker = df.query_security_price(
    #                         security, exchange, progress_marker, allow_chunking=True)
    #                 for data in data_to_add:
    #                     security_price_mod.SecurityPrice.add_direct(orm, data)
    #                 df_data = {'progress_marker': progress_marker}
    #                 where_this_df = ('id', model_meta.LogicOp.EQ, df.id)
    #                 datafeed_src_mod.DatafeedSrc.update_direct(orm, df_data, where_this_df)
    #                 if progress_marker is None:
    #                     all_dates_retrieved = True


        # Should basically read config, create "jobs in progress" for it if it
        #   doesn't already exist
        # Tasks are essentially then generated out of jobs_in_progress
        # Will only support db init and periodic to start (must be both?)
        # Even though not init, will queue db init and periodic at same time
        #   (but maybe will just queue up periodic jobs until init done)
        # Changing anything in config ERASES job in progress!
        # jobs_in_progress = [
        #     {
        #         'config': {
        #             # TODO: This should be codified from DataCategory
        #             'data category': time_series_pricing,
        #             'start_datetime': start_datetime,
        #             'end_datetime': end_datetime,
        #             'data_interval': data_interval,
        #             'tickers': ticker, # From config file
        #             'exchanges': exchanges, # From config file
        #         },
        #         'last_executed': {
        #             'ticker': ticker,
        #             'datetime': last_datetime,
        #         },
        #         # If called next day, cycle through first tickers and catch up
        #     },
        # ]






    # def init_bookmark(config_as_called, config_as_executed, existing_bookmarks):
    #     existing_bookmark = None
    #     for b in existing_bookmarks:
    #         if b['config_as_called'] == config_as_called:
    #             existing_bookmark = b
    #             break

    #     if existing_bookmark is None:
    #         new_bookmark = {
    #             'config_as_called': config_as_called,
    #             'config_as_executed': config_as_executed,
    #             'df_last_executed': None,
    #         }
    #         existing_bookmarks.append(new_bookmark)
    #         return

    #     if existing_bookmark['config_as_executed'] == config_as_executed:
    #         return











    # def get_securities():
    #     """
    #     """




    # def add_security_price(security_id=None):
    #     if not security_id:
    #         security = get_security()
    #         if not security:
    #             security = add_security()
    #         security_id = security.id




    # def add_security():
    #     if not exchange_id:
    #         add_exchange()




    # def build_job(self):
    #     """
    #     """
    #     entry = {
    #         'config': {
    #             # TODO: This should be codified from DataCategory
    #             'data category': time_series_pricing,
    #             'start_datetime': start_datetime,
    #             'end_datetime': end_datetime,
    #             'data_interval': data_interval,
    #             'tickers': ticker, # From config file
    #             'exchanges': exchanges, # From config file
    #         },
    #         'last_executed': {
    #             'ticker': ticker,
    #             'datetime': last_datetime,
    #         },
    #     }





datafeed_job.register_datafeed_job_cls(TimeSeriesPricingJob)
