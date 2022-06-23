


from abc import ABC, abstractmethod, abstractclassmethod
from enum import Enum
import pickle

from grand_trade_auto.general import config
# from grand_trade_auto.datafeed import datafeeds



_DATAFEED_JOBS = set()

def register_datafeed_job_cls(job_cls):
    _DATAFEED_JOBS.add(job_cls)




# TODO: This name sucks
class WhenToRun(Enum):
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
        # self.df = None
        self._init_nonserial()



    def _init_nonserial(self):
        """
        """
        # TODO: Need to resolve the circular reference / file structure
        #      ...probably need df passed as needed to functions by caller
        # TODO: Avoid this by passing df when calling execute_job*?
        # self.df = datafeeds.get_datafeed(self.config_data['df_id'],
        #         self.config_data['env'])



    def _clear_nonserial(self):
        """
        """
        # self.df = None


    @classmethod
    def load_data_from_config_by_category(cls, df_cp, df_id):
        data_cat_name = df_cp.get(df_id, 'data category', fallback=None)
        df_job_cls = cls.get_class_from_name(data_cat_name)
        if df_job_cls is None:
            raise Exception('Invalid category in datafeed config:'
                    f'{data_cat_name}')
        return df_job_cls.load_data_from_config(df_cp, df_id)


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


    @abstractmethod
    def build_resume_string(self):
        """
        """


    @abstractmethod
    def get_iterator(self):
        """
        Get the iterator that will step through data in chunks compatible with
        resume.
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



    @staticmethod
    def convert_jobs_to_db(jobs):
        """
        """
        for job in jobs:
            job._clear_nonserial()
        job_db_data = pickle.dumps(jobs, config.PICKLE_PROTOCOL)
        for job in jobs:
            job._init_nonserial()
        return job_db_data



    @staticmethod
    def convert_db_to_jobs(jobs_db_data):
        """
        """
        jobs = pickle.loads(jobs_db_data, config.PICKLE_PROTOCOL)
        for job in jobs:
            job._init_nonserial()
        return jobs
