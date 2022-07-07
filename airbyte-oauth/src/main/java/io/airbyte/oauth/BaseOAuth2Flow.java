/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.OAuthConfigSpecification;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.lang.reflect.Type;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Function;
import java.util.function.Supplier;
import org.apache.commons.lang3.RandomStringUtils;

/**
 * Abstract Class factoring common behavior for oAuth 2.0 flow implementations
 */
public abstract class BaseOAuth2Flow extends BaseOAuthFlow {

  /**
   * Simple enum of content type strings and their respective encoding functions used for POSTing the
   * access token request
   */
  public enum TOKEN_REQUEST_CONTENT_TYPE {

    URL_ENCODED("application/x-www-form-urlencoded", BaseOAuth2Flow::toUrlEncodedString),
    JSON("application/json", BaseOAuth2Flow::toJson);

    String contentType;
    Function<Map<String, String>, String> converter;

    public String getContentType() {
      return contentType;
    }

    public Function<Map<String, String>, String> getConverter() {
      return converter;
    }

    TOKEN_REQUEST_CONTENT_TYPE(final String contentType, final Function<Map<String, String>, String> converter) {
      this.contentType = contentType;
      this.converter = converter;
    }

  }

  protected final HttpClient httpClient;
  protected final TOKEN_REQUEST_CONTENT_TYPE tokenReqContentType;
  private final Supplier<String> stateSupplier;

  public BaseOAuth2Flow(final ConfigRepository configRepository, final HttpClient httpClient) {
    this(configRepository, httpClient, BaseOAuth2Flow::generateRandomState);
  }

  public BaseOAuth2Flow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    this(configRepository, httpClient, stateSupplier, TOKEN_REQUEST_CONTENT_TYPE.URL_ENCODED);
  }

  public BaseOAuth2Flow(final ConfigRepository configRepository,
                        final HttpClient httpClient,
                        final Supplier<String> stateSupplier,
                        final TOKEN_REQUEST_CONTENT_TYPE tokenReqContentType) {
    super(configRepository);
    this.httpClient = httpClient;
    this.stateSupplier = stateSupplier;
    this.tokenReqContentType = tokenReqContentType;
  }

  @Override
  public String getSourceConsentUrl(final UUID workspaceId,
                                    final UUID sourceDefinitionId,
                                    final String redirectUrl,
                                    final JsonNode inputOAuthConfiguration,
                                    final OAuthConfigSpecification oAuthConfigSpecification)
      throws IOException, ConfigNotFoundException, JsonValidationException {
    validateInputOAuthConfiguration(oAuthConfigSpecification, inputOAuthConfiguration);
    final JsonNode oAuthParamConfig = getSourceOAuthParamConfig(workspaceId, sourceDefinitionId);
    return formatConsentUrl(sourceDefinitionId, getClientIdUnsafe(oAuthParamConfig), redirectUrl, inputOAuthConfiguration);
  }

  @Override
  public String getDestinationConsentUrl(final UUID workspaceId,
                                         final UUID destinationDefinitionId,
                                         final String redirectUrl,
                                         final JsonNode inputOAuthConfiguration,
                                         final OAuthConfigSpecification oAuthConfigSpecification)
      throws IOException, ConfigNotFoundException, JsonValidationException {
    validateInputOAuthConfiguration(oAuthConfigSpecification, inputOAuthConfiguration);
    final JsonNode oAuthParamConfig = getDestinationOAuthParamConfig(workspaceId, destinationDefinitionId);
    return formatConsentUrl(destinationDefinitionId, getClientIdUnsafe(oAuthParamConfig), redirectUrl, inputOAuthConfiguration);
  }

  /**
   * Depending on the OAuth flow implementation, the URL to grant user's consent may differ,
   * especially in the query parameters to be provided. This function should generate such consent URL
   * accordingly.
   *
   * @param definitionId The configured definition ID of this client
   * @param clientId The configured client ID
   * @param redirectUrl the redirect URL
   * @param inputOAuthConfiguration any configuration property from connector necessary for this OAuth
   *        Flow
   */
  protected abstract String formatConsentUrl(final UUID definitionId,
                                             final String clientId,
                                             final String redirectUrl,
                                             final JsonNode inputOAuthConfiguration)
      throws IOException;

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
  @Deprecated
  public Map<String, Object> completeSourceOAuth(final UUID workspaceId,
                                                 final UUID sourceDefinitionId,
                                                 final Map<String, Object> queryParams,
                                                 final String redirectUrl)
      throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getSourceOAuthParamConfig(workspaceId, sourceDefinitionId);
    return formatOAuthOutput(
        oAuthParamConfig,
        completeOAuthFlow(
            getClientIdUnsafe(oAuthParamConfig),
            getClientSecretUnsafe(oAuthParamConfig),
            extractCodeParameter(queryParams),
            redirectUrl,
            Jsons.emptyObject(),
            oAuthParamConfig),
        getDefaultOAuthOutputPath());
  }

  @Override
  @Deprecated
  public Map<String, Object> completeDestinationOAuth(final UUID workspaceId,
                                                      final UUID destinationDefinitionId,
                                                      final Map<String, Object> queryParams,
                                                      final String redirectUrl)
      throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getDestinationOAuthParamConfig(workspaceId, destinationDefinitionId);
    return formatOAuthOutput(
        oAuthParamConfig,
        completeOAuthFlow(
            getClientIdUnsafe(oAuthParamConfig),
            getClientSecretUnsafe(oAuthParamConfig),
            extractCodeParameter(queryParams),
            redirectUrl,
            Jsons.emptyObject(),
            oAuthParamConfig),
        getDefaultOAuthOutputPath());
  }

  @Override
  public Map<String, Object> completeSourceOAuth(final UUID workspaceId,
                                                 final UUID sourceDefinitionId,
                                                 final Map<String, Object> queryParams,
                                                 final String redirectUrl,
                                                 final JsonNode inputOAuthConfiguration,
                                                 final OAuthConfigSpecification oAuthConfigSpecification)
      throws IOException, ConfigNotFoundException, JsonValidationException {
    validateInputOAuthConfiguration(oAuthConfigSpecification, inputOAuthConfiguration);
    final JsonNode oAuthParamConfig = getSourceOAuthParamConfig(workspaceId, sourceDefinitionId);
    return formatOAuthOutput(
        oAuthParamConfig,
        completeOAuthFlow(
            getClientIdUnsafe(oAuthParamConfig),
            getClientSecretUnsafe(oAuthParamConfig),
            extractCodeParameter(queryParams),
            redirectUrl,
            inputOAuthConfiguration,
            oAuthParamConfig),
        oAuthConfigSpecification);
  }

  @Override
  public Map<String, Object> completeDestinationOAuth(final UUID workspaceId,
                                                      final UUID destinationDefinitionId,
                                                      final Map<String, Object> queryParams,
                                                      final String redirectUrl,
                                                      final JsonNode inputOAuthConfiguration,
                                                      final OAuthConfigSpecification oAuthConfigSpecification)
      throws IOException, ConfigNotFoundException, JsonValidationException {
    validateInputOAuthConfiguration(oAuthConfigSpecification, inputOAuthConfiguration);
    final JsonNode oAuthParamConfig = getDestinationOAuthParamConfig(workspaceId, destinationDefinitionId);
    return formatOAuthOutput(
        oAuthParamConfig,
        completeOAuthFlow(
            getClientIdUnsafe(oAuthParamConfig),
            getClientSecretUnsafe(oAuthParamConfig),
            extractCodeParameter(queryParams),
            redirectUrl,
            inputOAuthConfiguration,
            oAuthParamConfig),
        oAuthConfigSpecification);
  }

  protected Map<String, Object> completeOAuthFlow(final String clientId,
                                                  final String clientSecret,
                                                  final String authCode,
                                                  final String redirectUrl,
                                                  final JsonNode inputOAuthConfiguration,
                                                  final JsonNode oAuthParamConfig)
      throws IOException {
    final var accessTokenUrl = getAccessTokenUrl(inputOAuthConfiguration);
    final HttpRequest request = HttpRequest.newBuilder()
        .POST(HttpRequest.BodyPublishers
            .ofString(tokenReqContentType.converter.apply(getAccessTokenQueryParameters(clientId, clientSecret, authCode, redirectUrl))))
        .uri(URI.create(accessTokenUrl))
        .header("Content-Type", tokenReqContentType.contentType)
        .header("Accept", "application/json")
        .build();
    // TODO: Handle error response to report better messages
    try {
      final HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
      return extractOAuthOutput(Jsons.deserialize(response.body()), accessTokenUrl);
    } catch (final InterruptedException e) {
      throw new IOException("Failed to complete OAuth flow", e);
    }
  }

  /**
   * Query parameters to provide the access token url with.
   */
  protected Map<String, String> getAccessTokenQueryParameters(final String clientId,
                                                              final String clientSecret,
                                                              final String authCode,
                                                              final String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        // required
        .put("client_id", clientId)
        .put("redirect_uri", redirectUrl)
        .put("client_secret", clientSecret)
        .put("code", authCode)
        .build();
  }

  /**
   * Once the user is redirected after getting their consent, the API should redirect them to a
   * specific redirection URL along with query parameters. This function should parse and extract the
   * code from these query parameters in order to continue the OAuth Flow.
   */
  protected String extractCodeParameter(final Map<String, Object> queryParams) throws IOException {
    if (queryParams.containsKey("code")) {
      return (String) queryParams.get("code");
    } else {
      throw new IOException("Undefined 'code' from consent redirected url.");
    }
  }

  /**
   * Returns the URL where to retrieve the access token from.
   */
  protected abstract String getAccessTokenUrl(final JsonNode inputOAuthConfiguration);

  /**
   * Extract all OAuth outputs from distant API response and store them in a flat map.
   */
  protected Map<String, Object> extractOAuthOutput(final JsonNode data, final String accessTokenUrl) throws IOException {
    final Map<String, Object> result = new HashMap<>();
    if (data.has("refresh_token")) {
      result.put("refresh_token", data.get("refresh_token").asText());
    } else {
      throw new IOException(String.format("Missing 'refresh_token' in query params from %s", accessTokenUrl));
    }
    return result;
  }

  @Override
  @Deprecated
  public List<String> getDefaultOAuthOutputPath() {
    return List.of("credentials");
  }

  protected static void validateInputOAuthConfiguration(final OAuthConfigSpecification oauthConfigSpecification,
                                                        final JsonNode inputOAuthConfiguration)
      throws JsonValidationException {
    if (oauthConfigSpecification != null && oauthConfigSpecification.getOauthUserInputFromConnectorConfigSpecification() != null) {
      final JsonSchemaValidator validator = new JsonSchemaValidator();
      validator.ensure(oauthConfigSpecification.getOauthUserInputFromConnectorConfigSpecification(), inputOAuthConfiguration);
    }
  }

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

  protected static String toJson(final Map<String, String> body) {
    final Gson gson = new Gson();
    final Type gsonType = new TypeToken<Map<String, String>>() {}.getType();
    return gson.toJson(body, gsonType);
  }

}
