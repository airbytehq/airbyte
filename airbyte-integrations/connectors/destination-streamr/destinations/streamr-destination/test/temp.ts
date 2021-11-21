import fs from 'fs';
import {AffixOptions, open, track} from 'temp';
import {Dictionary} from 'ts-essentials';

import {InvalidRecordStrategy} from '../src';

// Automatically track and cleanup temp files at exit
// TODO: this does not seem to work - figure out what's wrong
track();

/**
 * Creates a temporary file
 * @return path to the temporary file
 */
export async function tempFile(
  data: string,
  opts?: AffixOptions
): Promise<string> {
  const file = await open(opts);
  fs.writeSync(file.fd, data, null, 'utf-8');
  return file.path;
}

/**
 * Creates a temporary file with testing configuration
 * @return path to the temporary config file
 */
export async function tempConfig(
  privateKey: string,
  streamId: string,
  invalid_record_strategy: InvalidRecordStrategy = InvalidRecordStrategy.SKIP,
  source_specific_configs?: Dictionary<any>
): Promise<string> {
  const conf = {
    privateKey,
    streamId,
    invalid_record_strategy,
    source_specific_configs,
  };
  return tempFile(JSON.stringify(conf), {suffix: '.json'});
}
