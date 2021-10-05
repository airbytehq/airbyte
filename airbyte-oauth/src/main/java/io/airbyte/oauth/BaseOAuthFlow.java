/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpClient.Version;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.commons.lang3.RandomStringUtils;

public abstract class BaseOAuthFlow implements OAuthFlowImplementation {

  private final HttpClient httpClient;
  private final ConfigRepository configRepository;
  private final Supplier<String> stateSupplier;

  public BaseOAuthFlow(ConfigRepository configRepository) {
    this(configRepository, HttpClient.newBuilder().version(Version.HTTP_1_1).build(), BaseOAuthFlow::generateRandomState);
  }

  public BaseOAuthFlow(ConfigRepository configRepository, HttpClient httpClient, Supplier<String> stateSupplier) {
    this.configRepository = configRepository;
    this.httpClient = httpClient;
    this.stateSupplier = stateSupplier;
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

  /**
   * Depending on the OAuth flow implementation, the URL to grant user's consent may differ,
   * especially in the query parameters to be provided. This function should generate such consent URL
   * accordingly.
   */
  protected abstract String formatConsentUrl(UUID definitionId, String clientId, String redirectUrl) throws IOException;

  private static String generateRandomState() {
    return RandomStringUtils.randomAlphanumeric(7);
  }

  /**
   * Generate a string to use as state in the OAuth process.
   */
  protected String getState() {
    return stateSupplier.get();
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
    // TODO: Handle error response to report better messages
    try {
      final HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());;
      return extractRefreshToken(Jsons.deserialize(response.body()));
    } catch (InterruptedException e) {
      throw new IOException("Failed to complete OAuth flow", e);
    }
  }

  /**
   * Once the user is redirected after getting their consent, the API should redirect them to a
   * specific redirection URL along with query parameters. This function should parse and extract the
   * code from these query parameters in order to continue the OAuth Flow.
   */
  protected abstract String extractCodeParameter(Map<String, Object> queryParams) throws IOException;

  /**
   * Returns the URL where to retrieve the access token from.
   */
  protected abstract String getAccessTokenUrl();

  /**
   * Query parameters to provide the access token url with.
   */
  protected abstract Map<String, String> getAccessTokenQueryParameters(String clientId, String clientSecret, String authCode, String redirectUrl);

  /**
   * Once the auth code is exchange for a refresh token, the oauth flow implementation can extract and
   * returns the values of fields to be used in the connector's configurations.
   */
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

  private static String urlEncode(String s) {
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
      throw new IllegalArgumentException("Undefined parameter 'client_id' necessary for the OAuth Flow.");
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
      throw new IllegalArgumentException("Undefined parameter 'client_secret' necessary for the OAuth Flow.");
    }
  }

  private static String toUrlEncodedString(Map<String, String> body) {
    final StringBuilder result = new StringBuilder();
    for (var entry : body.entrySet()) {
      if (result.length() > 0) {
        result.append("&");
      }
      result.append(entry.getKey()).append("=").append(urlEncode(entry.getValue()));
    }
    return result.toString();
  }

}
