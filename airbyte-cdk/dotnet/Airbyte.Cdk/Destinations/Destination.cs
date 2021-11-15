using System.IO;
using System.Text.Json;
using System.Threading.Tasks;
using Airbyte.Cdk.Models;
using Airbyte.Cdk.Sources.Utils;

namespace Airbyte.Cdk.Destinations
{
    public abstract class Destination : Connector
    {
        public virtual JsonElement ReadState(string statepath) =>
            string.IsNullOrWhiteSpace(statepath) || !File.Exists(statepath)
                ? "".AsJsonElement()
                : JsonDocument.Parse(File.ReadAllText(statepath)).RootElement.Clone();

        public abstract Task Write(AirbyteLogger logger, JsonElement config,
            ConfiguredAirbyteCatalog catalog, AirbyteMessage msg);
    }
}
