
"""

Subclasses will hold the actual SQL / etc queries for their individual tied dbs.

"""

from abc import ABC, abstractmethod


class Orm(ABC):
    """
    """

    def __init__(self):
        """
        """
        self._db = None


    def create_schemas(self):
        """
        """
        self._create_schema_datafeed_src()


    @abstractmethod
    def _create_schema_datafeed_src(self):
        """
        """


    @abstractmethod
    def add(self):
        """
        """
