using System.Text.Json;
using System.Text.Json.Serialization;

namespace Airbyte.Cdk.Models
{
    public class AirbyteRecordMessage
    {
        /// <summary>
        /// The name of this record's stream
        /// </summary>
        [JsonPropertyName("stream")]
        public string Stream { get; set; }

        /// <summary>
        /// The record data
        /// </summary>
        [JsonPropertyName("data")]
        public JsonDocument Data { get; set; }

        /// <summary>
        /// When the data was emitted from the source. epoch in millisecond.
        /// </summary>
        [JsonPropertyName("emitted_at")]
        public long EmittedAt { get; set; }

        /// <summary>
        /// The namespace of this record's stream
        /// </summary>
        [JsonPropertyName("namespace")]
        public string? Namespace { get; set; }
    }
}