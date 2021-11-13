using System.Text.Json;
using System.Text.Json.Serialization;

namespace Airbyte.Cdk.Models
{
    public class ConnectorSpecification
    {
        [JsonPropertyName("documentationUrl")]
        public string? DocumentationUrl { get; set; }

        [JsonPropertyName("changelogUrl")]
        public string? ChangelogUrl { get; set; }

        /// <summary>
        /// ConnectorDefinition specific blob. Must be a valid JSON string.
        /// </summary>
        [JsonPropertyName("connectionSpecification")]
        public JsonDocument ConnectionSpecification { get; set; }

        /// <summary>
        /// If the connector supports incremental mode or not.
        /// </summary>
        [JsonPropertyName("supportsIncremental")]
        public bool? SupportsIncremental { get; set; }

        /// <summary>
        /// If the connector supports normalization or not.
        /// </summary>
        [JsonPropertyName("supportsNormalization")]
        public bool? SupportsNormalization { get; set; }

        /// <summary>
        /// If the connector supports DBT or not.
        /// </summary>
        [JsonPropertyName("supportsDBT")]
        public bool? SupportsDBT { get; set; }

        /// <summary>
        /// List of destination sync modes supported by the connector
        /// </summary>
        [JsonPropertyName("supported_destination_sync_modes")]
        public DestinationSyncMode[]? SupportedDestinationSyncModes { get; set; }

        [JsonPropertyName("authSpecification")]
        public AuthSpecification? AuthSpecification { get; set; }
    }
}