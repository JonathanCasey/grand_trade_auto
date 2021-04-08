# Usage

## Executing
Main scripts intended for execution are in the root of `grand_trade_auto`.
These need to be run from the repo root to make paths work correctly.  E.g.:
```bash
cd /path/to/repo/root
python grand_trade_auto/tmp_main.py
```

The only exception to this is the web interface.  To run with `uvicorn`:
```bach
cd /path/to/repo/root
uvicorn main_web:app --app-dir /grand_trade_auto/web/backend
# Optionally, use `--reload` in `uvicorn` command during dev
```

This will make the page accessible at
[http://localhost:8000](http://localhost:8000) (unless port changed via `--port`
arg to `uvicorn`, then use that port), with auto-generated docs at
[http://localhost:8000/docs](http://localhost:8000/docs) and the redocs version
at [http://localhost:8000/redoc](http://localhost:8000/redoc).

It is recommended to wrap uvicorn in something such as a service to ensure it is
restarted when deployed.



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


## Unit Testing Jinja2
The goal of jinja2 unit testing is to ensure templates can be rendered and that
necessary fields exist as expected.

There is a slight but ultimately inconsequential discrepancy between the unit
testing and deployment when it comes to safe escaping.  FastAPI appears to
autoescape by default.  In unit testing, the Jinja2 environment is manually
configured to autoescape.  These may seem to differ in presentation -- the unit
testing will show `<` as `lt;` and such, while viewing the FastAPI rendering in
a browser may show the actual characters `<` and such rather than performing the
HTML instructions indicated by that tag.  This is really a difference in how the
browser may choose to display this, as viewing the source (not inspection in
Chrome) will show the `lt;`.

Unit tests will generate temporary copies of the jinja2 templates so that
fastapi elements can be factored out.  These are done on a pytest session basis,
so they will be created in the `/tests/unit/web/frontend/templates` dir with a
`tmp_sanitized__` prefix at the start of running a test session and will be
deleted when those tests are complete.  If these files do remain for any reason,
it is fine and perhaps preferable to manually delete them.


## Color Palette
The following is the color scheme used for this project.

 Type      | RGB Color | Name
:----------|:----------|:------
 Primary   | ![#85BB65](https://via.placeholder.com/15/85BB65/000000?text=+) `#85BB65` | Pistachio / Dollar bill
 Secondary | ![#363636](https://via.placeholder.com/15/363636/000000?text=+) `#363636` | Jet
 Tertiary  | ![#7D869C](https://via.placeholder.com/15/7D869C/000000?text=+) `#7D869C` | Roman Silver
