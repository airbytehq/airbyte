/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuth2Flow;
import java.io.IOException;
import java.net.URISyntaxException;
import java.net.URLDecoder;
import java.net.http.HttpClient;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import org.apache.http.client.utils.URIBuilder;

public class LeverOAuthFlow extends BaseOAuth2Flow {

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

  public LeverOAuthFlow(ConfigRepository configRepository, HttpClient httpClient) {
    super(configRepository, httpClient);
  }

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

  /**
   * Extract all OAuth outputs from distant API response and store them in a flat map.
   */
  protected Map<String, Object> extractOAuthOutput(final JsonNode data, final String accessTokenUrl) throws IOException {
    final Map<String, Object> result = new HashMap<>();
    if (data.has("access_token")) {
      result.put("access_token", data.get("access_token").asText());
    } else {
      throw new IOException(String.format("Missing 'refresh_token' in query params from %s", accessTokenUrl));
    }
    return result;
  }

  /**
   * Returns the URL where to retrieve the access token from.
   */
  @Override
  protected String getAccessTokenUrl() {
    return ACCESS_TOKEN_URL;
  }

  @Override
  protected String formatConsentUrl(UUID definitionId, String clientId, String redirectUrl, JsonNode inputOAuthConfiguration) throws IOException {
    try {
      return URLDecoder.decode((new URIBuilder(AUTHORIZE_URL))

          .addParameter("client_id", clientId)
          .addParameter("redirect_uri", redirectUrl)
          .addParameter("state", getState())
          .addParameter("response_type", "code")
          .addParameter("scope", SCOPES)
          .addParameter("audience", getAudience())
          .addParameter("prompt", "consent").build().toString(), StandardCharsets.UTF_8);
    } catch (URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

}
