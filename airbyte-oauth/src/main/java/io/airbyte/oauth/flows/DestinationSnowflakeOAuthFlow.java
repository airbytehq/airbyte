/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuth2Flow;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import org.apache.commons.lang3.StringUtils;
import org.apache.http.client.utils.URIBuilder;

public class DestinationSnowflakeOAuthFlow extends BaseOAuth2Flow {

  private static final String AUTHORIZE_URL = "https://%s/oauth/authorize";
  private static final String ACCESS_TOKEN_URL = "https://%s/oauth/token-request";

  public DestinationSnowflakeOAuthFlow(
                                       final ConfigRepository configRepository,
                                       final HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @Override
  protected String formatConsentUrl(final UUID definitionId,
                                    final String clientId,
                                    final String redirectUrl,
                                    final JsonNode inputOAuthConfiguration)
      throws IOException {
    try {
      return new URIBuilder(
          String.format(AUTHORIZE_URL, extractAuthorizeUrl(inputOAuthConfiguration)))
              .addParameter("client_id", clientId)
              .addParameter("redirect_uri", redirectUrl)
              .addParameter("response_type", "code")
              .addParameter("state", getState())
              .build().toString();

    } catch (final URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  @Override
  protected String getAccessTokenUrl(final JsonNode inputOAuthConfiguration) {
    return String.format(ACCESS_TOKEN_URL, extractTokenUrl(inputOAuthConfiguration));
  }

  @Override
  protected String extractCodeParameter(final Map<String, Object> queryParams) throws IOException {
    return super.extractCodeParameter(queryParams);
  }

  @Override
  protected Map<String, String> getAccessTokenQueryParameters(final String clientId,
                                                              final String clientSecret,
                                                              final String authCode,
                                                              final String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        // required
        .put("grant_type", "authorization_code")
        .put("code", authCode)
        .put("redirect_uri", redirectUrl)
        .build();
  }

  // --------------------------------------------
  @Override
  protected Map<String, Object> completeOAuthFlow(final String clientId,
                                                  final String clientSecret,
                                                  final String authCode,
                                                  final String redirectUrl,
                                                  final JsonNode inputOAuthConfiguration,
                                                  final JsonNode oAuthParamConfig)
      throws IOException {
    final var accessTokenUrl = getAccessTokenUrl(inputOAuthConfiguration);

    final byte[] authorization = Base64.getEncoder()
        .encode((clientId + ":" + clientSecret).getBytes(StandardCharsets.UTF_8));
    final HttpRequest request = HttpRequest.newBuilder()
        .POST(HttpRequest.BodyPublishers
            .ofString(tokenReqContentType.getConverter().apply(
                getAccessTokenQueryParameters(clientId, clientSecret, authCode, redirectUrl))))
        .uri(URI.create(accessTokenUrl))
        .header("Content-Type", tokenReqContentType.getContentType())
        .header("Accept", "application/json")
        .header("Authorization", "Basic " + new String(authorization, StandardCharsets.UTF_8))
        .build();
    try {
      final HttpResponse<String> response = httpClient.send(request,
          HttpResponse.BodyHandlers.ofString());

      return extractOAuthOutput(Jsons.deserialize(response.body()), accessTokenUrl);
    } catch (final InterruptedException e) {
      throw new IOException("Failed to complete OAuth flow", e);
    }
  }

  /**
   * Extract all OAuth outputs from distant API response and store them in a flat map.
   */
  @Override
  protected Map<String, Object> extractOAuthOutput(final JsonNode data, final String accessTokenUrl)
      throws IOException {
    final Map<String, Object> result = new HashMap<>();
    // access_token is valid for only 10 minutes
    if (data.has("access_token")) {
      result.put("access_token", data.get("access_token").asText());
    } else {
      throw new IOException(String.format("Missing 'access_token' in query params from %s",
          accessTokenUrl));
    }

    if (data.has("refresh_token")) {
      result.put("refresh_token", data.get("refresh_token").asText());
    } else {
      throw new IOException(String.format("Missing 'refresh_token' in query params from %s",
          accessTokenUrl));
    }
    return result;
  }

  private String extractAuthorizeUrl(final JsonNode inputOAuthConfiguration) {
    final var url = inputOAuthConfiguration.get("host");
    return url == null ? StringUtils.EMPTY : url.asText();
  }

  private String extractTokenUrl(final JsonNode inputOAuthConfiguration) {
    final var url = inputOAuthConfiguration.get("host");
    // var url = inputOAuthConfiguration.get("token_url");
    return url == null ? StringUtils.EMPTY : url.asText();
  }

}
