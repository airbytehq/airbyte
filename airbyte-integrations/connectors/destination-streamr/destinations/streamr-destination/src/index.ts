import {Command} from 'commander';
import {
  AirbyteConfig,
  AirbyteConfiguredCatalog,
  AirbyteConfiguredStream,
  AirbyteConnectionStatus,
  AirbyteConnectionStatusMessage,
  AirbyteDestination,
  AirbyteDestinationRunner,
  AirbyteLogger,
  AirbyteMessageType,
  AirbyteRecord,
  AirbyteSpec,
  AirbyteStateMessage,
  DestinationSyncMode,
  parseAirbyteMessage,
} from 'faros-airbyte-cdk';
import _, {keyBy, sortBy, uniq} from 'lodash';
import readline from 'readline';
import {Writable} from 'stream';
import {Stream, StreamrClient} from 'streamr-client';
import {Dictionary} from 'ts-essentials';
import {VError} from 'verror';

/** The main entry point. */
export function mainCommand(options?: {
  exitOverride?: boolean;
  suppressOutput?: boolean;
}): Command {
  const logger = new AirbyteLogger();
  const destination = new StreamrDestination(logger);
  const destinationRunner = new AirbyteDestinationRunner(logger, destination);
  const program = destinationRunner.mainCommand();

  if (options?.exitOverride) {
    program.exitOverride();
  }
  if (options?.suppressOutput) {
    program.configureOutput({
      // eslint-disable-next-line @typescript-eslint/no-empty-function
      writeOut: () => {},
      // eslint-disable-next-line @typescript-eslint/no-empty-function
      writeErr: () => {},
    });
  }

  return program;
}

export enum InvalidRecordStrategy {
  FAIL = 'FAIL',
  SKIP = 'SKIP',
}

interface WriteStats {
  messagesRead: number;
  recordsRead: number;
  recordsProcessed: number;
  recordsWritten: number;
  recordsErrored: number;
  processedByStream: Dictionary<number>;
  writtenByModel: Dictionary<number>;
}

/** Streamr destination implementation. */
class StreamrDestination extends AirbyteDestination {
  constructor(
    private readonly logger: AirbyteLogger,
    private streamrClient: StreamrClient = undefined,
    private streamr: Stream = undefined,
    private invalidRecordStrategy: InvalidRecordStrategy = InvalidRecordStrategy.SKIP
  ) {
    super();
  }

  getStreamrClient(): StreamrClient {
    if (this.streamrClient) return this.streamrClient;
    throw new VError('Streamr client is not initialized');
  }

  async spec(): Promise<AirbyteSpec> {
    return new AirbyteSpec(require('../resources/spec.json'));
  }

  async check(config: AirbyteConfig): Promise<AirbyteConnectionStatusMessage> {
    // TODO: How to validate that private key is valid?
    try {
      await this.init(config);
    } catch (e: any) {
      return new AirbyteConnectionStatusMessage({
        status: AirbyteConnectionStatus.FAILED,
        message: e.message,
      });
    }

    try {
      const exists = await this.getStreamrClient().getStream(config.streamId);
      if (!exists) {
        throw new VError(`Stream id ${config.streamId} does not exist`);
      }
    } catch (e) {
      return new AirbyteConnectionStatusMessage({
        status: AirbyteConnectionStatus.FAILED,
        message: `Not found stream ${config.streamId}. Error: ${e}`,
      });
    }
    return new AirbyteConnectionStatusMessage({
      status: AirbyteConnectionStatus.SUCCEEDED,
    });
  }

  private async init(config: AirbyteConfig): Promise<void> {
    if (!config.privateKey) {
      throw new VError('Missing private key');
    }

    if (!config.streamId) {
      throw new VError('Missing stream id');
    }
    try {
      this.streamrClient = new StreamrClient({
        auth: {
          privateKey: config.privateKey,
        },
      });

      this.streamr = await this.streamrClient.getStream(config.streamId);
    } catch (e) {
      throw new VError(`Failed to initialize Streamr Client. Error: ${e}`);
    }
  }

  async *write(
    config: AirbyteConfig,
    catalog: AirbyteConfiguredCatalog,
    stdin: NodeJS.ReadStream,
    dryRun: boolean
  ): AsyncGenerator<AirbyteStateMessage> {
    await this.init(config);

    const {streams, deleteModelEntries} =
      this.initStreamsCheckConverters(catalog);

    const stateMessages: AirbyteStateMessage[] = [];

    // Avoid creating a new revision and writer when dry run is enabled
    if (config.dry_run === true || dryRun) {
      this.logger.info("Dry run is ENABLED. Won't write any records");
      await this.writeEntries(config, stdin, streams, stateMessages);
    } else {
      // Log all models to be deleted (if any)
      if (deleteModelEntries.length > 0) {
        // TODO: Handle delete model
        const modelsToDelete = sortBy(deleteModelEntries).join(',');
        this.logger.info(
          `Deleting records in destination graph ${config.graph} for models: ${modelsToDelete}`
        );
      }

      // TODO: Move streamr to instace property
      // const client = await this.getStreamrClient().getOrCreateStream(
      //   config.streamId
      // );
      // client.publish(streams, new Date());
      // TODO: Print writer output

      await this.writeEntries(config, stdin, streams, stateMessages);
    }
    // Since we are writing all records in a single revision,
    // we should be ok to return all the state messages at the end,
    // once the revision has been closed.
    for (const state of stateMessages) yield state;
  }

  private async writeEntries(
    config: AirbyteConfig,
    stdin: NodeJS.ReadStream,
    streams: Dictionary<AirbyteConfiguredStream>,
    stateMessages: AirbyteStateMessage[],
    writer?: Writable
  ): Promise<void> {
    const stats = {
      messagesRead: 0,
      recordsRead: 0,
      recordsProcessed: 0,
      recordsWritten: 0,
      recordsErrored: 0,
      processedByStream: {},
      writtenByModel: {},
    };

    // NOTE: readline.createInterface() will start to consume the input stream once invoked.
    // Having asynchronous operations between interface creation and asynchronous iteration may
    // result in missed lines.
    const input = readline.createInterface({
      input: stdin,
      terminal: stdin.isTTY,
    });
    try {
      // Process input & write records
      for await (const line of input) {
        this.handleRecordProcessingError(stats, () => {
          const msg = parseAirbyteMessage(line);
          stats.messagesRead++;
          if (msg.type === AirbyteMessageType.STATE) {
            stateMessages.push(msg as AirbyteStateMessage);
          } else if (msg.type === AirbyteMessageType.RECORD) {
            stats.recordsRead++;
            const recordMessage = msg as AirbyteRecord;
            if (!recordMessage.record) {
              throw new VError('Empty record');
            }
            // if (!streams[recordMessage.record.stream]) {
            //   throw new VError(
            //     `Undefined stream ${recordMessage.record.stream}`
            //   );
            // }
            const unpacked = recordMessage.unpackRaw();
            if (!unpacked.record) {
              throw new VError('Empty unpacked record');
            }
            const stream = unpacked.record.stream;
            const count = stats.processedByStream[stream];
            stats.processedByStream[stream] = count ? count + 1 : 1;

            const writeRecord = async (context: any): Promise<any> => {
              this.streamr.publish(unpacked.record, Date.now()).then(() => {
                writer?.write(context);
                stats.recordsWritten++;
                stats.recordsProcessed++;
              });
            };

            writeRecord(unpacked)
              .then()
              .catch((error) => {
                throw new VError('Error sync record');
              });
          }
        });
      }
    } finally {
      this.logWriteStats(stats, writer);
      input.close();
    }
  }

  private logWriteStats(stats: WriteStats, writer?: Writable): void {
    this.logger.info(`Read ${stats.messagesRead} messages`);
    this.logger.info(`Read ${stats.recordsRead} records`);
    this.logger.info(`Processed ${stats.recordsProcessed} records`);
    const processed = _(stats.processedByStream)
      .toPairs()
      .orderBy(0, 'asc')
      .fromPairs()
      .value();
    this.logger.info(
      `Processed records by stream: ${JSON.stringify(processed)}`
    );
    const writeMsg = writer ? 'Wrote' : 'Would write';
    this.logger.info(`${writeMsg} ${stats.recordsWritten} records`);
    const written = _(stats.writtenByModel)
      .toPairs()
      .orderBy(0, 'asc')
      .fromPairs()
      .value();
    this.logger.info(
      `${writeMsg} records by model: ${JSON.stringify(written)}`
    );
    this.logger.info(`Errored ${stats.recordsErrored} records`);
  }

  private handleRecordProcessingError(
    stats: WriteStats,
    processRecord: () => void
  ): void {
    try {
      processRecord();
    } catch (e: any) {
      stats.recordsErrored++;
      this.logger.error(
        `Error processing input: ${e.message ?? JSON.stringify(e)}`
      );
      if (this.invalidRecordStrategy === InvalidRecordStrategy.FAIL) {
        throw e;
      }
    }
  }

  private initStreamsCheckConverters(catalog: AirbyteConfiguredCatalog): {
    streams: Dictionary<AirbyteConfiguredStream>;
    deleteModelEntries: ReadonlyArray<string>;
  } {
    const streams = keyBy(catalog.streams, (s) => s.stream.name);
    const streamKeys = Object.keys(streams);
    const deleteModelEntries: string[] = [];

    // Check input streams & initialize record converters
    // TODO: Check on destination sync mode
    // for (const stream of streamKeys) {
    //   const destinationSyncMode = streams[stream].destination_sync_mode;
    //   if (!destinationSyncMode) {
    //     throw new VError(
    //       `Undefined destination sync mode for stream ${stream}`
    //     );
    //   }

    //   // Prepare destination models to delete if any
    //   if (destinationSyncMode === DestinationSyncMode.OVERWRITE) {
    //     // TODO: PUSH TO delete list
    //     // deleteModelEntries.push(...converter.destinationModels);
    //   }
    // }

    return {
      streams,
      deleteModelEntries: uniq(deleteModelEntries),
    };
  }
}
