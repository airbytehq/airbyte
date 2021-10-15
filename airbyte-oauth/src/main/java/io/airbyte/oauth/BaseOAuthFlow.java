/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpClient.Version;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.commons.lang3.RandomStringUtils;

/*
 * Class implementing generic oAuth 2.0 flow.
 */
public abstract class BaseOAuthFlow extends BaseOAuthConfig {

  private final HttpClient httpClient;
  private final Supplier<String> stateSupplier;

  public BaseOAuthFlow(final ConfigRepository configRepository) {
    this(configRepository, HttpClient.newBuilder().version(Version.HTTP_1_1).build(), BaseOAuthFlow::generateRandomState);
  }

  public BaseOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository);
    this.httpClient = httpClient;
    this.stateSupplier = stateSupplier;
  }

  @Override
  public String getSourceConsentUrl(final UUID workspaceId, final UUID sourceDefinitionId, final String redirectUrl)
      throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getSourceOAuthParamConfig(workspaceId, sourceDefinitionId);
    return formatConsentUrl(sourceDefinitionId, getClientIdUnsafe(oAuthParamConfig), redirectUrl);
  }

  @Override
  public String getDestinationConsentUrl(final UUID workspaceId, final UUID destinationDefinitionId, final String redirectUrl)
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
  public Map<String, Object> completeSourceOAuth(
                                                 final UUID workspaceId,
                                                 final UUID sourceDefinitionId,
                                                 final Map<String, Object> queryParams,
                                                 final String redirectUrl)
      throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getSourceOAuthParamConfig(workspaceId, sourceDefinitionId);
    return completeOAuthFlow(
        getClientIdUnsafe(oAuthParamConfig),
        getClientSecretUnsafe(oAuthParamConfig),
        extractCodeParameter(queryParams),
        redirectUrl);
  }

  @Override
  public Map<String, Object> completeDestinationOAuth(final UUID workspaceId,
                                                      final UUID destinationDefinitionId,
                                                      final Map<String, Object> queryParams,
                                                      final String redirectUrl)
      throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getDestinationOAuthParamConfig(workspaceId, destinationDefinitionId);
    return completeOAuthFlow(
        getClientIdUnsafe(oAuthParamConfig),
        getClientSecretUnsafe(oAuthParamConfig),
        extractCodeParameter(queryParams),
        redirectUrl);
  }

  private Map<String, Object> completeOAuthFlow(final String clientId, final String clientSecret, final String authCode, final String redirectUrl)
      throws IOException {
    final HttpRequest request = HttpRequest.newBuilder()
        .POST(HttpRequest.BodyPublishers.ofString(toUrlEncodedString(getAccessTokenQueryParameters(clientId, clientSecret, authCode, redirectUrl))))
        .uri(URI.create(getAccessTokenUrl()))
        .header("Content-Type", "application/x-www-form-urlencoded")
        .build();
    // TODO: Handle error response to report better messages
    try {
      final HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());;
      return extractRefreshToken(Jsons.deserialize(response.body()));
    } catch (final InterruptedException e) {
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

  private static String urlEncode(final String s) {
    try {
      return URLEncoder.encode(s, StandardCharsets.UTF_8);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  private static String toUrlEncodedString(final Map<String, String> body) {
    final StringBuilder result = new StringBuilder();
    for (final var entry : body.entrySet()) {
      if (result.length() > 0) {
        result.append("&");
      }
      result.append(entry.getKey()).append("=").append(urlEncode(entry.getValue()));
    }
    return result.toString();
  }

}
