/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import java.io.IOException;
import java.lang.reflect.Type;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpClient.Version;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.UUID;
import java.util.function.Function;
import java.util.function.Supplier;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.http.client.utils.URIBuilder;

/*
 * Class implementing generic oAuth 2.0 flow.
 */
public abstract class BaseOAuthFlow extends BaseOAuthConfig {

  public UUID getWorkspaceId() {
    return workspaceId;
  }

  @Override
  public void setWorkspaceId(UUID workspaceId) {
    this.workspaceId = workspaceId;
  }

  /**
   * Simple enum of content type strings and their respective encoding functions used for POSTing the access token request
   */
  public enum TOKEN_REQUEST_CONTENT_TYPE {
    URL_ENCODED ("application/x-www-form-urlencoded", BaseOAuthFlow::toUrlEncodedString),
    JSON ("application/json", BaseOAuthFlow::toJson);

    String contentType;
    Function<Map<String, String>, String> converter;

    TOKEN_REQUEST_CONTENT_TYPE(String contentType, Function<Map<String, String>, String> converter) {
      this.contentType = contentType;
      this.converter = converter;
    }
  }

  protected final HttpClient httpClient;
  private final TOKEN_REQUEST_CONTENT_TYPE tokenReqContentType;
  private final ConfigRepository configRepository;
  private final HttpClient httpClient;
  private final Supplier<String> stateSupplier;
  private UUID workspaceId;



  public BaseOAuthFlow(final ConfigRepository configRepository) {
    this(configRepository, HttpClient.newBuilder().version(Version.HTTP_1_1).build(), BaseOAuthFlow::generateRandomState);
  }

  public BaseOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository);
  public BaseOAuthFlow(ConfigRepository configRepository, TOKEN_REQUEST_CONTENT_TYPE tokenReqContentType) {
    this(configRepository,
            HttpClient.newBuilder().version(Version.HTTP_1_1).build(),
            BaseOAuthFlow::generateRandomState,
            tokenReqContentType);
  }

  public BaseOAuthFlow(ConfigRepository configRepository, HttpClient httpClient, Supplier<String> stateSupplier) {
    this(configRepository, httpClient, stateSupplier, TOKEN_REQUEST_CONTENT_TYPE.URL_ENCODED);
  }

  public BaseOAuthFlow(ConfigRepository configRepository, HttpClient httpClient, Supplier<String> stateSupplier, TOKEN_REQUEST_CONTENT_TYPE tokenReqContentType) {
    this.configRepository = configRepository;
    this.httpClient = httpClient;
    this.stateSupplier = stateSupplier;
    this.tokenReqContentType = tokenReqContentType;
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

  protected String formatConsentUrl(String clientId,
                                    String redirectUrl,
                                    String host,
                                    String path,
                                    String scope,
                                    String responseType) throws IOException {
    final URIBuilder builder = new URIBuilder()
            .setScheme("https")
            .setHost(host)
            .setPath(path)
            // required
            .addParameter("client_id", clientId)
            .addParameter("redirect_uri", redirectUrl)
            .addParameter("state", getState())
            // optional
            .addParameter("response_type", responseType)
            .addParameter("scope", scope);
    try {
      return builder.build().toString();
    } catch (URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  protected String getSubdomainUnsafe(JsonNode oauthConfig) {
    if (oauthConfig.get("subdomain") != null) {
      return oauthConfig.get("subdomain").asText();
    } else {
      throw new IllegalArgumentException("Undefined parameter 'subdomain' necessary for the Zendesk OAuth Flow.");
    }
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
        .POST(HttpRequest.BodyPublishers.ofString(tokenReqContentType.converter.apply(getAccessTokenQueryParameters(clientId, clientSecret, authCode, redirectUrl))))
        .uri(URI.create(getAccessTokenUrl()))
        .header("Content-Type", tokenReqContentType.contentType)
        .build();
    // TODO: Handle error response to report better messages
    try {
      final HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
      return extractRefreshToken(Jsons.deserialize(response.body()));
    } catch (final InterruptedException e) {
      throw new IOException("Failed to complete OAuth flow", e);
    }
  }

  protected String extractCodeParameter(Map<String, Object> queryParams) throws IOException {
    if (queryParams.containsKey("code")) {
      return (String) queryParams.get("code");
    } else {
      throw new IOException("Undefined 'code' from consent redirected url.");
    }
  }

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

  protected JsonNode getSourceOAuthParamConfig(UUID workspaceId, UUID sourceDefinitionId) throws IOException, ConfigNotFoundException {
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
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * Throws an exception if the client ID cannot be extracted. Subclasses should override this to
   * parse the config differently.
   *
   * @return The client Id from the OAuthConfig
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
   * @return The Client Secret from the OAuthConfiguration
   */
  protected String getClientSecretUnsafe(JsonNode oauthConfig) {
    if (oauthConfig.get("client_secret") != null) {
      return oauthConfig.get("client_secret").asText();
    } else {
      throw new IllegalArgumentException("Undefined parameter 'client_secret' necessary for the OAuth Flow.");
    }
  }

  protected static String toUrlEncodedString(final Map<String, String> body) {
    final StringBuilder result = new StringBuilder();
    for (final var entry : body.entrySet()) {
      if (result.length() > 0) {
        result.append("&");
      }
      result.append(entry.getKey()).append("=").append(urlEncode(entry.getValue()));
    }
    return result.toString();
  }

  protected static String toJson(final Map<String, String> body) {
    final Gson gson = new Gson();
    Type gsonType = new TypeToken<Map<String, String>>(){}.getType();
    return gson.toJson(body, gsonType);
  }

}
