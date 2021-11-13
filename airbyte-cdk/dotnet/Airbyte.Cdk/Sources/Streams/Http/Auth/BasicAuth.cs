using System.Linq;
using Flurl.Http;

namespace Airbyte.Cdk.Sources.Streams.Http.Auth
{
    public class BasicAuth : AuthBase
    {
        public BasicAuth(string[] tokens, string authmethod = "Bearer", string authheader = "Authorization")
        {
            Tokens = tokens;
            AuthMethod = authmethod;
            AuthHeader = authheader;
        }

        public string AuthHeader { get; }

        public string AuthMethod { get; }

        public string[] Tokens { get; }

        public IFlurlRequest GetAuthHeader(IFlurlRequest request)
            => request.WithHeader(AuthHeader, $"{AuthMethod} {Tokens.Aggregate((current, next) => current + " " + next)}");
    }

    public static class BasicAuthFlurlRequestExtension
    {
        public static IFlurlRequest WithBasicAuth(this IFlurlRequest request, BasicAuth auth) =>
            auth.GetAuthHeader(request);
    }
}
