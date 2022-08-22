/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
import java.util.Locale;
import java.util.Map;
import java.util.UUID;
import org.apache.http.client.utils.URIBuilder;

public class LeverOAuthFlow extends BaseOAuth2Flow {

  private static final String AUTHORIZE_URL = "%s/authorize";
  private static final String ACCESS_TOKEN_URL = "%s/oauth/token";

  private static final String SCOPES = String.join("+", "applications:read:admin",
      "applications:read:admin",
      "interviews:read:admin",
      "notes:read:admin",
      "offers:read:admin",
      "opportunities:read:admin",
      "referrals:read:admin",
      "resumes:read:admin",
      "users:read:admin",
      "offline_access");

  public LeverOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  private String getAudience(final JsonNode inputOAuthConfiguration) {
    return String.format("%s/v1/", getBaseApiUrl(inputOAuthConfiguration));
  }

  @Override
  protected Map<String, String> getAccessTokenQueryParameters(final String clientId,
                                                              final String clientSecret,
                                                              final String authCode,
                                                              final String redirectUrl) {
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
   * Returns the URL where to retrieve the access token from.
   */
  @Override
  protected String getAccessTokenUrl(final JsonNode inputOAuthConfiguration) {
    return String.format(ACCESS_TOKEN_URL, getBaseAuthUrl(inputOAuthConfiguration));
  }

  @Override
  protected String formatConsentUrl(final UUID definitionId, final String clientId, final String redirectUrl, final JsonNode inputOAuthConfiguration)
      throws IOException {

    try {
      return URLDecoder.decode((new URIBuilder(String.format(AUTHORIZE_URL, getBaseAuthUrl(inputOAuthConfiguration)))
          .addParameter("client_id", clientId)
          .addParameter("redirect_uri", redirectUrl)
          .addParameter("state", getState())
          .addParameter("response_type", "code")
          .addParameter("scope", SCOPES)
          .addParameter("audience", getAudience(inputOAuthConfiguration))
          .addParameter("prompt", "consent").build().toString()), StandardCharsets.UTF_8);
    } catch (final URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  private String getBaseAuthUrl(final JsonNode inputOAuthConfiguration) {
    if (isProduction(inputOAuthConfiguration)) {
      return "http1s://auth.lever.co";
    } else {
      return "https://sandbox-lever.auth0.com";
    }
  }

  private String getBaseApiUrl(final JsonNode inputOAuthConfiguration) {
    if (isProduction(inputOAuthConfiguration)) {
      return "https://api.lever.co/";
    } else {
      return "https://api.sandbox.lever.co";
    }
  }

  private boolean isProduction(final JsonNode inputOAuthConfiguration) {
    final var environment = inputOAuthConfiguration.get("environment");
    return environment != null
        && environment.asText().toLowerCase(Locale.ROOT).equals("production");
  }

}
