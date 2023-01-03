/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
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
import java.util.function.Supplier;
import org.apache.http.client.utils.URIBuilder;

public class SourceSnowflakeOAuthFlow extends BaseOAuth2Flow {

  private static final String AUTHORIZE_URL = "https://%s/oauth/authorize";
  private static final String ACCESS_TOKEN_URL = "https://%s/oauth/token-request";

  public SourceSnowflakeOAuthFlow(ConfigRepository configRepository, HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @VisibleForTesting
  public SourceSnowflakeOAuthFlow(ConfigRepository configRepository, HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String formatConsentUrl(UUID definitionId,
                                    String clientId,
                                    String redirectUrl,
                                    JsonNode inputOAuthConfiguration)
      throws IOException {
    try {
      String consentUrl = new URIBuilder(String.format(AUTHORIZE_URL, extractUrl(inputOAuthConfiguration)))
          .addParameter("client_id", clientId)
          .addParameter("redirect_uri", redirectUrl)
          .addParameter("response_type", "code")
          .addParameter("state", getState())
          .build().toString();
      String providedRole = extractRole(inputOAuthConfiguration);
      return providedRole.isEmpty()
          ? consentUrl
          : getConsentUrlWithScopeRole(consentUrl, providedRole);
    } catch (final URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  private static String getConsentUrlWithScopeRole(String consentUrl, String providedRole) throws URISyntaxException {
    return new URIBuilder(consentUrl)
        .addParameter("scope", "session:role:" + providedRole)
        .build().toString();
  }

  @Override
  protected String getAccessTokenUrl(JsonNode inputOAuthConfiguration) {
    return String.format(ACCESS_TOKEN_URL, extractUrl(inputOAuthConfiguration));
  }

  @Override
  protected String extractCodeParameter(Map<String, Object> queryParams) throws IOException {
    return super.extractCodeParameter(queryParams);
  }

  @Override
  protected Map<String, String> getAccessTokenQueryParameters(String clientId,
                                                              String clientSecret,
                                                              String authCode,
                                                              String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        // required
        .put("grant_type", "authorization_code")
        .put("code", authCode)
        .put("redirect_uri", redirectUrl)
        .build();
  }

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

  @Override
  protected Map<String, Object> extractOAuthOutput(JsonNode data, String accessTokenUrl)
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
    if (data.has("username")) {
      result.put("username", data.get("username").asText());
    } else {
      throw new IOException(String.format("Missing 'username' in query params from %s",
          accessTokenUrl));
    }
    return result;
  }

  private String extractUrl(JsonNode inputOAuthConfiguration) {
    var url = inputOAuthConfiguration.get("host");
    return url == null ? "snowflakecomputing.com" : url.asText();
  }

  private String extractRole(JsonNode inputOAuthConfiguration) {
    var role = inputOAuthConfiguration.get("role");
    return role == null ? "" : role.asText();
  }

}
