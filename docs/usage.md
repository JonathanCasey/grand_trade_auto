# Usage

## Executing
Main scripts intended for execution are in the root of `grand_trade_auto`.
These need to be run from the repo root to make paths work correctly.  E.g.:
```bash
cd /path/to/repo/root
python grand_trade_auto/tmp_main.py
```



# Contributing

## Logger
Balancing readability against performance, the pylint warning
`logging-fstring-interpolation` is disabled.  The intention is largerly for this
to apply to warnings and more severe log levels as well as anything that would
be low overhead.  It is recommended that anything info or debug level,
especially if there are many calls or each call is an time-expensive
interpolation to use the `logger.debug('log %(name)s', {'name'=name_var})` sort
of methods instead so that the interpolation is only executed when that logger
level is enabled.


## Workflows
Before pushing, it is recommended to run through the checks that CircleCI will
run.  In short, this is largely running from the repo root:
```
python -m pylint grand_trade_auto
python -m pylint tests
pytest
```


## Postgres / psycopg2

##### Unit test error: `psycopg2.errors.ObjectInUse`
If unit tests cannot be run successfully due to `psycopg2.errors.ObjectInUse`,
this may be to the database being open in postgres.

If `pgAdmin` is in use, the database should show as uncolored with a red `x` to
indicate it is disconnected.  Otherwise, will need to right click the database
and select "Disconnect Database...".  (If database does not show at all, may
need to right-click the Databases list and select "Refresh...", though the unit
tests aim to drop the database when done).

Any `psql` connections to the database should similarly be reviewed for any
disconnects required.
