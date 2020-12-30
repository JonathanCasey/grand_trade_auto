# Setup

# Using

### Database: PostgreSQL
If using PostgreSQL as a database for some or all data, the
[Getting Started docs on PostgreSQL](https://www.postgresqltutorial.com/postgresql-getting-started/)
are fantastic.


### Config files
The config files in `/config/stubs` must be copied to `/config` with the
`.default` suffix dropped; the rest of the filename must remain unchanged (e.g.
`/config/stubs/databases.conf.default` -> `/config/databases.conf`).

**DATA LOSS WARNING**: If planning to run unit tests, a test env database config
will need to be provided.  This MUST be different from the database used for
production and development, as it will create, add/modify data, and then drop
the database.  IF YOU USE THE SAME DATABASE AS YOUR PRODUCTION OR DEVELOPMENT
DATABASE, YOU WILL LOSE THAT DATABASE!


##### Logger
The `logger.conf` file, for the most part, follows the standard format for use
with `logging.config.fileConfig()`.  Only the root logger is supported.  The
`logger.conf.default` has the recommended initial settings, though some details
like the log file location should be set accordingly.

There are a couple extra items added to the handlers beyond the standard options
supported by `logging.config.fileConfig()`.  Note that these options are not
perfect since it can only try to match the handler on some of the config
parameters because the name is not stored (should be added in python 3.10 as
indicated by
[this commit](https://github.com/python/cpython/commit/b15100fe7def8580c78ed16f0bb4b72b2ae7af3f)).
This should only matter if the class, level, and format specifier all match.

Each handler can specify a `max level` as well.  This can be specified in name
or in number format, and will setup a filter so messages at this level and below
(and in accordance with the `level` parameter) are included while ones above are
not.

The handlers also allow `allow level override lower` and
`allow level override raise` to be specified.  This allows the option for CLI
invocation of the python module to provide an argument to override the log level
of the root logger and of the handlers that have one of these options.  Allowing
lower will let the handler's level be overridden with a lower value; while
allowing higher will only allow the handler's level to be overridden with a
higher one.  It is not recommended to use both together in one handler.  This
does not impact the `max level` setting at all.

The logger provides another logger level of `disabled` to disable a logger -- no
code will log to that level.  The CLI arg override can specify any of these log
levels by name, as well as use `all` or `verbose` to be equivalent to `notset`.

The logger levels are recommended to adhere to these general guidelines
([source](https://www.loggly.com/use-cases/6-python-logging-best-practices-you-should-be-aware-of/)):
- `debug`: Debugging purposes in development.
- `info`: Something interesting but expected happens.
- `warning`: Something unexpected or unusual happens.  Not an error, but
      attention warranted.
- `error`: Something went wrong but is usually recoverable.
- `critical`: Doomsday scenario. The application is unusable. Someone should be
      woken up at 2 a.m.

When setting a level for the logger, it will report all log messages for that
level and more severe.  In this regard, `notset` is "less severe" than `debug`
and therefore reports everything; while `disabled` is "more severe" then
`critical` and would report nothing.  Not setting the handler is the same as
`notset`.

As explained [here](https://stackoverflow.com/a/17668861), if the logger and the
handler are set to different levels, the effective output will be the most
severe of both.  For example, if the logger is set to `info` and the handler is
set to `error`, then `error` and `critical` log messages will be outputted.  The
same would be true if the logger were `error` and the handler were `info`.



# Contributing

## One-time Setup

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
obvious (e.g. `docker-hub-creds` is intended to defind the user/pass env vars).
For the Docker Hub password, an access token should be created on the Security
page of your Docker Hub account profile.
