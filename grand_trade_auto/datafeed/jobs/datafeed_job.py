


from abc import ABC, abstractmethod, abstractclassmethod
from enum import Enum
import logging
import pickle

from grand_trade_auto.general import config
from grand_trade_auto.general import utils as gen_utils
from grand_trade_auto.model.datafeed_src import DatafeedSrc



logger = logging.getLogger(__name__)



_DATAFEED_JOBS = set()

def register_datafeed_job_cls(job_cls):
    _DATAFEED_JOBS.add(job_cls)




class RunType(Enum):
    """
    """
    ONE_SHOT = 'one shot'
    PERIODIC = 'periodic'



class RunInterval(Enum):
    """
    """
    DAILY = 'daily'




class DatafeedJob(ABC):


    def __init__(self, config_data, is_for_init=False,
            resume_data=None):
        """
        """
        self.config_data = config_data
        self.is_for_init = is_for_init
        self.resume_data = resume_data
        self._init_nonserial()



    def _init_nonserial(self):
        """
        """
        # For now, nothing to do



    def _clear_nonserial(self):
        """
        """
        # For now, nothing to do



    @classmethod
    def load_data_from_config_by_category(cls, df_cp, df_id):
        data_cat_name = df_cp.get(df_id, 'data category', fallback=None)
        df_job_cls = cls.get_class_from_name(data_cat_name)
        if df_job_cls is None:
            raise Exception('Invalid category in datafeed config:'
                    f'{data_cat_name}')
        return df_job_cls.load_data_from_config(df_cp, df_id)



    @classmethod
    def _load_from_config_id(cls, df_cp, df_id, data=None,
            should_validate=False):
        """
        """
        if data is None:
            data = {}
        data['env'] = df_cp[df_id]['env'].strip()
        data['apic_src'] = df_cp[df_id]['apic src'].strip()
        data['database_dst'] = df_cp[df_id]['database dst'].strip()
        data['dependent_datafeeds'] = config.parse_list_from_conf_string(
                df_cp.get(df_id, 'dependent datafeeds', fallback=None),
                config.CastType.STRING, delim_newlines=True, strip_quotes=True)

        data['include_fk_datafeeds'] = config.parse_list_from_conf_string(
                df_cp.get(df_id, 'include fk_datafeeds', fallback=None),
                config.CastType.STRING, delim_newlines=True, strip_quotes=True)
        data['exclude_fk_datafeeds'] = config.parse_list_from_conf_string(
                df_cp.get(df_id, 'exclude fk datafeeds', fallback=None),
                config.CastType.STRING, delim_newlines=True, strip_quotes=True)

        if should_validate:
            cls._validate_config_data_id(data, df_cp, df_id)

        return data



    @staticmethod
    def _validate_config_data_id(data, df_cp, df_id):
        """
        """
        if df_id in data['exclude_fk_datafeeds']:
            raise Exception('Cannot include own datafeed in foreign key'
                    ' exclusion list.')

        missing_dfs = set(data['dependent_datafeeds']).difference(
                df_cp.sections())
        if missing_dfs:
            raise Exception('Invalid dependent datafeeds that do not match'
                    ' another datafeed section:'
                    + gen_utils.list_to_quoted_element_str(
                        sorted(list(missing_dfs))))

        fk_datafeeds = set(data['include_fk_datafeeds']
                + data['exclude_fk_datafeeds'])
        missing_dfs = fk_datafeeds.difference(df_cp.sections())
        if missing_dfs:
            raise Exception('Invalid include/exclude fk datafeeds that do'
                    ' not match another datafeed section:'
                    + gen_utils.list_to_quoted_element_str(
                        sorted(list(missing_dfs))))

        overlap_dfs = set(data['include_fk_datafeeds']).intersection(
                data['exclude_fk_datafeeds'])
        if overlap_dfs:
            raise Exception('Cannot have foreign key datafeeds included'
                    ' and excluded: '
                    + gen_utils.list_to_quoted_element_str(
                        sorted(list(overlap_dfs))))

        # If no exceptions, nothing to return!


    @classmethod
    def _load_from_config_data_category(cls, df_cp, df_id, data=None):
        """
        """
        if data is None:
            data = {}
        if df_cp or df_id:
            logger.debug('Unused args ignored in'
                    ' `_load_from_config_data_category()`')
        data['data_category'] = cls.get_dc_names()[0]
        return data


    @classmethod
    def _load_from_config_run_options(cls, df_cp, df_id, data=None,
            should_validate=False):
        """
        """
        data['run_type'] = RunType(df_cp[df_id]['when to run'])

        if data['run_type'] in [RunType.PERIODIC, RunType.ONE_SHOT]:
            cls._load_from_config_datetimes_for_init(df_cp, df_id, data,
                    should_validate)

        if data['run_type'] is RunType.PERIODIC:
            data['run_interval'] = RunInterval(df_cp[df_id]['run interval'])
            data['run_offset'] = config.get_parsed_time_from_config(df_cp,
                    df_id, 'run offset')
            # TODO: Factor in time zone...


    @classmethod
    def _load_from_config_datetimes_for_init(cls, df_cp, df_id, data=None,
            should_validate=False):
        """
        """
        if data is None:
            data = {}
        data['start_datetime'] = config.get_parsed_datetime_from_confg(df_cp,
                df_id, 'start datetime')
        data['end_datetime'] = config.get_parsed_datetime_from_confg(df_cp,
                df_id, 'end datetime')
        if should_validate:
            if data['end_datetime'] is not None \
                    and data['start_datetime'] is None:
                raise Exception('If end datetime defined, must define start'
                        f' datetime in datafeed config section: {df_id}')
        return data



    @classmethod
    def _load_from_config_exchanges_tickers(cls, df_cp, df_id, data=None,
            should_validate=False):
        """
        """
        if data is None:
            data = {}
        for option in [
                    'include exchanges',
                    'include tickers',
                    'exclude exchanges',
                    'exclude tickers'
                ]:
            data[option.replace(' ', '_')] = config.parse_list_from_conf_string(
                    df_cp.get(df_id, option, fallback=None),
                    config.CastType.STRING, delim_newlines=True,
                    strip_quotes=True)
        if should_validate:
            cls._validate_obvious_exchange_ticker_conflicts(data)
        return data



    @staticmethod
    def get_class_from_name(name):
        """
        """
        for df_job_cls in _DATAFEED_JOBS:
            if name.lower() in df_job_cls.get_dc_names():
                return df_job_cls
        return None



    @classmethod
    @abstractclassmethod
    def load_data_from_config(cls, df_cp, df_id):
        """
        """


    @classmethod
    @abstractclassmethod
    def get_dc_names(cls):
        """
        """


    @classmethod
    def execute_jobs(cls, jobs, df):
        """
        It is assumed that jobs provided are in the order they were queued, but
        if the caller does not care, neither does this function.
        """
        init_first_jobs = sorted(jobs, key=lambda job: not job.is_for_init)
        for job in init_first_jobs:
            job.execute(df)



    @staticmethod
    def execute_job(job, df):
        """
        """
        job.execute(df)



    @abstractmethod
    def execute(self, df):
        """
        """



    def finish(self, df):
        """
        """
        df.handle_finished_job(self)



    @staticmethod
    def convert_jobs_to_db(jobs):
        """
        """
        for job in jobs:
            job._clear_nonserial()            # pylint: disable=protected-access
        job_db_data = pickle.dumps(jobs, config.PICKLE_PROTOCOL)
        for job in jobs:
            job._init_nonserial()             # pylint: disable=protected-access
        return job_db_data



    @staticmethod
    def convert_db_to_jobs(jobs_db_data):
        """
        """
        jobs = pickle.loads(jobs_db_data, config.PICKLE_PROTOCOL)
        for job in jobs:
            job._init_nonserial()             # pylint: disable=protected-access
        return jobs



    @staticmethod
    def _validate_obvious_exchange_ticker_conflicts(data):
        """
        """
        inc_exchanges = set(data['include_exchanges'])
        exc_exchanges = set(data['exclude_exchanges'])
        inc_tickers_exact = {t for t in data['include_tickers'] if ':' in t}
        inc_tickers_vague = {t for t in data['include_tickers'] if ':' not in t}
        exc_tickers_exact = {t for t in data['exclude_tickers'] if ':' in t}
        exc_tickers_vague = {t for t in data['exclude_tickers'] if ':' not in t}
        inc_exchanges_from_exact = {x.split(':')[0] for x in inc_tickers_exact}
        inc_tickers_from_exact = {x.split(':')[1] for x in inc_tickers_exact}
        #exc_exchanges_from_exact = {x.split(':')[0] for x in exc_tickers_exact}
        exc_tickers_from_exact = {x.split(':')[1] for x in exc_tickers_exact}

        invalid_overlap_exchange_sets = {
            inc_exchanges.intersection(exc_exchanges),
            exc_exchanges.intersection(inc_exchanges_from_exact),
        }
        invalid_overlap_ticker_sets = {
            inc_tickers_exact.intersection(exc_tickers_exact),
            inc_tickers_from_exact.intersection(exc_tickers_vague),
            exc_tickers_from_exact.intersection(inc_tickers_vague),
        }

        for invalid_exchanges in invalid_overlap_exchange_sets:
            raise Exception('Cannot have exchange included and excluded: '
                    + gen_utils.list_to_quoted_element_str(
                        sorted(list(invalid_exchanges))))
        for invalid_tickers in invalid_overlap_ticker_sets:
            raise Exception('Cannot have tickers included and excluded: '
                    + gen_utils.list_to_quoted_element_str(
                        sorted(list(invalid_tickers))))
        # Else, all good -- nothing to return!



    @staticmethod
    def _build_where_for_df_ids(df, include_df_ids=None, exclude_df_ids=None):
        """
        """
        if include_df_ids is not None or exclude_df_ids is not None:
            dfs_allowed, include_dfs_missing = DatafeedSrc.get_by_column(
                    df.db.orm, 'name', include_df_ids, include_missing=True)
            dfs_disallowed, exclude_dfs_missing = DatafeedSrc.get_by_column(
                    df.db.orm, 'name', exclude_vals=exclude_df_ids,
                    include_missing=True)
            if include_dfs_missing:
                logger.warning('Skipping missing include fk datafeeds for'
                        f" datafeed '{df.df_id}': "
                        + gen_utils.list_to_quoted_element_str(
                            [d.name for d in include_dfs_missing]) + ".")
            if include_dfs_missing:
                logger.warning('Skipping missing exclude fk datafeeds for'
                        f" datafeed '{df.df_id}': "
                        + gen_utils.list_to_quoted_element_str(
                            [d.name for d in exclude_dfs_missing]) + ".")

            where_df_ids = DatafeedSrc.build_where_for_column('id',
                    [d.id for d in dfs_allowed],
                    [d.id for d in dfs_disallowed])
        else:
            where_df_ids = None

        return where_df_ids
