using System.Text.Json.Serialization;

namespace Airbyte.Cdk.Models
{
    public class AirbyteConnectionStatus
    {
        [JsonPropertyName("status")]
        public Status Status { get; set; }

        [JsonPropertyName("message")]
        public string? Message { get; set; }
    }
}