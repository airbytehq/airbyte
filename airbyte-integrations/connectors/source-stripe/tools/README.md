This is a tool to seed records into a test Stripe account.

The script currently only supports creating customers and bank accounts.

You can use the `generate-customers` command to create customers from a template.

Example:
`python tools/create_customers.py  generate-customers tools/customers_template.json --tag 08-23 --iterations 100 --output-path secrets/customers.json`
This command will create 100 copies of the customers and their bank accounts, replacing the `{TAG}` and `{ITERATION}` template variables with the tag passed as argument, and the iteration number.

The generated output file can then serve as input to the `populate-customers` command:

Example:
`python tools/create_customers.py populate-customers --config-path secrets/performance-config.json --data-path secrets/customers.json --concurrency 10`
This command will call the Stripe API and create the records and bank accounts that were previously generated.
- `config-path` is the path to a connector config file
- `data-path` is the path to a JSON file containing the records to create
- `concurrency` is the size of the threadpool

The `populate-customers` command will skip customer records that already exists in the Stripe account (using the name as the identity).