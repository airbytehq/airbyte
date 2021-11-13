using System.Text.Json;
using System.Text.Json.Serialization;

namespace Airbyte.Cdk.Models
{
    public class AirbyteStateMessage
    {
        /// <summary>
        /// The state data
        /// </summary>
        [JsonPropertyName("data")]
        public JsonDocument Data { get; set; }
    }
}