# Usage

# Contributing

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
