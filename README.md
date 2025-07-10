## iSPAT Backend

### How to run the server:
1. Run prestart command
```sh
./scripts/prestart.sh
```

2. Run uvicorn via
```sh
poetry run fastapi run --reload app/main.py
```

**API Docs will be hosted at /docs, or /redoc**
