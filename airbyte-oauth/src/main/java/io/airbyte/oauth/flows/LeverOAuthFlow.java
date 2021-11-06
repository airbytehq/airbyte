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
import java.net.http.HttpClient;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;

public class LeverOAuthFlow extends BaseOAuthFlow {

  private static final String AUTHORIZE_URL = "https://sandbox-lever.auth0.com/authorize";
  private static final String ACCESS_TOKEN_URL = "https://sandbox-lever.auth0.com/oauth/token";
  // private static final String ACCESS_TOKEN_URL = "https://api.sandbox.lever.co/oauth/token";
  private static final String SCOPES = String.join("+", "applications:read:admin",
      "contact:read:admin",
      "interviews:read:admin",
      "offers:read:admin",
      "opportunities:read:admin",
      "postings:read:admin",
      "referrals:read:admin",
      "requisitions:read:admin",
      "resumes:read:admin",
      "sources:read:admin",
      "stages:read:admin",
      "offline_access");

  private String getAudience() {
    return "https://api.sandbox.lever.co/v1/";
  }

  protected Map<String, String> getAccessTokenQueryParameters(String clientId, String clientSecret, String authCode, String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        // required
        .put("client_id", clientId)
        .put("redirect_uri", redirectUrl)
        .put("client_secret", clientSecret)
        .put("grant_type", "authorization_code")
        .put("code", authCode)
        .build();
  }

  @Override
  protected Map<String, Object> extractRefreshToken(JsonNode data, String accessTokenUrl) throws IOException {
    System.out.println(Jsons.serialize(data));
    if (data.has("refresh_token")) {
      final String refreshToken = data.get("refresh_token").asText();
      return Map.of("refresh_token", refreshToken);
    } else {
      throw new IOException(String.format("Missing 'refresh_token' in query params from %s", accessTokenUrl));
    }
  }

  @Override
  protected String formatConsentUrl(UUID definitionId, String clientId, String redirectUrl) throws IOException {
    return String.format("%s?client_id=%s&redirect_uri=%s&response_type=code&state=%s&scope=%s&prompt=consent&audience=%s",
        AUTHORIZE_URL,
        clientId,
        redirectUrl,
        getState(),
        SCOPES,
        getAudience());
  }

  public LeverOAuthFlow(ConfigRepository configRepository) {
    super(configRepository);
  }

  @VisibleForTesting
  LeverOAuthFlow(ConfigRepository configRepository, HttpClient httpClient, Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  /**
   * Returns the URL where to retrieve the access token from.
   */
  @Override
  protected String getAccessTokenUrl() {
    return ACCESS_TOKEN_URL;
  }

}
