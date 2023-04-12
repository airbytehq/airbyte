poetry2setup >> setup.py
dagster-cloud serverless deploy-python-executable --location-name metadata_service_orchestrator --location-file dagster_cloud.yaml --python-version 3.9
rm setup.py