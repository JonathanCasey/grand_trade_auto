# Contributing

Guidelines for contributing are largely TBD, as this is a solo project at this
time.  Helpful items for setup and usage, including for forking, are below.

Follow existing conventions as best as possible.

Respect the CI and the CI will respect you.

- [One-time Setup](#one-time-setup)
- [Usage](#usage)
- [Design Conventions](#design-conventions)



# One-time Setup

### Python environment and VSCode Setup
In general the repo root should be added to the python path environment
variable.  Python automatically adds the directory of the module being executed
to the path, but elements of this project will not work unless the repo root is
in the path, and there are no modules that execute from the repo root.

Save this workspace, and edit the workspace settings (Ctrl+Shift+P >
`Preferences: Open Workspace Settings (JSON)`) and ADD the following to the
existing settings.  This workspace file should be the one opened everytime
evelopment is being started.  The workspace will need to be closed and reopened
after editing these workspace settings:
```json
{
	"settings": {
		"terminal.integrated.env.linux": {               // If developing on Linux
			"PYTHONPATH": "/path/to/repo/root"
		},
    "terminal.integrated.env.osx": {                 // If developing on Mac OSX
			"PYTHONPATH": "/path/to/repo/root"
		},
    "terminal.integrated.env.windows": {             // If developing on Windows
			"PYTHONPATH": "C:/path/to/repo/root",
			"WSLENV": "PYTHONPATH/l"                       // If using WSL in Windows
		}
	}
}
```


In Windows, one way of using a specific version of python is to open a cmd
prompt (not powershell) -- probably as admin -- and navigate to the desired
older python version's folder.  Then, run
`mklink python3.7.exe C:\path\to\python37\python.exe` to make a sym link for
python 3.7, for example.  Now this can be evoked with `python3.7`.

While the admin prompt is open, this might be the best time to install
required pacakges with pip (can use `pip3.7` in this example) as installing as a
user can cause some headaches...  It has been observed that after installing
`pytest-order` as admin, the first run of `pytest` needs to be run as an admin
to finish some sort of init it seems -- after that, it should work as a user.


To support pytest and pylint, add the following to `.vscode/settings.json` in
the root of the repo:
```json
{
    "python.linting.pylintEnabled": true,
    "python.testing.pytestArgs": [
        "."
    ],
    "python.testing.pytestEnabled": true
}
```

In the `python.testing.pytestArgs` list above, it is likely desireable to put
some pytest args.  In particular, using `--skip-alters-db-schema` will run the
most tests.  This does mean other args needs to be tested separately.  Without
this, there may be inconsistent test results since some tests can be mutually
exclusive.


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
  - `alphavantage-test`
- `databases.conf`
  - `postgres-test` (do NOT use production db.  WILL be DELETED!)

The `env` for each of those must be `test`.

Note that some test WILL make API calls, so it will count against any rate
limiting or quotas.



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
python -m pylint ci_support
python -m pylint conftest

python ci_support/dir_init_checker.py grand_trade_auto
python ci_support/dir_init_checker.py ci_support
python ci_support/dir_init_checker.py tests

python -m pytest --cov=grand_trade_auto --run-only-alters-db-schema tests/unit
python -m pytest --cov=grand_trade_auto --cov-append --skip-alters-db-schema tests/unit
python -m pytest --run-only-alters-db-schema tests/integration
python -m pytest --skip-alters-db-schema tests/integration
```

Integration tests are intentionally omitted from code coverage reporting.  All
code coverage should be 100% based on unit testing.  Integration testing is
gravy!


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



# Design Conventions

## Unit Test Order
As much as possible, this is avoided; but with some tests that interact with
persistent data such as a database, this can be important.

When it comes to `pytest.mark.alters_db_schema`, these tests have an order for
the tests to do last, where the last test is the lowest level / most disruptive
test (drop database), and the 2nd to last is the next lowest level (e.g. types),
the 3rd to last is the next lowest (e.g. tables), etc.

For db-orm-model integration tests, such as `test_int__postgres_orm_models.py`,
there order for each `model_crud` test is based on dependencies.  1st tests
without any dependencies are run, then 2nd are tests that may depend only on
those models (since they will then require fixtures for those dependent models),
and so on.
