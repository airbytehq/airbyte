using System.Text.Json.Serialization;

namespace Airbyte.Cdk.Models
{
    public class AuthSpecification
    {
        /// <summary>
        /// Auth type to make use of
        /// </summary>
        [JsonPropertyName("auth_type")]
        public AuthType? AuthType { get; set; }

        /// <summary>
        /// If the connector supports OAuth, this field should be non-null.
        /// </summary>
        [JsonPropertyName("oauth2Specification")]
        public OAuth2Specification? OAuth2Specification { get; set; }
    }
}