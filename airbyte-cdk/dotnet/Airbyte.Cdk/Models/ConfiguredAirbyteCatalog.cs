using System.Text.Json.Serialization;

namespace Airbyte.Cdk.Models
{
    public class ConfiguredAirbyteCatalog
    {
        [JsonPropertyName("streams")]
        public ConfiguredAirbyteStream[] Streams { get; set; }
    }
}