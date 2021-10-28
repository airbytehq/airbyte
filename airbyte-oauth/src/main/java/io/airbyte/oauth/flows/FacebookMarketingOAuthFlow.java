/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuthFlow;
import java.io.IOException;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.http.client.utils.URIBuilder;

/**
 * Following docs from
 * https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow
 */
public class FacebookMarketingOAuthFlow extends BaseOAuthFlow {

  private static final String ACCESS_TOKEN_URL = "https://graph.facebook.com/v11.0/oauth/access_token";

  public FacebookMarketingOAuthFlow(final ConfigRepository configRepository) {
    super(configRepository);
  }

  @VisibleForTesting
  FacebookMarketingOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String formatConsentUrl(final UUID definitionId, final String clientId, final String redirectUrl) throws IOException {
    final URIBuilder builder = new URIBuilder()
        .setScheme("https")
        .setHost("www.facebook.com")
        .setPath("v11.0/dialog/oauth")
        // required
        .addParameter("client_id", clientId)
        .addParameter("redirect_uri", redirectUrl)
        .addParameter("state", getState())
        // optional
        .addParameter("response_type", "code")
        .addParameter("scope", "ads_management,ads_read,read_insights");
    try {
      return builder.build().toString();
    } catch (final URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  @Override
  protected String getAccessTokenUrl() {
    return ACCESS_TOKEN_URL;
  }

  @Override
  protected Map<String, Object> extractRefreshToken(final JsonNode data, String accessTokenUrl) throws IOException {
    // Facebook does not have refresh token but calls it "long lived access token" instead:
    // see https://developers.facebook.com/docs/facebook-login/access-tokens/refreshing
    if (data.has("access_token")) {
      return Map.of("access_token", data.get("access_token").asText());
    } else {
      throw new IOException(String.format("Missing 'access_token' in query params from %s", ACCESS_TOKEN_URL));
    }
  }

}
