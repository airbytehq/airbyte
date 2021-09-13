package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuthFlow;
import java.io.IOException;
import java.util.Map;
import java.util.UUID;

/**
 * Following docs from https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow
 */
public class FacebookMarketingOAuthFlow extends BaseOAuthFlow {

  private final String consentUrl = "https://www.facebook.com/v11.0/dialog/oauth";
  private final String accessTokenUrl = "https://graph.facebook.com/v11.0/oauth/access_token";

  public FacebookMarketingOAuthFlow(ConfigRepository configRepository) {
    super(configRepository);
  }

  @Override
  protected String getBaseConsentUrl() {
    return consentUrl;
  }

  @Override
  protected Map<String, String> getConsentQueryParameters(UUID definitionId, String clientId, String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        // required
        .put("client_id", clientId)
        .put("redirect_uri", redirectUrl)
        .put("state", getState(definitionId))
        // optional
        .put("response_type", "code")
        .put("scope", "ads_management,ads_read,read_insights")
        .build();
  }

  @Override
  protected String extractCodeParameter(Map<String, Object> queryParams) throws IOException {
    if (queryParams.containsKey("code")) {
      return (String) queryParams.get("code");
    } else {
      throw new IOException("Undefined 'code' from consent redirected url.");
    }
  }

  @Override
  protected String getAccessTokenUrl() {
    return accessTokenUrl;
  }

  @Override
  protected Map<String, String> getAccessTokenQueryParameters(String clientId, String clientSecret, String authCode, String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        // required
        .put("client_id", clientId)
        .put("redirect_uri", redirectUrl)
        .put("client_secret", clientSecret)
        .put("code", authCode)
        .build();
  }

  @Override
  protected Map<String, Object> extractRefreshToken(JsonNode data) throws IOException {
    if (data.has("access_token")) {
      return Map.of("access_token", data.get("access_token").asText());
    } else {
      throw new IOException(String.format("Missing 'access_token' in query params from %s", accessTokenUrl));
    }
  }
}
