using System;
using System.Linq;
using System.Text.Json;
using System.Threading.Channels;
using System.Threading.Tasks;
using Airbyte.Cdk.Models;
using Airbyte.Cdk.Sources.Streams;
using Airbyte.Cdk.Sources.Streams.Http;
using Airbyte.Cdk.Sources.Utils;
using Type = Airbyte.Cdk.Models.Type;

namespace Airbyte.Cdk.Sources
{
    /// <summary>
    /// Abstract base class for an Airbyte Source. Consumers should implement any abstract methods
    /// in this class to create an Airbyte Specification compliant Source.
    /// </summary>
    public abstract class AbstractSource : Source
    {
        protected AirbyteLogger Logger { get; private set; }

        protected ChannelWriter<AirbyteMessage> Channel { get; private set; }

        protected JsonElement Config { get; private set; }

        protected JsonElement State { get; private set; }

        protected ConfiguredAirbyteCatalog Catalog { get; private set; }

        /// <summary>
        /// Check if a connection can be established
        /// </summary>
        /// <param name="logger"></param>
        /// <param name="config">The user-provided configuration as specified by the source's spec. This usually contains information required to check connection e.g. tokens, secrets and keys etc.</param>
        /// <returns>A Dictionary of (boolean, error). If boolean is true, then the connection check is successful and we can connect to the underlying data
        /// source using the provided configuration.</returns>
        public abstract bool CheckConnection(AirbyteLogger logger, JsonElement config, out Exception exc);

        /// <summary>
        /// An array of the streams in this source connector.
        /// </summary>
        /// <param name="config">The user-provided configuration as specified by the source's spec. Any stream construction related operation should happen here.</param>
        /// <returns></returns>
        public abstract Stream[] Streams(JsonElement config);

        public string Name
        {
            get => GetType().Name;
        }

        /// <summary>
        /// Implements the Discover operation from the Airbyte Specification. See https://docs.airbyte.io/architecture/airbyte-specification.
        /// </summary>
        /// <param name="logger"></param>
        /// <param name="config"></param>
        /// <returns></returns>
        public override AirbyteCatalog Discover(AirbyteLogger logger, JsonElement config)
            => new() { Streams = Streams(config).Select(x => x.AsAirbyteStream()).ToArray() };

        /// <summary>
        /// Implements the Check Connection operation from the Airbyte Specification. See https://docs.airbyte.io/architecture/airbyte-specification.
        /// </summary>
        /// <param name="logger"></param>
        /// <param name="config"></param>
        /// <returns></returns>
        public override AirbyteConnectionStatus Check(AirbyteLogger logger, JsonElement config)
        {
            try
            {
                return CheckConnection(logger, config, out var exc)
                    ? new AirbyteConnectionStatus { Status = Status.SUCCEEDED }
                    : throw exc;
            }
            catch (Exception e)
            {
                return new AirbyteConnectionStatus { Status = Status.FAILED, Message = e.Message };
            }
        }

        /// <summary>
        /// Implements the Read operation from the Airbyte Specification. See https://docs.airbyte.io/architecture/airbyte-specification.
        /// </summary>
        /// <param name="logger"></param>
        /// <param name="channel"></param>
        /// <param name="config"></param>
        /// <param name="catalog"></param>
        /// <param name="state"></param>
        /// <returns></returns>
        public override async Task Read(AirbyteLogger logger, ChannelWriter<AirbyteMessage> channel,
            JsonElement config,
            ConfiguredAirbyteCatalog catalog, JsonElement state)
        {
            //Set values
            Logger = logger;
            Channel = channel;
            Config = config;
            Catalog = catalog;
            State = state;

            logger.Info($"Starting syncing {Name}");
            var streamsInstances = Streams(config);
            foreach (var configuredStream in catalog.Streams)
            {
                var streamInstance = streamsInstances.FirstOrDefault(x => x.Name == configuredStream.Stream.Name);
                if (streamInstance == null)
                    throw new Exception(
                        $"The requested stream {configuredStream.Stream.Name} was not found in the source. Available streams: {streamsInstances.Select(x => x.Name)}");

                try
                {
                    await ReadStream(logger, streamInstance, configuredStream);
                }
                catch (Exception e)
                {
                    logger.Exception(e);
                    logger.Fatal($"Fatal exception occurred during ReadStream: {e.Message}");
                    throw;
                }
            }
        }

        private async Task ReadStream(AirbyteLogger logger, Stream streaminstance, ConfiguredAirbyteStream configuredstream)
        {
            if (Config.TryGetProperty("_page_size", out var pagesizeElement) &&
                streaminstance is HttpStream stream && pagesizeElement.TryGetInt32(out int pagesize))
            {
                Logger.Info($"Setting page size for {Name} to {pagesize}");
                stream.PageSize = pagesize;
            }

            long recordcount;
            long? recordlimit = Config.TryGetProperty("_limit", out var limitElement) && limitElement.TryGetInt64(out var limit) ? limit : null;
            Logger.Info($"Syncing stream: {streaminstance.Name}");

            var streamname = configuredstream.Stream.Name;
            if (State.TryGetProperty(streamname, out var stateElement))
                Logger.Info($"Setting state of {streamname} stream to {stateElement}");
            else
                stateElement = "{}".AsJsonElement();

            if (configuredstream.SyncMode == SyncMode.incremental && streaminstance.SupportsIncremental)
                recordcount = await ReadIncremental(logger, streaminstance, configuredstream, stateElement, recordlimit);
            else
                recordcount = await streaminstance.ReadRecords(logger, SyncMode.full_refresh, Channel, stateElement, recordlimit,
                    configuredstream.CursorField, null);

            Logger.Info($"Read {recordcount} records from {streaminstance.Name} stream");
        }

        private async Task<long> ReadIncremental(AirbyteLogger logger, Stream streaminstance, ConfiguredAirbyteStream configuredstream, JsonElement stateElement, long? recordlimit = null)
        {
            var slices = streaminstance.StreamSlices(SyncMode.incremental, configuredstream.CursorField, stateElement);
            return await streaminstance.ReadRecords(logger, SyncMode.incremental, Channel, stateElement, recordlimit, null, slices);
        }

        public static AirbyteMessage AsAirbyteMessage(string streamname, JsonElement data) => new()
        {
            Type = Type.RECORD,
            Record = new()
            {
                EmittedAt = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds(),
                Data = data,
                Stream = streamname
            }
        };
    }
}
