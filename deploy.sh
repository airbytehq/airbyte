# Build SurveyCTO connector image
cd airbyte-integrations/connectors/source-surveycto && docker build . -t airbyte/source-surveycto:dev

# Build Commcare connector image
cd airbyte-integrations/connectors/source-commcare && docker build . -t airbyte/source-commcare:dev

docker compose up -d