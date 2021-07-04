# Contributing

Guidelines for contributing are largely TBD, as this is a solo project at this
time.  Helpful items for setup and usage, including for forking, are below.

Follow existing conventions as best as possible.

Respect the CI and the CI will respect you.

- [One-time Setup](#one-time-setup)
- [Usage](#usage)



# One-time Setup

### Python environment in VSC
To support pytest, add the following to `.vscode/settings.json` in the root of
the repo:
```json
{
    "python.envFile": "${workspaceFolder}/.env",
    "python.testing.pytestArgs": [
        "."
    ],
    "python.testing.pytestEnabled": true,
    "terminal.integrated.env.windows": {
        "PYTHONPATH": "${workspaceFolder}/grand_trade_auto;${env:PYTHONPATH}",
    }
}
```

Also create a `.env` file in the root of the repo with the following line:
```
PYTHONPATH=C:\path\to\the\repo\root;${PYTHONPATH}
```

Note that in the above, if not on Windows, the semicolon `;` separator should be
replaced with a colon `:`.

This only works when opening the folder.  If opened as part of a multi-folder
project, the `"terminal.integrated.env.windows"` will not be applied.  While not
the most elegant, running
`$env:PYTHONPATH = 'C:\path\to\repo\grand_trade_auto;' + $env:PYTHONPATH` will
do the trick (the last part for the plus `+` sign and onwards can be omitted if
it is not set at all yet).


### CircleCI
If forking this project, CircleCI will need contexts setup.  See
`.circleci/config.yml` for the contexts needed; the contents should be mostly
obvious (e.g. `docker-hub-creds` is intended to define the user/pass env vars).
For the Docker Hub password, an access token should be created on the Security
page of your Docker Hub account profile.

For `alpaca-paper-creds` it is STRONGLY REQUIRED the **paper** API credentials
are used (unless you really want to test with live trading / real money...).


### Config files and Unit Testing
While unit testing in CI uses mock configs, running unit testing locally expects
certain test environment configs to exist.  The following config sections/IDs
are required in their respective config files in order to run the relevant
unit tests:
- `apics.conf`:
  - `alpaca-test`
- `databases.conf`
  - `postgres-test` (do NOT use production db.  WILL be DELETED!)

The `env` for each of those must be `test`.



# Usage

## Logger
Balancing readability against performance, the pylint warnings
`logging-fstring-interpolation` and `logging-not-lazy` are disabled.  The
intention is largerly for this to apply to warnings and more severe log levels
as well as anything that would be low overhead.  It is recommended that anything
info or debug level, especially if there are many calls or each call is an
time-expensive interpolation to use the
`logger.debug('log %(name)s', {'name'=name_var})` sort of methods instead so
that the interpolation is only executed when that logger level is enabled.


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
