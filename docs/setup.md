# Setup

# Using

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
    "python.testing.pytestEnabled": true
}
```

Also create a `.env` file in the root of the repo with the following line:
```
PYTHONPATH=C:\path\to\the\repo\root;${PYTHONPATH}
```

Note that in the above, if not on Windows, the semicolon `;` separator should be
replaced with a colon `:`.


### CircleCI
If forking this project, CircleCI will need contexts setup.  See
`.circleci/config.yml` for the contexts needed; the contents should be mostly
obvious (e.g. `docker-hub-creds` is intended to defind the user/pass env vars).
For the Docker Hub password, an access token should be created on the Security
page of your Docker Hub account profile.
