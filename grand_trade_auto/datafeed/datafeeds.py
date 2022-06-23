



from pkgutil import get_data
from grand_trade_auto.datafeed import alphavantage_df
from grand_trade_auto.general import config


_DFS = (
    alphavantage_df.AlphavantageDatafeed,
)

_dfs_loaded = {}



def get_datafeed(df_id, env=None):
    # TODO: Fix docstring
    """
    Gets the requested database.  Will return cached version if already
    loaded, otherwise will load and cache.

    Args:
      db_id (str): The section ID of the database from the databases.conf file.
      env (str or None): The environment for which this database is valid.
        Optional - can be used to be protect against incorrect access.

    Returns:
      db (Database<> or None): Returns the database that matches the given
        criteria, loading from conf if required.  None if no matching database.

    Raises:
      (AssertionError): Raised when an invalid combination of input arg
        criteria provided cannot guarantee a minimum level of definition.
    """
    assert df_id is not None

    if df_id in _dfs_loaded:
        if _dfs_loaded[df_id].matches_id_criteria(df_id, env):
            return _dfs_loaded[df_id]

    df = _get_datafeed_from_config(df_id, env)
    if df is not None:
        _dfs_loaded[df_id] = df
    return df



def ensure_all_datafeeds_loaded(env=None):
    """
    """
    df_cp = config.read_conf_file('datafeeds.conf')
    for df_id in df_cp.sections():
        # "get" has right code to load, but do not care about return
        get_datafeed(df_id, env)



def _get_datafeed_from_config(df_id, env=None):
    # TODO: Fix docstring
    """
    Loads the specified database from the config file.

    Arg:
      db_id (str): The section ID of the database from the databases.conf file
        to load.
      env (str or None): The environment for which this database is valid.
        Optional - can be used to be protect against incorrect access.

    Returns:
      db (Datbase<> or None): The database loaded and created from the config
        file based on the provided criteria.  None if no match found.

    Raises:
      (AssertionError): Raised if database cannot be loaded.
    """
    assert df_id is not None

    df_cp = config.read_conf_file('datafeeds.conf')

    if df_id not in df_cp.sections():
        return None

    if env is not None and env != df_cp[df_id]['env'].strip():
        return None

    df_sel = None
    for df in _DFS:
        # TODO: If file client, compare that instead
        if df_cp[df_id]['apic src'].strip() == df.get_apic_id():
            df_sel = df
            break

    if df_sel is None:
        return None

    df = df_sel.load_from_config(df_cp, df_id)
    return df



def queue_jobs_due_to_run(df_ids=None, env=None):
    """
    """
    if df_ids is None:
        df_ids = [df.id for df in _dfs_loaded]

    for df_id in df_ids:
        df = get_datafeed(df_id, env)
        if df is None:
            raise Exception(f'Invalid datafeed id to queue: {df_id}')
        df.queue_jobs_due_to_run()



def run_queued_jobs(df_ids=None, env=None):
    """
    """
    if df_ids is None:
        df_ids = [df.id for df in _dfs_loaded]

    for df_id in df_ids:
        df = get_datafeed(df_id, env)
        if df is None:
            raise Exception(f'Invalid datafeed id to run: {df_id}')
        df.run_queued_jobs()
