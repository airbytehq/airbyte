using System.Text.Json.Serialization;

namespace Airbyte.Cdk.Models
{
    public class AirbyteMessage
    {
        /// <summary>
        /// Message type
        /// </summary>
        [JsonPropertyName("type")]
        public Type Type { get; set; }

        /// <summary>
        /// Log message: any kind of logging you want the platform to know about.
        /// </summary>
        [JsonPropertyName("log")]
        public AirbyteLogMessage Log { get; set; }

        [JsonPropertyName("spec")]
        public ConnectorSpecification? Spec { get; set; }

        [JsonPropertyName("connectionStatus")]
        public AirbyteConnectionStatus? ConnectionStatus { get; set; }

        /// <summary>
        /// Log message: any kind of logging you want the platform to know about.
        /// </summary>
        [JsonPropertyName("catalog")]
        public AirbyteCatalog? Catalog { get; set; }

        /// <summary>
        /// Record message: the record
        /// </summary>
        [JsonPropertyName("record")]
        public AirbyteRecordMessage? Record { get; set; }

        /// <summary>
        /// schema message: the state. Must be the last message produced. The platform uses this information
        /// </summary>
        [JsonPropertyName("state")]
        public AirbyteStateMessage? State { get; set; }
    }
}