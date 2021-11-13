using System.Text.Json.Serialization;

namespace Airbyte.Cdk.Models
{
    public class AirbyteLogMessage
    {
        /// <summary>
        /// The type of logging
        /// </summary>
        [JsonPropertyName("level")]
        public Level Level { get; set; }

        /// <summary>
        /// The log message
        /// </summary>
        [JsonPropertyName("message")]
        public string Message { get; set; }
    }
}