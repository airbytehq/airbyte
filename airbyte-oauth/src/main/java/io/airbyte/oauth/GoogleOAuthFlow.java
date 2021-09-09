/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.oauth;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpClient.Version;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

/**
 * Following docs from https://developers.google.com/identity/protocols/oauth2/web-server
 */
public class GoogleOAuthFlow implements OAuthFlowImplementation {

  private final HttpClient httpClient;

  private static final String GOOGLE_ANALYTICS_CONSENT_URL = "https://accounts.google.com/o/oauth2/v2/auth";
  private static final String GOOGLE_ANALYTICS_ACCESS_TOKEN_URL = "https://oauth2.googleapis.com/token";
  @VisibleForTesting
  static final String GOOGLE_ANALYTICS_SCOPE = "https%3A//www.googleapis.com/auth/analytics.readonly";
  private static final List<String> GOOGLE_QUERY_PARAMETERS = List.of(
      String.format("scope=%s", GOOGLE_ANALYTICS_SCOPE),
      "access_type=offline",
      "include_granted_scopes=true",
      "response_type=code",
      "prompt=consent");

  private final ConfigRepository configRepository;

  public GoogleOAuthFlow(ConfigRepository configRepository) {
    this(configRepository, HttpClient.newBuilder().version(Version.HTTP_1_1).build());
  }

  @VisibleForTesting
  GoogleOAuthFlow(ConfigRepository configRepository, HttpClient httpClient) {
    this.configRepository = configRepository;
    this.httpClient = httpClient;
  }

  @Override
  public String getSourceConsentUrl(UUID workspaceId, UUID sourceDefinitionId, String redirectUrl) throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getSourceOAuthParamConfig(workspaceId, sourceDefinitionId);
    if (oAuthParamConfig.has("client_id")) {
      final String clientId = oAuthParamConfig.get("client_id").asText();
      return getConsentUrl(sourceDefinitionId, clientId, redirectUrl);
    } else {
      throw new IOException("Undefined parameter 'client_id' for Google OAuth Flow.");
    }
  }

  @Override
  public String getDestinationConsentUrl(UUID workspaceId, UUID destinationDefinitionId, String redirectUrl)
      throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getDestinationOAuthParamConfig(workspaceId, destinationDefinitionId);
    if (oAuthParamConfig.has("client_id")) {
      final String clientId = oAuthParamConfig.get("client_id").asText();
      return getConsentUrl(destinationDefinitionId, clientId, redirectUrl);
    } else {
      throw new IOException("Undefined parameter 'client_id' for Google OAuth Flow.");
    }
  }

  private static String getConsentUrl(UUID definitionId, String clientId, String redirectUrl) {
    final StringBuilder result = new StringBuilder(GOOGLE_ANALYTICS_CONSENT_URL)
        .append("?");
    for (String queryParameter : GOOGLE_QUERY_PARAMETERS) {
      result.append(queryParameter).append("&");
    }
    return result
        .append("state=").append(definitionId.toString()).append("&")
        .append("client_id=").append(clientId).append("&")
        .append("redirect_uri=").append(redirectUrl)
        .toString();
  }

  @Override
  public Map<String, Object> completeSourceOAuth(UUID workspaceId, UUID sourceDefinitionId, Map<String, Object> queryParams, String redirectUrl)
      throws IOException, ConfigNotFoundException {
    if (queryParams.containsKey("code")) {
      final String code = (String) queryParams.get("code");
      final JsonNode oAuthParamConfig = getSourceOAuthParamConfig(workspaceId, sourceDefinitionId);
      if (oAuthParamConfig.has("client_id") && oAuthParamConfig.has("client_secret")) {
        final String clientId = oAuthParamConfig.get("client_id").asText();
        final String clientSecret = oAuthParamConfig.get("client_secret").asText();
        return completeOAuthFlow(clientId, clientSecret, code, redirectUrl);
      } else {
        throw new IOException("Undefined parameter 'client_id' and 'client_secret' for Google OAuth Flow.");
      }
    } else {
      throw new IOException("Undefined 'code' from consent redirected url.");
    }
  }

  @Override
  public Map<String, Object> completeDestinationOAuth(UUID workspaceId,
                                                      UUID destinationDefinitionId,
                                                      Map<String, Object> queryParams,
                                                      String redirectUrl)
      throws IOException, ConfigNotFoundException {
    if (queryParams.containsKey("code")) {
      final String code = (String) queryParams.get("code");
      final JsonNode oAuthParamConfig = getDestinationOAuthParamConfig(workspaceId, destinationDefinitionId);
      if (oAuthParamConfig.has("client_id") && oAuthParamConfig.has("client_secret")) {
        final String clientId = oAuthParamConfig.get("client_id").asText();
        final String clientSecret = oAuthParamConfig.get("client_secret").asText();
        return completeOAuthFlow(clientId, clientSecret, code, redirectUrl);
      } else {
        throw new IOException("Undefined parameter 'client_id' and 'client_secret' for Google OAuth Flow.");
      }
    } else {
      throw new IOException("Undefined 'code' from consent redirected url.");
    }
  }

  private Map<String, Object> completeOAuthFlow(String clientId, String clientSecret, String code, String redirectUrl) throws IOException {
    final ImmutableMap<String, String> body = new Builder<String, String>()
        .put("client_id", clientId)
        .put("client_secret", clientSecret)
        .put("code", code)
        .put("grant_type", "authorization_code")
        .put("redirect_uri", redirectUrl)
        .build();
    final HttpRequest request = HttpRequest.newBuilder()
        .POST(HttpRequest.BodyPublishers.ofString(Jsons.serialize(body)))
        .uri(URI.create(GOOGLE_ANALYTICS_ACCESS_TOKEN_URL))
        .header("Content-Type", "application/x-www-form-urlencoded")
        .build();
    final HttpResponse<String> response;
    try {
      response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
      final JsonNode json = Jsons.deserialize(response.body());
      return Map.of(
          "access_token", Jsons.getStringOrNull(json, "access_token"),
          "expires_in", Jsons.getIntOrZero(json, "expires_in"),
          "refresh_token", Jsons.getStringOrNull(json, "refresh_token"),
          "scope", Jsons.getStringOrNull(json, "scope"),
          "token_type", Jsons.getStringOrNull(json, "token_type"));
    } catch (InterruptedException e) {
      throw new IOException("Failed to complete Google OAuth flow", e);
    }
  }

  private JsonNode getSourceOAuthParamConfig(UUID workspaceId, UUID sourceDefinitionId) throws IOException, ConfigNotFoundException {
    try {
      final Optional<SourceOAuthParameter> param = MoreOAuthParameters.getSourceOAuthParameter(
          configRepository.listSourceOAuthParam().stream(), workspaceId, sourceDefinitionId);
      if (param.isPresent()) {
        return param.get().getConfiguration();
      } else {
        throw new ConfigNotFoundException(ConfigSchema.SOURCE_OAUTH_PARAM, "Undefined OAuth Parameter.");
      }
    } catch (JsonValidationException e) {
      throw new IOException("Failed to load OAuth Parameters", e);
    }
  }

  private JsonNode getDestinationOAuthParamConfig(UUID workspaceId, UUID destinationDefinitionId) throws IOException, ConfigNotFoundException {
    try {
      final Optional<DestinationOAuthParameter> param = MoreOAuthParameters.getDestinationOAuthParameter(
          configRepository.listDestinationOAuthParam().stream(), workspaceId, destinationDefinitionId);
      if (param.isPresent()) {
        return param.get().getConfiguration();
      } else {
        throw new ConfigNotFoundException(ConfigSchema.DESTINATION_OAUTH_PARAM, "Undefined OAuth Parameter.");
      }
    } catch (JsonValidationException e) {
      throw new IOException("Failed to load OAuth Parameters", e);
    }
  }

}
