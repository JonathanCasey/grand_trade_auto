



from abc import ABC
from collections import namedtuple



# TODO: Shared enums also here



class Model(ABC):
    """
    """

    _tablename = None
    _columns = None


    def _active_as_namedtuple(self):
        """
        """
        ActiveRecord = namedtuple(type(self).__name__, self._active_cols)
        return ActiveRecord({c: getattr(self, c) for c in self._active_cols})


    def __init__(self, **data):
        """
        """
        self._orm = None
        self._active_cols = set()
        for k, v in data.items():
            self.__setattr__(k, v)

    def __setattr__(self, name, value):
        if name in self._columns:
            self._active_cols.add(name)
        return super().__setattr__(name, value)



    @classmethod
    def add_direct(cls):
        """
        """

    def add(self):
        """
        """
        self._orm.add()
