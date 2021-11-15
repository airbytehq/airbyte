using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.Unicode;
using System.Threading.Channels;
using System.Threading.Tasks;
using Airbyte.Cdk.Destinations;
using Airbyte.Cdk.Models;
using Airbyte.Cdk.Sources;
using Airbyte.Cdk.Sources.Utils;
using CommandLine;
using Type = Airbyte.Cdk.Models.Type;

namespace Airbyte.Cdk
{
    public class AirbyteEntrypoint
    {
        static Connector Connector { get; set; }

        static Options Options { get; set; }

        static AirbyteLogger Logger { get; } = new();

        public static string AirbyteImplPath
        {
            get => Environment.GetEnvironmentVariable("AIRBYTE_IMPL_PATH");
        }

        public static async Task Main(string[] args)
        {
            Console.OutputEncoding = Encoding.UTF8;
            Console.InputEncoding = Encoding.UTF8;

            Parser.Default.ParseArguments<ReadOptions, WriteOptions>(args)
                .WithParsed<ReadOptions>(options => Options = options)
                .WithParsed<WriteOptions>(options => Options = options)
                .WithNotParsed(_ => Environment.Exit(1));

            string implModule = Environment.GetEnvironmentVariable("AIRBYTE_IMPL_MODULE");

            if (!File.Exists(AirbyteImplPath))
                throw new FileNotFoundException($"Cannot find implementation binary {AirbyteImplPath}");

            var implementation = Assembly.LoadFile(AirbyteImplPath).GetTypes().Where(x => typeof(Connector).IsAssignableFrom(x) && !x.IsAbstract && !x.IsInterface)
                .FirstOrDefault(x => x.Name.Equals(implModule, StringComparison.OrdinalIgnoreCase));

            if (implementation == null)
                throw new Exception("Source implementation not found!");
            if (Activator.CreateInstance(implementation) is not Connector instance)
                throw new Exception("Implementation provided does not implement Connector class!");

            Connector = instance;
            try
            {
                await Launch();
            }
            catch (Exception e)
            {
                Logger.Fatal($"Exception ({e.GetType()}): {e.Message}");
            }
        }

        private static Source GetSource()
        {
            if (Connector is not Source source)
                throw new Exception($"Could not instantiate Source as current type ({Connector.GetType().Name}) is not implementing {nameof(Source)}");
            return source;
        }

        private static Destination GetDestination()
        {
            if (Connector is not Destination destination)
                throw new Exception($"Could not instantiate Destination as current type ({Connector.GetType().Name}) is not implementing {nameof(Destination)}");
            return destination;
        }

        private static async Task Launch()
        {
            var spec = Connector.Spec();
            
            switch (Options.Command.ToLowerInvariant())
            {
                case "spec":
                    ToConsole(new AirbyteMessage
                    {
                        Type = Type.SPEC,
                        Spec = spec
                    });
                    break;
                case "check":
                    var result = Connector.Check(Logger, GetConfig(spec));
                    if (result.Status == Status.SUCCEEDED) Logger.Info("Check succeeded");
                    else Logger.Error("Check failed");
                    ToConsole(new AirbyteMessage
                    {
                        Type = Type.CONNECTION_STATUS,
                        ConnectionStatus = result
                    });
                    break;
                case "discover":
                    ToConsole(new AirbyteMessage
                    {
                        Type = Type.CATALOG,
                        Catalog = GetSource().Discover(Logger, GetConfig(spec))
                    });
                    break;
                case "read":
                    Channel<AirbyteMessage> readerChannel = Channel.CreateUnbounded<AirbyteMessage>();
                    var readOptions = Options as ReadOptions;
                    var readtasks = new[]
                    {
                        Task.Run(async () =>
                        {
                            var writer = readerChannel.Writer;
                            var source = GetSource();
                            var state = GetState(source, readOptions);
                            var config = GetConfig(spec);
                            var catalog = GetCatalog();
                            try
                            {
                                await source.Read(Logger, writer, config, catalog, state);
                            }
                            catch (Exception e)
                            {
                                Logger.Exception(e);
                                Logger.Fatal("Could not process data due to exception: " + e.Message);
                            }

                            //Set to complete!
                            writer.Complete();
                        }),
                        Task.Run(async () =>
                        {
                            await foreach (var msg in readerChannel.Reader.ReadAllAsync())
                                ToConsole(msg);
                        })
                    };

                    Task.WaitAll(readtasks);
                    break;
                case "write":
                    Channel<AirbyteMessage> writerChannel = Channel.CreateUnbounded<AirbyteMessage>();
                    var writetasks = new[]
                    {
                        Task.Run(async () =>
                        {
                            var writer = writerChannel.Writer;
                            while (true) // Loop forever, no state end message?
                            {
                                var text = await Console.In.ReadLineAsync();
                                if (TryGetAirbyteMessage(text, out var msg))
                                    await writer.WriteAsync(msg);
                            }
                        }),
                        Task.Run(async () =>
                        {
                            var destination = GetDestination();
                            await foreach (var msg in writerChannel.Reader.ReadAllAsync())
                                await destination.Write(Logger, GetConfig(spec),
                                    JsonSerializer.Deserialize<ConfiguredAirbyteCatalog>(Options.Catalog), msg);
                        })
                    };

                    Task.WaitAll(writetasks);
                    break;
                default:
                    throw new NotImplementedException($"Unexpected command: {Options.Command}");
            }
        }

        private static bool TryGetAirbyteMessage(string input, out AirbyteMessage msg)
        {
            msg = null;
            try
            {
                msg = JsonSerializer.Deserialize<AirbyteMessage>(input);
                return true;
            }
            catch
            {
                //TODO: do some logging?
            }

            return false;
        }

        private static JsonElement GetConfig(ConnectorSpecification spec)
        {
            var contents = string.IsNullOrWhiteSpace(Options.Config) ? throw new Exception("Config is undefined!")
                : !TryGetPath(Options.Config, out var filepath) ? throw new FileNotFoundException("Could not find config file: " + filepath)
                : File.ReadAllText(filepath);

            if (string.IsNullOrWhiteSpace(contents))
                throw new Exception("Config file is empty!");

            var toreturn = contents.AsJsonElement();

            if (!ResourceSchemaLoader.TryCheckConfigAgainstSpecOrExit(toreturn, spec, out var exc))
                throw new Exception($"Config does not match spec schema: {exc.Message}");

            Logger.Info($"Found config file at location: {filepath}");
            //Logger.Debug($"Config file contents: {toreturn.RootElement}");

            return toreturn;
        }

        private static ConfiguredAirbyteCatalog GetCatalog()
        {
            if (TryGetPath(Options.Catalog, out var filepath))
            {
                Logger.Info($"Found catalog at location: {filepath}");
                var contents = File.ReadAllText(filepath);
                //Logger.Debug($"Catalog file contents: {contents}");
                return JsonSerializer.Deserialize<ConfiguredAirbyteCatalog>(contents,
                    new JsonSerializerOptions
                    {
                        Converters = { new JsonStringEnumConverter() }
                    });
            }
            else throw new FileNotFoundException("Cannot find catalog file: " + filepath);
        }

        private static JsonElement GetState(Source source, ReadOptions readoptions)
        {
            if (TryGetPath(readoptions.State, out var filepath))
                Logger.Info($"Found state file at location: {filepath}");
            else
                Logger.Warn($"Could not find state file, config reported state file location: {readoptions.State}");

            var contents = source.ReadState(filepath);
            Logger.Debug($"State file contents: {contents.GetRawText()}");
            return contents;
        }

        public static bool TryGetPath(string filename, out string filepath)
        {
            filepath = string.Empty;
            if (string.IsNullOrWhiteSpace(filename))
                return false;
            foreach (var path in new[] { Path.Join(Path.GetDirectoryName(AirbyteImplPath), filename), filename, Path.Join(Directory.GetCurrentDirectory(), filename) })
                if (File.Exists(path))
                {
                    filepath = path;
                    break;
                }

            return !string.IsNullOrWhiteSpace(filepath);
        }

        public static void ToConsole<T>(T item) where T : AirbyteMessage =>
            Console.WriteLine(Encoding.UTF8.GetString(JsonSerializer.SerializeToUtf8Bytes(item, new JsonSerializerOptions
            {
                WriteIndented = false,
                IgnoreNullValues = true,
                Converters = { new JsonStringEnumConverter() },
                Encoder = JavaScriptEncoder.Create(UnicodeRanges.All)
            })));

    }
}


