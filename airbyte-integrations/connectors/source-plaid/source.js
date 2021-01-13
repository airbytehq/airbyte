const fs = require('fs');
const axios = require('axios');
const path = require('path');
const { ArgumentParser } = require('argparse');
const dateFns = require('date-fns');
const getMilliseconds = dateFns.getMilliseconds;

async function read(config, catalog) {
  let balancesStream = null;
  for (const configuredStreamIndex in catalog.streams) {
    const configuredStream = catalog.streams[configuredStreamIndex];
    if (configuredStream.stream.name === 'balances') {
      balancesStream = configuredStream;
    }
  }

  if (balancesStream === null) {
    log('No streams selected');
    return;
  }
  // We only support full_refresh at the moment, so verify the user didn't ask for another sync mode
  if (balancesStream.sync_mode !== 'full_refresh') {
    log('This connector only supports full refresh syncs! (for now)');
    process.exit(1);
  }

  // If we've made it this far, all the configuration is good and we can pull the balance.
  const now = new Date();
  const url = `${getBaseUrl(config.plaid_env)}/accounts/balance/get`;
  const response = await axios.post(
    url,
    {
      access_token: config.access_token,
      client_id: config.client_id,
      secret: config.api_key,
    },
    { validateStatus: () => true }
  );

  if (response.status !== 200) {
    log('Failure occurred when calling Plaid API');
    process.exit(1);
  } else {
    response.data.accounts
      .map((account) => {
        const data = {
          account_id: account.account_id,
          available: account.balances.available,
          current: account.balances.current,
          iso_currency_code: account.balances.iso_currency_code,
          limit: account.balances.limit,
          unofficial_currency_code: account.balances.unofficial_currency_code,
        };
        const record = {
          stream: 'balances',
          data: data,
          emitted_at: getMilliseconds(now),
        };
        return { type: 'RECORD', record: record };
      })
      .forEach((record) => console.log(JSON.stringify(record)));
  }
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath));
}

function getBaseUrl(plaidEnv) {
  if (plaidEnv === 'sandbox') {
    return 'https://sandbox.plaid.com';
  } else if (plaidEnv === 'development') {
    return 'https://development.plaid.com';
  } else if (plaidEnv === 'production') {
    return 'https://production.plaid.com';
  } else {
    throw new Error('Invalid Plaid Environment');
  }
}

async function check(config) {
  // Validate input configuration by hitting the balance endpoint.
  let result;
  const url = `${getBaseUrl(config.plaid_env)}/accounts/balance/get`;
  const response = await axios.post(
    url,
    {
      access_token: config.access_token,
      client_id: config.client_id,
      secret: config.api_key,
    },
    { validateStatus: () => true }
  );
  if (response.status === 200) {
    result = { status: 'SUCCEEDED' };
  } else if (response.data.code === 'INVALID_ACCESS_TOKEN') {
    result = { status: 'FAILED', message: 'Access token is incorrect.' };
  } else {
    result = {
      status: 'FAILED',
      message: response.data.error_message,
    };
  }
  // Format the result of the check operation according to the Airbyte Specification
  const outputMessage = { type: 'CONNECTION_STATUS', connectionStatus: result };
  console.log(JSON.stringify(outputMessage));
}

function log(message) {
  const logJson = { type: 'LOG', log: message };
  console.log(logJson);
}

function discover() {
  const catalog = {
    streams: [
      {
        name: 'balance',
        supported_sync_modes: ['full_refresh'],
        json_schema: {
          properties: {
            account_id: {
              type: 'string',
            },
            available: {
              type: 'number',
            },
            current: {
              type: 'number',
            },
            iso_currency_code: {
              type: 'string',
            },
            limit: {
              type: 'number',
            },
            unofficial_currency_code: {
              type: 'string',
            },
          },
        },
      },
    ],
  };
  const airbyte_message = { type: 'CATALOG', catalog };
  console.log(JSON.stringify(airbyte_message));
}

function getInputFilePath(filePath) {
  if (path.isAbsolute(filePath)) {
    return filePath;
  } else {
    return path.join(process.cwd(), filePath);
  }
}

function spec() {
  // Read the file named spec.json from the module directory as a JSON file
  const specPath = path.join(path.dirname(__filename), 'spec.json');
  const specification = readJson(specPath);

  // form an Airbyte Message containing the spec and print it to stdout
  const airbyteMessage = { type: 'SPEC', spec: specification };

  console.log(JSON.stringify(airbyteMessage));
}

async function run(args) {
  const parentParser = new ArgumentParser({ add_help: false });
  const mainParser = new ArgumentParser({ add_help: false });
  const subparsers = mainParser.add_subparsers({ title: 'commands', dest: 'command' });

  // Accept the spec command
  subparsers.add_parser('spec', {
    help: 'outputs the json configuration specification',
    parents: [parentParser],
  });

  // Accept the check command
  const checkParser = subparsers.add_parser('check', {
    help: 'checks the config used to connect',
    parents: [parentParser],
  });
  const requiredCheckParser = checkParser.add_argument_group('required named arguments');
  requiredCheckParser.add_argument('--config', {
    type: 'str',
    required: true,
    help: 'path to the json configuration file',
  });

  // Accept the discover command
  const discover_parser = subparsers.add_parser('discover', {
    help: "outputs a catalog describing the source's schema",
    parents: [parentParser],
  });
  const requiredDiscoverParser = discover_parser.add_argument_group('required named arguments');
  requiredDiscoverParser.add_argument('--config', {
    type: 'str',
    required: true,
    help: 'path to the json configuration file',
  });

  // Accept the read command
  const readParser = subparsers.add_parser('read', {
    help: 'reads the source and outputs messages to STDOUT',
    parents: [parentParser],
  });
  readParser.add_argument('--state', {
    type: 'str',
    required: false,
    help: 'path to the json-encoded state file',
  });
  const requiredReadParser = readParser.add_argument_group('required named arguments');
  requiredReadParser.add_argument('--config', {
    type: 'str',
    required: true,
    help: 'path to the json configuration file',
  });
  requiredReadParser.add_argument('--catalog', {
    type: 'str',
    required: true,
    help: 'path to the catalog used to determine which data to read',
  });

  const parsedArgs = mainParser.parse_args(args);
  const command = parsedArgs.command;

  if (command === 'spec') {
    spec();
  } else if (command === 'check') {
    const config = readJson(getInputFilePath(parsedArgs.config));
    await check(config);
  } else if (command === 'discover') {
    discover();
  } else if (command === 'read') {
    const config = readJson(getInputFilePath(parsedArgs.config));
    const configuredCatalog = readJson(getInputFilePath(parsedArgs.catalog));
    await read(config, configuredCatalog);
  } else {
    // If we don't recognize the command log the problem and exit with an error code greater than 0 to indicate the process
    // had a failure
    log('Invalid command. Allowable commands: [spec, check, discover, read]');
    process.exit(1);
  }

  // A zero exit code means the process successfully completed
  process.exit(0);
}

(async function () {
  await run(process.argv.slice(2)).catch((reason) => console.log(reason));
})();
