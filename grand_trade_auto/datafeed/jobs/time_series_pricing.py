


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

        data['should_save_raw'] = df_cp.getboolean(df_id, 'save raw prices',
                fallback=True)
        data['should_save_adjusted'] = df_cp.getboolean(df_id,
                'save adjusted prices', fallback=True)
        data['data_interval'] = model_meta.PriceFrequency(
                df_cp[df_id]['data interval'])

        cls._load_from_config_exchanges_tickers(df_cp, df_id, data, True)
        return data




    @classmethod
    def get_dc_names(cls):
        """
        The first will be used as storage for official reference and reporting.
        """
        return ['time series pricing']



    # TODO: Refactor, especially with ExchangesSecuritiesInfoJob
    def execute(self, df):
        """
        """
        where_df_ids = self._build_where_for_df_ids(df,
                self.config_data['include_fk_datafeeds'],
                self.config_data['exclude_fk_datafeeds'])
        where_this_df = ('id', model_meta.LogicOp.EQ, df.id)

        # TODO: Check if any in include and exclude, raise error (also for tickers)
        exchanges, exchanges_missing, _ = Exchange.get_by_column(df.db.orm, 'acronym',
                self.config_data['include_exchanges'],
                self.config_data['exclude_exchanges'], where_df_ids, include_missing=True)
        if exchanges_missing:
            logger.warning("Exchanges not in database could not be found in"
                    f" datafeed.  Datafeed section: '{df.df_id}'.  Exchanges: "
                    # ", ".join([f"'{e.acronym}'" for e in exchanges_missing])
                    + gen_utils.list_to_quoted_element_str(
                        [e.acronym for e in exchanges_missing])
                    + ".  These have been skipped.")

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
                        self.config_data['data_interval'],
                        exchanges=exchanges,
                        allow_chunking=True,
                        resume_data=self.resume_data['datafeed_resume_data'])
                for price_entry in price_data:
                    # TODO: Catch if db add fails due to unique key, log warning
                    #     With this, will make start/end inclusive (user should pick different run time)
                    SecurityPrice.add_direct(df.db.orm, price_entry,
                            commit=False)
                # Do want the following db op to commit
                DatafeedSrc.update_direct(df.db.orm,
                        {'resume_data': self.resume_data}, where=where_this_df)
                if self.resume_data['datafeed_resume_data'] is None:
                    security_finished = True
                    # Leave resume data as None for start of next security

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

        where_exchanges = Exchange.build_where_for_column('id',
                exchanges_allowed_by_acronym.values())
        where_combined = Exchange.combine_wheres([where_and, where_exchanges],
                model_meta.LogicCombo.AND)

        exact_in_db = \
                Security.get_by_columns(df.db.orm, ('exchange_id', 'ticker'),
                    include_exact_val_sets, exclude_exact_val_sets, where_and)
        vague_in_db = Security.get_by_column(df.db.orm, 'ticker',
                include_without_exchange, exclude_without_exchange,
                where_combined)

        # TODO: Re-add error warnings for missing

        return exact_in_db + vague_in_db




datafeed_job.register_datafeed_job_cls(TimeSeriesPricingJob)
