# Connector builder


## Getting started 

Setup the virtual environment and install dependencies
```python
python -m venv .venv
source .venv/bin/activate
pip install .
```

Then run the server
```python
uvicorn connector_builder.entrypoint:app --port 8080
```

The server is now reachable on localhost:8080

