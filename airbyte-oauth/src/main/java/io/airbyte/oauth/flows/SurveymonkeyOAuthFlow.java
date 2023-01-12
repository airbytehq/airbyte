/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
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

/**
 * https://developer.surveymonkey.com/api/v3/?#authentication
 */
public class SurveymonkeyOAuthFlow extends BaseOAuth2Flow {

  /**
   * https://developer.surveymonkey.com/api/v3/#access-url
   */
  private static final String API_ACCESS_URL_USA = "https://api.surveymonkey.com/";
  private static final String API_ACCESS_URL_EU = "https://api.eu.surveymonkey.com/";
  private static final String API_ACCESS_URL_CA = "https://api.surveymonkey.ca/";

  private static final String EUROPE = "Europe";
  private static final String CANADA = "Canada";
  private static final String USA = "USA";

  private static final String AUTHORIZE_URL = "oauth/authorize";
  private static final String ACCESS_TOKEN_URL = "oauth/token";

  public SurveymonkeyOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @VisibleForTesting
  SurveymonkeyOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  protected String getBaseURLByOrigin(final JsonNode inputOAuthConfiguration) throws Error {
    final String origin = getConfigValueUnsafe(inputOAuthConfiguration, "origin");
    if (EUROPE.equals(origin)) {
      return API_ACCESS_URL_EU;
    } else if (CANADA.equals(origin)) {
      return API_ACCESS_URL_CA;
    } else if (USA.equals(origin)) {
      return API_ACCESS_URL_USA;
    } else {
      throw new Error("Unknown Origin: " + origin);
    }
  }

  @Override
  protected String formatConsentUrl(final UUID definitionId,
                                    final String clientId,
                                    final String redirectUrl,
                                    final JsonNode inputOAuthConfiguration)
      throws IOException {
    try {
      final String baseUrl = getBaseURLByOrigin(inputOAuthConfiguration);
      return new URIBuilder(baseUrl)
          .setPath(AUTHORIZE_URL)
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
  protected String getAccessTokenUrl(final JsonNode inputOAuthConfiguration) {
    final String baseURL = getBaseURLByOrigin(inputOAuthConfiguration);
    return baseURL + ACCESS_TOKEN_URL;
  }

  @Override
  protected Map<String, String> getAccessTokenQueryParameters(final String clientId,
                                                              final String clientSecret,
                                                              final String authCode,
                                                              final String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        .putAll(super.getAccessTokenQueryParameters(clientId, clientSecret, authCode, redirectUrl))
        .put("grant_type", "authorization_code")
        .build();
  }

  @Override
  protected Map<String, Object> extractOAuthOutput(final JsonNode data, final String accessTokenUrl) {
    Preconditions.checkArgument(data.has("access_token"), "Missing 'access_token' in query params from %s", ACCESS_TOKEN_URL);
    return Map.of("access_token", data.get("access_token").asText());
  }

  @Override
  public List<String> getDefaultOAuthOutputPath() {
    return List.of();
  }

}
