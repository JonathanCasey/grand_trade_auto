#!/usr/bin/env python3
"""
Holds the generic datafeed meta-class that others will subclass.  Any other
shared datafeed code that needs to be accessed by all datafeeds can be
implemented here so they have access when this is imported.

Module Attributes:
  logger (Logger): Logger for this module.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from abc import ABC, abstractmethod
import logging
import pickle

from grand_trade_auto.apic import apics
from grand_trade_auto.database import databases
from grand_trade_auto.datafeed.jobs import datafeed_job
from grand_trade_auto.general import config
from grand_trade_auto.model import model_meta
from grand_trade_auto.model.datafeed_src import DatafeedSrc



logger = logging.getLogger(__name__)


# TODO Tomorrow: Re-org everything to finish "design", fill in last missing functions / errors, commit, doc + unit test (same time)!
# will keep datafeed, datafeedjob, and anything else abstract/general use here


class Datafeed(ABC):
    """
    The abstract class for all datafeed functionality.  Each datafeed type will
    subclass this, but externally will likely only call the generic methods
    defined here to unify the interface.

    Class Attributes:
      N/A

    # TODO: Correct all this
    Instance Attributes:
      [inherited from Apic]:
        _env (str): The run environment type valid for using this broker.
        _apic_id (str): The id used as the section name in the API Client conf.
    """
    @abstractmethod
    def __init__(self, env, df_id, apic, db, config_data, **kwargs):
        """
        Creates the datafeed handle.

        Args:
          See parent(s) for required kwargs.
        """
        self._env = env
        self._df_id = df_id
        self._apic = apic
        self._db = db
        self._config_data = config_data
        self._job_cls = datafeed_job.DatafeedJob.get_class_from_name(
                self._config_data['data category'])
        self._queued_jobs = self._load_and_validate_queued_jobs()
        self._save_config_data()

        # df_model = self._get_self_model()
        # if not self.is_same_config(df_model.config_parser, df_cp):
        #     self.invalidate_wip_jobs()
        #     # TODO: Invalidate linked data?
        # self._jobs_queued_in_db self.get_jobs_from_db = df_model.progress_marker
        # # TODO: Rename progress marker to jobs in db

        if kwargs:
            logger.warning('Discarded excess kwargs provided to'
                    + f' {self.__class__.__name__}: {", ".join(kwargs.keys())}')



    def get_apic_id(self):
        """
        """
        return self._apic._apic_id



    @classmethod
    def load_from_config(cls, df_cp, df_id):
        """
        """
        data = datafeed_job.DatafeedJob.load_data_from_config_by_category(
                df_cp, df_id)
        kwargs = {}
        kwargs['env'] = data['env']
        kwargs['df_id'] = df_id
        kwargs['apic'] = apics.get_apic(data['apic_src'], data['env'])
        kwargs['db'] = databases.get_database(data['database_dst'],
                data['env'])
        kwargs['config_data'] = data
        return cls(**kwargs)



    # TODO: Add caching?
    def _get_self_model(self):
        """
        """
        where = ('section_name', model_meta.LogicOp.EQUALS, self._df_id)
        self_db_record = DatafeedSrc.query_direct(
                self._db._orm, where=where)
        if self_db_record is None:
            self._add_db_self()
        self_db_record = DatafeedSrc.query_direct(
                self._db._orm, where=where)
        return self_db_record



    def _add_db_self(self):
        """
        """
        data = {}
        data['name'] = self._df_id
        data['config_data'] = self._convert_config_data_to_db()
        data['is_init_complete'] = False
        data['queued_jobs'] = None
        self_db_record = DatafeedSrc(self._db.orm, data)
        self_db_record.add()



    @staticmethod
    def _is_same_config(config_data_1, config_data_2):
        """
        """
        return config_data_1 == config_data_2



    def _load_and_validate_queued_jobs(self):
        """
        """
        df_model = self._get_self_model()
        config_data_from_db = self._convert_db_to_config_data(
                df_model.config_data)
        # TODO: Change to is_critically_same_config() to ignore things like run time?
        if not self._is_same_config(config_data_from_db, self._config_data):
            self._invalidate_queued_jobs()
            # TODO: Invalidate linked data?  Warn possibly orphaned data?
        return self._job_cls.convert_db_to_jobs(df_model.queued_jobs)



    def is_due_to_run(self):
        """
        """
        # TODO: Check dependent datafeeds are init
        # TODO: Check datetime good
        return True



    def queue_jobs_due_to_run(self):
        """
        """
        if not self.is_due_to_run():
            return

        df_model = self._get_self_model()
        new_jobs = []
        if not df_model.is_init_complete \
                and not any([j.is_for_init for j in self._queued_jobs]):
            new_init_job = self._job_cls(self._config_data, is_for_init=True)
            new_jobs.append(new_init_job)
        new_update_job = self._job_cls(self._config_data)
        new_jobs.append(new_update_job)
        self._save_jobs(new_jobs)



    def handle_finished_job(self, job):
        """
        """
        try:
            self._queued_jobs.remove(job)
        except ValueError as ex:
            logger.warning('Could not remove job since not loaded in queue.'
                    f'  Original error message: {str(ex)}')
        self._save_jobs()



    def _invalidate_queued_jobs(self):
        """
        """
        df_model = self._get_self_model()
        df_model.queued_jobs = None
        df_model.update()



    def _save_jobs(self, additional_jobs=None):
        """
        """
        if additional_jobs is not None:
            self._queued_jobs.extend(additional_jobs)
        queued_jobs_db_data = self._job_cls.convert_jobs_to_db(
                self._queued_jobs)
        df_model = self._get_self_model()
        df_model.queued_jobs = queued_jobs_db_data
        df_model.update()



    def _save_config_data(self):
        df_model = self._get_self_model()
        config_data_db_data = self._convert_config_data_to_db()
        df_model.config_data = config_data_db_data
        df_model.update()



    def _convert_config_data_to_db(self):
        """
        """
        return pickle.dumps(self._config_data, config.PICKLE_PROTOCOL)



    @staticmethod
    def _convert_db_to_config_data(config_db_data):
        """
        """
        return pickle.loads(config_db_data, config.PICKLE_PROTOCOL)



    def run_queued_jobs(self):
        """
        """
        self._job_cls.execute_jobs(self._queued_jobs)
