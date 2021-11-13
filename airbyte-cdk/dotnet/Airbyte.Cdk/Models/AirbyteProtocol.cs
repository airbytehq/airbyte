using System.Text.Json.Serialization;

namespace Airbyte.Cdk.Models
{
    public class AirbyteProtocol
    {
        [JsonPropertyName("airbyte_message")]
        public AirbyteMessage? AirbyteMessage { get; set; }

        [JsonPropertyName("configured_airbyte_catalog")]
        public ConfiguredAirbyteCatalog? ConfiguredAirbyteCatalog { get; set; }
    }
}