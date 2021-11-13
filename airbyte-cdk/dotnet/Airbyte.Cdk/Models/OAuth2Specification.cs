using System.Text.Json.Serialization;

namespace Airbyte.Cdk.Models
{
    public class OAuth2Specification
    {
        /// <summary>
        /// A list of strings representing a pointer to the root object which contains any oauth parameters in the ConnectorSpecification.
        /// </summary>
        [JsonPropertyName("rootObject")]
        public string[]? RootObject { get; set; }

        /// <summary>
        /// Pointers to the fields in the rootObject needed to obtain the initial refresh/access tokens for the OAuth flow. Each inner array represents the path in the rootObject of the referenced field. For example. Assume the rootObject contains params 'app_secret', 'app_id' which are needed to get the initial refresh token.
        /// </summary>
        [JsonPropertyName("oauthFlowInitParameters")]
        public string[][]? OauthFlowInitParameters { get; set; }

        /// <summary>
        /// Pointers to the fields in the rootObject which can be populated from successfully completing the oauth flow using the init parameters. This is typically a refresh/access token. Each inner array represents the path in the rootObject of the referenced field.
        /// </summary>
        [JsonPropertyName("oauthFlowOutputParameters")]
        public string[][]? OauthFlowOutputParameters { get; set; }
    }
}