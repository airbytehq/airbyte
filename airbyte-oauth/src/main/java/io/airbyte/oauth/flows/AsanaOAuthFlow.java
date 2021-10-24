/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
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
 * Following docs from https://developers.asana.com/docs/oauth
 */
public class AsanaOAuthFlow extends BaseOAuthFlow {

  private static final String AUTHORIZE_URL = "https://app.asana.com/-/oauth_authorize";
  private static final String ACCESS_TOKEN_URL = "https://app.asana.com/-/oauth_token";

  public AsanaOAuthFlow(ConfigRepository configRepository) {
    super(configRepository);
  }

  @VisibleForTesting
  AsanaOAuthFlow(ConfigRepository configRepository, HttpClient httpClient, Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String formatConsentUrl(UUID definitionId, String clientId, String redirectUrl) throws IOException {
    try {
      return new URIBuilder(AUTHORIZE_URL)
          .addParameter("client_id", clientId)
          .addParameter("redirect_uri", redirectUrl)
          .addParameter("response_type", "code")
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
  protected Map<String, String> getAccessTokenQueryParameters(String clientId, String clientSecret, String authCode, String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        .putAll(super.getAccessTokenQueryParameters(clientId, clientSecret, authCode, redirectUrl))
        .put("grant_type", "authorization_code")
        .build();
  }

  @Override
  protected Map<String, Object> extractRefreshToken(JsonNode data) throws IOException {
    System.out.println(Jsons.serialize(data));
    if (data.has("refresh_token")) {
      final String refreshToken = data.get("refresh_token").asText();
      return Map.of("credentials", Map.of("refresh_token", refreshToken));
    } else {
      throw new IOException(String.format("Missing 'refresh_token' in query params from %s", ACCESS_TOKEN_URL));
    }
  }

}
