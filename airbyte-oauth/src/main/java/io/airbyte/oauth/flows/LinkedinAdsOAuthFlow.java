/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuth2Flow;
import java.io.IOException;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.http.client.utils.URIBuilder;

public class LinkedinAdsOAuthFlow extends BaseOAuth2Flow {

  private static final String AUTHORIZE_URL = "https://www.linkedin.com/oauth/v2/authorization";
  private static final String ACCESS_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken";
  private static final String SCOPES = "r_ads_reporting r_ads";

  public LinkedinAdsOAuthFlow(ConfigRepository configRepository, HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @VisibleForTesting
  public LinkedinAdsOAuthFlow(ConfigRepository configRepository, final HttpClient httpClient, Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String formatConsentUrl(UUID definitionId, String clientId, String redirectUrl) throws IOException {
    try {
      return new URIBuilder(AUTHORIZE_URL)
          .addParameter("client_id", clientId)
          .addParameter("redirect_uri", redirectUrl)
          .addParameter("response_type", "code")
          .addParameter("scope", SCOPES)
          .addParameter("state", getState())
          .build().toString();
    } catch (URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  @Override
  protected String getAccessTokenUrl() {
    return ACCESS_TOKEN_URL;
  }

  @Override
  protected Map<String, Object> extractOAuthOutput(final JsonNode data, final String accessTokenUrl) {
    // Intercom does not have refresh token but calls it "long lived access token" instead:
    // see https://developers.intercom.com/building-apps/docs/setting-up-oauth
    Preconditions.checkArgument(data.has("access_token"), "Missing 'access_token' in query params from %s", ACCESS_TOKEN_URL);
    return Map.of("access_token", data.get("access_token").asText());
  }

  @Override
  protected List<String> getDefaultOAuthOutputPath() {
    return List.of();
  }

}
