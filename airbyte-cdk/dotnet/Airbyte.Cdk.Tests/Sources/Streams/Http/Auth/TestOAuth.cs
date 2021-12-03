using System;
using Airbyte.Cdk.Sources.Streams.Http.Auth;
using FluentAssertions;
using Flurl;
using Flurl.Http;
using Moq;
using Xunit;

namespace Airbyte.Cdk.Tests.Sources.Streams.Http.Auth
{
    public class TestOAuth
    {
        private string _refreshEndpoint = "https://some_url.com/v1";
        private string _clientId = "client_id";
        private string _clientSecret = "client_secret";
        private string _refreshToken = "refresh_token";

        [Fact]
        public void TestGetAuthHeaderFresh()
        {
            //Should not retrieve new token if current token is valid.
            var system = new Mock<OAuth>(_refreshEndpoint, _clientId, _clientSecret, _refreshToken, null, null, "", "");
            system.CallBase = true;
            system.Setup(x => x.RefreshAccessToken()).Returns(() =>
                ("access_token", DateTime.UtcNow + TimeSpan.FromSeconds(1000)));
            var request = new Mock<FlurlRequest>(() => new FlurlRequest(Url.Parse("airbyte.io")));
            request.CallBase = true;


            request.Object.WithOauth(system.Object);

            request.Object.Headers.Count.Should().Be(1);
            request.Object.Headers[0].Name.Should().Be("Authorization");
            request.Object.Headers[0].Value.Should().Be("Bearer access_token");
        }

        [Fact]
        public void TestGetAuthHeaderExpired()
        {
            //Should not retrieve new token if current token is valid.
            var system = new Mock<OAuth>(_refreshEndpoint, _clientId, _clientSecret, _refreshToken, null, null, "", "");
            system.CallBase = true;
            system.Setup(x => x.RefreshAccessToken()).Returns(() =>
                ("access_token_1", DateTime.UtcNow - TimeSpan.FromSeconds(1000)));
            var request = new Mock<FlurlRequest>(() => new FlurlRequest(Url.Parse("airbyte.io")));
            request.CallBase = true;

            //First expired
            request.Object.WithOauth(system.Object);
            system.Object.TokenHasExpired().Should().BeTrue();

            //Second, not expired
            system.Setup(x => x.RefreshAccessToken()).Returns(() =>
                ("access_token_2", DateTime.UtcNow + TimeSpan.FromSeconds(1000)));
            request.Object.WithOauth(system.Object);

            system.Object.TokenHasExpired().Should().BeFalse();
            request.Object.Headers.Count.Should().Be(1);
            request.Object.Headers[0].Name.Should().Be("Authorization");
            request.Object.Headers[0].Value.Should().Be("Bearer access_token_2");
        }

        [Fact]
        public void TestRefreshRequestBody()
        {
            //Should not retrieve new token if current token is valid.
            var scopes = new[] {"scope1", "scope2"};
            var system = new Mock<OAuth>(_refreshEndpoint, _clientId, _clientSecret, _refreshToken, scopes, null, "", "");
            system.CallBase = true;

            var result = system.Object.GetRefreshRequestBody();

            result.Should().NotBeNullOrWhiteSpace();
            var expected =
                "{\"grant_type\":\"refresh_token\",\"client_id\":\"client_id\",\"client_secret\":\"client_secret\",\"refresh_token\":\"refresh_token\",\"scopes\":[\"scope1\",\"scope2\"]}";
            result.Should().Be(expected);
        }

        [Fact(Skip = "Not Implemented")]
        public void TestRefreshAccessToken()
        {

        }
    }
}
