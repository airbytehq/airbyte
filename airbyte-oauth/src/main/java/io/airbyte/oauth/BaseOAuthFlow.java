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
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
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
import java.util.Map.Entry;
import java.util.Optional;
import java.util.UUID;
import org.apache.http.client.utils.URIBuilder;

public abstract class BaseOAuthFlow implements OAuthFlowImplementation {

  private final HttpClient httpClient;
  private final ConfigRepository configRepository;

  public BaseOAuthFlow(ConfigRepository configRepository) {
    this(configRepository, HttpClient.newBuilder().version(Version.HTTP_1_1).build());
  }

  public BaseOAuthFlow(ConfigRepository configRepository, HttpClient httpClient) {
    this.configRepository = configRepository;
    this.httpClient = httpClient;
  }

  @Override
  public String getSourceConsentUrl(UUID workspaceId, UUID sourceDefinitionId, String redirectUrl) throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getSourceOAuthParamConfig(workspaceId, sourceDefinitionId);
    return formatConsentUrl(sourceDefinitionId, getClientIdUnsafe(oAuthParamConfig), redirectUrl);
  }

  @Override
  public String getDestinationConsentUrl(UUID workspaceId, UUID destinationDefinitionId, String redirectUrl)
      throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getDestinationOAuthParamConfig(workspaceId, destinationDefinitionId);
    return formatConsentUrl(destinationDefinitionId, getClientIdUnsafe(oAuthParamConfig), redirectUrl);
  }

  private String formatConsentUrl(UUID definitionId, String clientId, String redirectUrl) {
    boolean firstEntry = true;
    final StringBuilder result = new StringBuilder(getBaseConsentUrl()).append("?");
    for (Entry<String, String> entry : getConsentQueryParameters(definitionId, clientId, redirectUrl).entrySet()) {
      if (!firstEntry) {
        result.append("&");
      } else {
        firstEntry = false;
      }
      result.append(entry.getKey()).append("=").append(UrlEncode(entry.getValue()));
    }
    return result.toString();
  }

  protected abstract String getBaseConsentUrl();

  protected abstract Map<String, String> getConsentQueryParameters(UUID definitionId, String clientId, String redirectUrl);

  protected String getState(UUID definitionId) {
    // TODO state should be randomly generated, and the 2nd step of oauth should verify its value
    // matches the initially generated state value:
    // return Jsons.serialize(Map.of(
    // "definitionId", definitionId.toString(),
    // "state", UUID.randomUUID()
    // ));
    return definitionId.toString();
  }

  @Override
  public Map<String, Object> completeSourceOAuth(UUID workspaceId, UUID sourceDefinitionId, Map<String, Object> queryParams, String redirectUrl)
      throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getSourceOAuthParamConfig(workspaceId, sourceDefinitionId);
    return completeOAuthFlow(
        getClientIdUnsafe(oAuthParamConfig),
        getClientSecretUnsafe(oAuthParamConfig),
        extractCodeParameter(queryParams),
        redirectUrl);
  }

  @Override
  public Map<String, Object> completeDestinationOAuth(UUID workspaceId,
                                                      UUID destinationDefinitionId,
                                                      Map<String, Object> queryParams,
                                                      String redirectUrl)
      throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getDestinationOAuthParamConfig(workspaceId, destinationDefinitionId);
    return completeOAuthFlow(
        getClientIdUnsafe(oAuthParamConfig),
        getClientSecretUnsafe(oAuthParamConfig),
        extractCodeParameter(queryParams),
        redirectUrl);
  }

  private Map<String, Object> completeOAuthFlow(String clientId, String clientSecret, String authCode, String redirectUrl) throws IOException {
    final HttpRequest request = HttpRequest.newBuilder()
        .POST(HttpRequest.BodyPublishers.ofString(toUrlEncodedString(getAccessTokenQueryParameters(clientId, clientSecret, authCode, redirectUrl))))
        .uri(URI.create(getAccessTokenUrl()))
        .header("Content-Type", "application/x-www-form-urlencoded")
        .build();
    try {
      final HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());;
      return extractRefreshToken(Jsons.deserialize(response.body()));
    } catch (InterruptedException e) {
      throw new IOException("Failed to complete Google OAuth flow", e);
    }
  }

  protected abstract String extractCodeParameter(Map<String, Object> queryParams) throws IOException;

  protected abstract String getAccessTokenUrl();

  protected abstract Map<String, String> getAccessTokenQueryParameters(String clientId, String clientSecret, String authCode, String redirectUrl);

  protected abstract Map<String, Object> extractRefreshToken(JsonNode data) throws IOException;

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

  private static String UrlEncode(String s) {
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

  private static String toUrlEncodedString(Map<String, String> body) {
    final StringBuilder result = new StringBuilder();
    for (var entry : body.entrySet()) {
      if (result.length() > 0) {
        result.append("&");
      }
      result.append(entry.getKey()).append("=").append(UrlEncode(entry.getValue()));
    }
    return result.toString();
  }

}
