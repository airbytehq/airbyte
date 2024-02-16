
# Paypal Transaction Source

This is the repository for the Paypal Transaction configuration based source connector.
For information about how to use this connector within Airbyte, see [the documentation](https://docs.airbyte.com/integrations/sources/paypal-transaction).

## Local development

#### Prerequisites
  * Python (~=3.9)
  * Paypal Client ID and Client Secret
  * If you are going to use the data generator scripts you need to setup yourPaypal Sandbox and a Buyer user in your sandbox, to simulate the data. YOu cna get that information in the [Apps & Credentials page](https://developer.paypal.com/dashboard/applications/live).
     * Buyer Username
     * Buyer Password
     * Payer ID (Account ID)

#### Create credentials
**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/sources/paypal-transaction)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `source_paypal_transaction/spec.yaml` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.
See `integration_tests/sample_config.json` for a sample config file.

**If you are an Airbyte core member**, copy the credentials in Lastpass under the secret name `source paypal-transaction test creds`
and place them into `secrets/config.json`.

### Locally running the connector docker image

* You must have created your credentials under the `secrets/` folder
* For the read command, you can create separate catalogs to test the streams individually. All catalogs are under the folder `integration_tests`. Select the one you want to test with the read command.

```
python main.py spec
python main.py check --config secrets/config.json
python main.py discover --config secrets/config.json
#Example with list_payments catalog and the debug flag
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog_list_payments.json --debug
```

#### Use `airbyte-ci` to build your connector
The Airbyte way of building this connector is to use our `airbyte-ci` tool.
You can follow install instructions [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md#L1).
Then running the following command will build your connector:

```bash
airbyte-ci connectors --name=source-paypal-transaction build
```
Once the command is done, you will find your connector image in your local docker registry: `airbyte/source-paypal-transaction:dev`.


##### Customizing our build process
When contributing on our connector you might need to customize the build process to add a system dependency or set an env var.
You can customize our build process by adding a `build_customization.py` module to your connector.
This module should contain a `pre_connector_install` and `post_connector_install` async function that will mutate the base image and the connector container respectively.
It will be imported at runtime by our build process and the functions will be called if they exist.

Here is an example of a `build_customization.py` module:
```python
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Feel free to check the dagger documentation for more information on the Container object and its methods.
    # https://dagger-io.readthedocs.io/en/sdk-python-v0.6.4/
    from dagger import Container


async def pre_connector_install(base_image_container: Container) -> Container:
    return await base_image_container.with_env_variable("MY_PRE_BUILD_ENV_VAR", "my_pre_build_env_var_value")

async def post_connector_install(connector_container: Container) -> Container:
    return await connector_container.with_env_variable("MY_POST_BUILD_ENV_VAR", "my_post_build_env_var_value")
```

#### Build your own connector image
This connector is built using our dynamic built process in `airbyte-ci`.
The base image used to build it is defined within the metadata.yaml file under the `connectorBuildOptions`.
The build logic is defined using [Dagger](https://dagger.io/) [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/pipelines/builds/python_connectors.py).
It does not rely on a Dockerfile.

If you would like to patch our connector and build your own a simple approach would be to:

1. Create your own Dockerfile based on the latest version of the connector image.
```Dockerfile
FROM airbyte/source-paypal-transaction:latest

COPY . ./airbyte/integration_code
RUN pip install ./airbyte/integration_code

# The entrypoint and default env vars are already set in the base image
# ENV AIRBYTE_ENTRYPOINT "python /airbyte/integration_code/main.py"
# ENTRYPOINT ["python", "/airbyte/integration_code/main.py"]
```
Please use this as an example. This is not optimized.

2. Build your image:
```bash
docker build -t airbyte/source-paypal-transaction:dev .
# Running the spec command against your patched connector
docker run airbyte/source-paypal-transaction:dev spec
```
#### Run
Then run any of the connector commands as follows:
```
docker run --rm airbyte/source-paypal-transaction:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-paypal-transaction:dev check --config /secrets/config_oauth.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-paypal-transaction:dev discover --config /secrets/config_oauth.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-paypal-transaction:dev read --config /secrets/config_oauth.json --catalog /integration_tests/configured_catalog.json
```

## Testing with CI test suite
You can run our full test suite locally using [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md):
```bash
airbyte-ci connectors --name=source-paypal-transaction test
```

If you ar etesting locally, you can use your local credentials (config.json file) by using `--use-local-secrtes`

```bash
airbyte-ci connectors --name source-paypal-transaction --use-local-secrets test
```

### Customizing acceptance Tests
Customize `acceptance-test-config.yml` file to configure tests. See [Connector Acceptance Tests](https://docs.airbyte.com/connector-development/testing-connectors/connector-acceptance-tests-reference) for more information.
If your connector requires to create or destroy resources for use during acceptance tests create fixtures for it and place them inside integration_tests/acceptance.py.

## Running Unit tests locally

To run unit tests locally, form the root `source_paypal_transaction` directory run:

```bash
python -m pytest unit_test
```

## Test changes in the sandbox

If you have a [Paypal Sandbox](https://developer.paypal.com/tools/sandbox/accounts/) you will be able to use some APIs to create new data and test how data is being created in your destinaiton and choose the best syn strategy that suits better your use case.
Some endpoints will require special permissions on the sandbox to update and change some values.

In the `bin` folder you will find several data generator scripts:

* **disputes_generator.py:** 
   * Update dispute: Uses the _PATCH_ method of the `https://api-m.paypal.com/v1/customer/disputes/{dispute_id}` endpoint. You need the ID and create a payload to pass it as an argument. See more information [here](https://developer.paypal.com/docs/api/customer-disputes/v1/#disputes_patch).

   ```bash
   python disputes_generator.py update DISPUTE_ID ''[{"op": "replace", "path": "/reason", "value": "The new reason"}]'
   ```
   
   * Update Evidence status: Uses the _POST_ method of the `https://api-m.paypal.com/v1/customer/disputes/{dispute_id}/require-evidence` endpoint. You need the ID and select an option to pass it as an argument. See more information [here](https://developer.paypal.com/docs/api/customer-disputes/v1/#disputes_require-evidence)
   ```bash
   python update_dispute.py require-evidence DISPUTE_ID SELLER_EVIDENCE
   ```

* **invoices.py:** 
   * Create draft invoice: Uses the _POST_ method of the `https://api-m.sandbox.paypal.com/v2/invoicing/invoices` endpoint. It will automatically generate an invoice (no need to pass any parameters). See more information [here](https://developer.paypal.com/docs/api/invoicing/v2/#invoices_create).

   ```bash
   python invoices.py create_draft
   ```
   
   * Send a Draft Invoice: Uses the _POST_ method of the `https://api-m.sandbox.paypal.com/v2/invoicing/invoices/{invoice_id}/send` endpoint. You need the Invoice ID, a subject and a note (just to have something to update) and an email as an argument. See more information [here](https://developer.paypal.com/docs/api/invoicing/v2/#invoices_send)
   ```bash
   python invoices.py send_draft --invoice_id "INV2-XXXX-XXXX-XXXX-XXXX" --subject "Your Invoice Subject" --note "Your custom note" --additional_recipients example@email.com
   ```

* **payments_generator.py:** 
   * Partially update payment: Uses the _PATCH_ method of the `https://api-m.paypal.com/v1/payments/payment/{payment_id}` endpoint. You need the payment ID and a payload with new values. (no need to pass any parameters). See more information [here](https://developer.paypal.com/docs/api/invoicing/v2/#invoices_create).

   ```bash
    python script_name.py update PAYMENT_ID '[{"op": "replace", "path": "/transactions/0/amount", "value": {"total": "50.00", "currency": "USD"}}]'
   ```
   
* **paypal_transaction_generator.py:** 
   Make sure you have the `buyer_username`, `buyer_password` and `payer_id` in your config file. You can get the sample configuratin in the `sample_config.json`. 

   * Generate transactions: This uses Selenium, so you will be prompted to your account to simulate the complete transaction flow. You can add a number at the end of the command to do more than one transaction. By default the script runs 3 transactions.

   **NOTE: Be midnfu of the number of transactions, as it will be interacting with your machine, and you may not be able to use it while creating the transactions** 

   ```bash
    python paypal_transaction_generator.py [NUMBER_OF_DESIRED_TRANSACTIONS]
   ```

* **product_catalog.py:** 
   * Create a product: Uses the _POST_ method of the `https://api-m.sandbox.paypal.com/v1/catalogs/products` endpoint. You need to add the description and the category in the command line. For the proper category see more information [here](https://developer.paypal.com/docs/api/catalog-products/v1/#products_create).

   ```bash
   python product_catalog.py --action create --description "YOUR DESCRIPTION" --category PAYPAL_CATEGORY
   ```
   
   * Update a product: Uses the _PATCH_ method of the `https://developer.paypal.com/docs/api/catalog-products/v1/#products_patch` endpoint. You need the product ID, a description and the Category as an argument. See more information [here](https://developer.paypal.com/docs/api/catalog-products/v1/#products_patch)
   ```bash
   python product_catalog.py --action update --product_id PRODUCT_ID --update_payload '[{"op": "replace", "path": "/description", "value": "My Update. Does it changes it?"}]'
   ```

## Dependency Management
All of your dependencies should go in `setup.py`, NOT `requirements.txt`. The requirements file is only used to connect internal Airbyte dependencies in the monorepo for local development.
We split dependencies between two groups, dependencies that are:
* required for your connector to work need to go to `MAIN_REQUIREMENTS` list.
* required for the testing need to go to `TEST_REQUIREMENTS` list

### Publishing a new version of the connector
You've checked out the repo, implemented a million dollar feature, and you're ready to share your changes with the world. Now what?
1. Make sure your changes are passing our test suite: `airbyte-ci connectors --name=source-paypal-transaction test`
2. Bump the connector version in `metadata.yaml`: increment the `dockerImageTag` value. Please follow [semantic versioning for connectors](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#semantic-versioning-for-connectors).
3. Make sure the `metadata.yaml` content is up to date.
4. Make the connector documentation and its changelog is up to date (`docs/integrations/sources/paypal-transaction.md`).
5. Create a Pull Request: use [our PR naming conventions](https://docs.airbyte.com/contributing-to-airbyte/resources/pull-requests-handbook/#pull-request-title-convention).
6. Pat yourself on the back for being an awesome contributor.
7. Someone from Airbyte will take a look at your PR and iterate with you to merge it into master.

