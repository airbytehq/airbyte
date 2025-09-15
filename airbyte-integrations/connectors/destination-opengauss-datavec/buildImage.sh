cd /home/hly/airbyte/airbyte-ci/connectors/pipelines/
eval "$(poetry env activate)"

airbyte-ci connectors --name destination-opengauss-datavec build -t dev
