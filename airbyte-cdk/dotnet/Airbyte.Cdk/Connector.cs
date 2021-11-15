using System.IO;
using System.Text.Json;
using Airbyte.Cdk.Models;

namespace Airbyte.Cdk
{
    public abstract class Connector
    {
        /// <summary>
        /// Persist config in temporary directory to run the Source job
        /// </summary>
        /// <param name="config"></param>
        /// <param name="tempdir"></param>
        /// <returns></returns>
        public virtual JsonElement Configure(JsonElement config, string tempdir)
        {
            var configpath = Path.Join(tempdir, "config.json");
            WriteConfig(config, configpath);
            return config;
        }

        /// <summary>
        /// Returns the spec for this integration. The spec is a JSON-Schema object describing the required configurations (e.g: username and password) required to run this integration.
        /// </summary>
        /// <returns></returns>
        public virtual ConnectorSpecification Spec()
        {
            var filepath = Path.Join(Path.GetDirectoryName(AirbyteEntrypoint.AirbyteImplPath), "spec.json");
            if (!File.Exists(filepath))
                throw new FileNotFoundException("Unable to find spec.json");
            var rawspec = ReadConfig(filepath);
            return JsonSerializer.Deserialize<ConnectorSpecification>(rawspec.GetRawText());
        }

        public static void WriteConfig(JsonElement config, string configpath) => File.WriteAllText(configpath, config.GetRawText());

        public static JsonElement ReadConfig(string configpath) => JsonDocument.Parse(File.ReadAllText(configpath)).RootElement.Clone();

        /// <summary>
        /// Tests if the input configuration can be used to successfully connect to the integration e.g: if a provided Stripe API token can be used to connect to the Stripe API.
        /// </summary>
        /// <param name="logger"></param>
        /// <param name="config"></param>
        /// <returns></returns>
        public abstract AirbyteConnectionStatus Check(AirbyteLogger logger, JsonElement config);
    }
}
