# Python-FastAPI

FastAPI component of the portfolio

## Docker

After opening the devcontainer, open main.py, go to the bottom right corner and click on the "3.12" to select the Python interpreter inside the container.
Select the one that has ".venv" in its path (it should be "Recommended"). Then reload the VSCode window.

## Host binding in Docker (devcontainer)

If you go to `http://localhost:8000/docs` and it doesn't load, you might need to change the host binding in `main.py` from `127.0.0.1` to `0.0.0.0`

## Run the app

```bash
fastapi dev main.py
```
