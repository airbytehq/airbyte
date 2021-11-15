using System;
using System.Collections.Generic;
using System.Linq;
using Airbyte.Cdk.Sources.Utils;
using Flurl.Http;

namespace Airbyte.Cdk.Sources.Streams.Http.Auth
{
    public class OAuth : AuthBase
    {

        public string TokenRefreshEndpoint { get; }

        public string ClientId { get; }

        public string ClientSecret { get; }

        public string RefreshToken { get; }

        public string ExpiresInName { get; }

        public string AccessTokenName { get; }

        private string AccessToken { get; set; }

        public DateTime? TokenExpiry { get; private set; }

        public IEnumerable<string> Scopes { get; }

        public OAuth(string tokenrefreshendpoint, string clientid, string clientsecret, string refreshtoken,
            IEnumerable<string> scopes = null, DateTime? tokenexpiry = null, string accesstokenname = "",
            string expiresinname = "")
        {
            TokenRefreshEndpoint = tokenrefreshendpoint;
            ClientId = clientid;
            ClientSecret = clientsecret;
            RefreshToken = refreshtoken;
            Scopes = scopes ?? new List<string>();
            TokenExpiry = tokenexpiry;
            AccessTokenName = accesstokenname;
            ExpiresInName = expiresinname;
        }

        public string GetAccessToken()
        {
            if (TokenHasExpired())
                (AccessToken, TokenExpiry) = RefreshAccessToken();

            return AccessToken;
        }

        public bool TokenHasExpired() => !TokenExpiry.HasValue || DateTime.UtcNow > TokenExpiry;

        /// <summary>
        /// Override to define additional parameters
        /// </summary>
        /// <returns></returns>
        public virtual string GetRefreshRequestBody()
        {
            Dictionary<string, object> payload = new()
            {
                { "grant_type", "refresh_token" },
                { "client_id", ClientId },
                { "client_secret", ClientSecret },
                { "refresh_token", RefreshToken }
            };

            if (Scopes.Any())
                payload["scopes"] = Scopes;

            return payload.AsJsonElement().GetRawText();
        }

        public virtual (string, DateTime) RefreshAccessToken()
        {
            try
            {
                var response = TokenRefreshEndpoint.PostJsonAsync(GetRefreshRequestBody()).Result;
                var json = response.GetJsonAsync().Result;
                return (json[AccessTokenName], DateTime.Parse(json[ExpiresInName]));
            }
            catch (Exception e)
            {
                throw new Exception($"Error while refreshing access token: {e.Message}");
            }
        }
    }

    public static class OauthFlurlRequestExtension
    {
        public static IFlurlRequest WithOauth(this IFlurlRequest request, OAuth auth) =>
            request.WithOAuthBearerToken(auth.GetAccessToken());
    }
}
