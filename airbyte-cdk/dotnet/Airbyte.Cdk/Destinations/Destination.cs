using System.IO;
using System.Text.Json;
using System.Threading.Tasks;
using Airbyte.Cdk.Models;

namespace Airbyte.Cdk.Destinations
{
    public abstract class Destination : Connector
    {
        public virtual JsonDocument ReadState(string statepath) =>
            string.IsNullOrWhiteSpace(statepath) || !File.Exists(statepath)
                ? null
                : JsonDocument.Parse(File.ReadAllText(statepath));

        public abstract Task Write(AirbyteLogger logger, JsonDocument config,
            ConfiguredAirbyteCatalog catalog, AirbyteMessage msg);
    }
}
