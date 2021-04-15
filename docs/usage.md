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
