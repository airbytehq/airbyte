from airbyte_lib import get_connector

# preparation (from airbyte-lib main folder):
#   python -m venv .venv-source-stripe
#   source .venv-source-stripe/bin/activate
#   pip install -e ../airbyte-integrations/connectors/source-stripe
# In separate terminal:
#   poetry run python examples/run_stripe.py

con = get_connector("source-stripe")

for msg in con._execute(["spec"]):
    print(msg)