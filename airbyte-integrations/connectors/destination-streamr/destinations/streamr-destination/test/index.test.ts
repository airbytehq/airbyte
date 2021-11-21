import {
  AirbyteConnectionStatus,
  AirbyteConnectionStatusMessage,
  AirbyteSpec,
  AirbyteStateMessage,
} from 'faros-airbyte-cdk';
import fs from 'fs';
import {getLocal} from 'mockttp';
import os from 'os';

import {CLI, read} from './cli';
import {tempConfig} from './temp';
const privateKey =
  '9c9853f5ad682ae1552cf9bb205da37b704bc6d6105a94e190c5727d25e3e6cc';
const streamId = '0x0d0102474519cd2fc1b3e3f962a87e39cbcbead2/test-streamr';

describe('index', () => {
  // const mockttp = getLocal({debug: false, recordTraffic: false});
  let configPath: string;

  beforeEach(async () => {
    // await mockttp.start({startPort: 30000, endPort: 50000});
    configPath = await tempConfig(privateKey, streamId);
  });

  afterEach(async () => {
    // await mockttp.stop();
    fs.unlinkSync(configPath);
  });

  test('help', async () => {
    const cli = await CLI.runWith(['--help']);
    expect(await read(cli.stderr)).toBe('');
    expect(await read(cli.stdout)).toMatch(/^Usage: main*/);
    expect(await cli.wait()).toBe(0);
  });

  test('spec', async () => {
    const cli = await CLI.runWith(['spec']);
    expect(await read(cli.stderr)).toBe('');
    expect(await read(cli.stdout)).toBe(
      JSON.stringify(new AirbyteSpec(require('../resources/spec.json'))) +
        os.EOL
    );
    expect(await cli.wait()).toBe(0);
  });

  test('check', async () => {
    // await mockttp
    //   .get('/users/me')
    //   .once()
    //   .thenReply(200, JSON.stringify({tenantId: '1'}));
    // await mockttp
    //   .get('/graphs/test-graph/statistics')
    //   .once()
    //   .thenReply(200, JSON.stringify({}));

    const cli = await CLI.runWith(['check', '--config', configPath]);

    expect(await read(cli.stderr)).toBe('');
    expect(await read(cli.stdout)).toBe(
      JSON.stringify(
        new AirbyteConnectionStatusMessage({
          status: AirbyteConnectionStatus.SUCCEEDED,
        })
      ) + os.EOL
    );
    expect(await cli.wait()).toBe(0);
  });

  test('indexing', async () => {
    const catalogPath = '../sample_files/configured_catalog.json';
    const recordPath = '../sample_files/records.jsonl';
    const cli = await CLI.runWith([
      'write',
      '--config',
      configPath,
      '--catalog',
      catalogPath,
    ]);
    const records = fs.readFileSync(recordPath);

    cli.stdin.write(records);

    expect(await read(cli.stderr)).toBe('');
    expect(await read(cli.stdout)).toBe(
      JSON.stringify(
        new AirbyteStateMessage({
          data: {
            streamId: '_airbyte_raw_mytestsource__asana__users',
          },
        })
      ) + os.EOL
    );
    expect(await cli.wait()).toBe(0);
  }, 20000);
});
