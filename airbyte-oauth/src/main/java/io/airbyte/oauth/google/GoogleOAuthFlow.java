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

package io.airbyte.oauth.google;

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
import io.airbyte.oauth.MoreOAuthParameters;
import io.airbyte.oauth.OAuthFlowImplementation;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpClient.Version;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.apache.http.client.utils.URIBuilder;

/**
 * Following docs from https://developers.google.com/identity/protocols/oauth2/web-server
 */
public class GoogleOAuthFlow implements OAuthFlowImplementation {

  private final HttpClient httpClient;

  private final static String CONSENT_URL = "https://accounts.google.com/o/oauth2/v2/auth";
  private final static String ACCESS_TOKEN_URL = "https://oauth2.googleapis.com/token";

  private final String scope;
  private final Map<String, String> defaultQueryParams;

  private final ConfigRepository configRepository;

  public GoogleOAuthFlow(ConfigRepository configRepository, String scope) {
    this(configRepository, scope, HttpClient.newBuilder().version(Version.HTTP_1_1).build());
  }

  @VisibleForTesting
  GoogleOAuthFlow(ConfigRepository configRepository, String scope, HttpClient httpClient) {
    this.configRepository = configRepository;
    this.httpClient = httpClient;
    this.scope = scope;
    this.defaultQueryParams = ImmutableMap.<String, String>builder()
        .put("scope", this.scope)
        .put("access_type", "offline")
        .put("include_granted_scopes", "true")
        .put("response_type", "code")
        .put("prompt", "consent")
        .build();

  }

  @Override
  public String getSourceConsentUrl(UUID workspaceId, UUID sourceDefinitionId, String redirectUrl) throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getSourceOAuthParamConfig(workspaceId, sourceDefinitionId);
    return getConsentUrl(sourceDefinitionId, getClientIdUnsafe(oAuthParamConfig), redirectUrl);
  }

  @Override
  public String getDestinationConsentUrl(UUID workspaceId, UUID destinationDefinitionId, String redirectUrl)
      throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getDestinationOAuthParamConfig(workspaceId, destinationDefinitionId);
    return getConsentUrl(destinationDefinitionId, getClientIdUnsafe(oAuthParamConfig), redirectUrl);
  }

  private String getConsentUrl(UUID definitionId, String clientId, String redirectUrl) {
    try {
      URIBuilder uriBuilder = new URIBuilder(CONSENT_URL)
          .addParameter("state", definitionId.toString())
          .addParameter("client_id", clientId)
          .addParameter("redirect_uri", redirectUrl);
      for (Map.Entry<String, String> queryParameter : defaultQueryParams.entrySet()) {
        uriBuilder.addParameter(queryParameter.getKey(), queryParameter.getValue());
      }
      return uriBuilder.toString();
    } catch (URISyntaxException e) {
      throw new IllegalArgumentException(e);
    }
  }

  @Override
  public Map<String, Object> completeSourceOAuth(UUID workspaceId, UUID sourceDefinitionId, Map<String, Object> queryParams, String redirectUrl)
      throws IOException, ConfigNotFoundException {
    if (queryParams.containsKey("code")) {
      final String code = (String) queryParams.get("code");
      final JsonNode oAuthParamConfig = getSourceOAuthParamConfig(workspaceId, sourceDefinitionId);
      final String clientId = getClientIdUnsafe(oAuthParamConfig);
      final String clientSecret = getClientSecretUnsafe(oAuthParamConfig);
      return completeOAuthFlow(clientId, clientSecret, code, redirectUrl);
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
      final String clientId = getClientIdUnsafe(oAuthParamConfig);
      final String clientSecret = getClientSecretUnsafe(oAuthParamConfig);
      return completeOAuthFlow(clientId, clientSecret, code, redirectUrl);
    } else {
      throw new IOException("Undefined 'code' from consent redirected url.");
    }
  }

  protected Map<String, Object> completeOAuthFlow(String clientId, String clientSecret, String code, String redirectUrl) throws IOException {
    final ImmutableMap<String, String> body = new Builder<String, String>()
        .put("client_id", clientId)
        .put("client_secret", clientSecret)
        .put("code", code)
        .put("grant_type", "authorization_code")
        .put("redirect_uri", redirectUrl)
        .build();
    final HttpRequest request = HttpRequest.newBuilder()
        .POST(HttpRequest.BodyPublishers.ofString(toUrlEncodedString(body)))
        .uri(URI.create(ACCESS_TOKEN_URL))
        .header("Content-Type", "application/x-www-form-urlencoded")
        .build();
    final HttpResponse<String> response;
    try {
      response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
      var data = Jsons.deserialize(response.body());
      if (data.has("refresh_token")) {
        return Map.of("refresh_token", data.get("refresh_token").asText());
      } else {
        // TODO This means the response from Google did not have a refresh token and is probably a
        // programming error
        // handle this better
        throw new IOException(String.format("Missing 'refresh_token' in query params from %s. Response: %s", ACCESS_TOKEN_URL, data));
      }
    } catch (InterruptedException e) {
      throw new IOException("Failed to complete Google OAuth flow", e);
    }
  }

  private static String toUrlEncodedString(ImmutableMap<String, String> body) {
    final StringBuilder result = new StringBuilder();
    for (var entry : body.entrySet()) {
      if (result.length() > 0) {
        result.append("&");
      }
      result.append(entry.getKey()).append("=").append(entry.getValue());
    }
    return result.toString();
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

  private String UrlEncode(String s) {
    try {
      return URLEncoder.encode(s, StandardCharsets.UTF_8);
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * Throws an exception if the client ID cannot be extracted. Subclasses should override this to
   * parse the config differently.
   *
   * @return
   */
  protected String getClientIdUnsafe(JsonNode oauthConfig) {
    if (oauthConfig.get("client_id") != null) {
      return oauthConfig.get("client_id").asText();
    } else {
      throw new IllegalArgumentException("Undefined parameter 'client_id' for Google OAuth Flow.");
    }
  }

  /**
   * Throws an exception if the client secret cannot be extracted. Subclasses should override this to
   * parse the config differently.
   *
   * @return
   */
  protected String getClientSecretUnsafe(JsonNode oauthConfig) {
    if (oauthConfig.get("client_secret") != null) {
      return oauthConfig.get("client_secret").asText();
    } else {
      throw new IllegalArgumentException("Undefined parameter 'client_secret' for Google OAuth Flow.");
    }
  }

}
