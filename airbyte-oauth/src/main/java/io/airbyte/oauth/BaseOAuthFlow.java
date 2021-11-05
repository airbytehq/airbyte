/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
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
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Function;
import java.util.function.Supplier;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.http.client.utils.URIBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/*
 * Class implementing generic oAuth 2.0 flow.
 */
public abstract class BaseOAuthFlow extends BaseOAuthConfig {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseOAuthFlow.class);

  /**
   * Simple enum of content type strings and their respective encoding functions used for POSTing the
   * access token request
   */
  public enum TOKEN_REQUEST_CONTENT_TYPE {

    URL_ENCODED("application/x-www-form-urlencoded", BaseOAuthFlow::toUrlEncodedString),
    JSON("application/json", BaseOAuthFlow::toJson);

    String contentType;
    Function<Map<String, String>, String> converter;

    TOKEN_REQUEST_CONTENT_TYPE(String contentType, Function<Map<String, String>, String> converter) {
      this.contentType = contentType;
      this.converter = converter;
    }

  }

  protected final HttpClient httpClient;
  private final TOKEN_REQUEST_CONTENT_TYPE tokenReqContentType;
  private final Supplier<String> stateSupplier;

  public BaseOAuthFlow(final ConfigRepository configRepository) {
    this(configRepository, HttpClient.newBuilder().version(Version.HTTP_1_1).build(), BaseOAuthFlow::generateRandomState);
  }

  public BaseOAuthFlow(ConfigRepository configRepository, TOKEN_REQUEST_CONTENT_TYPE tokenReqContentType) {
    this(configRepository,
        HttpClient.newBuilder().version(Version.HTTP_1_1).build(),
        BaseOAuthFlow::generateRandomState,
        tokenReqContentType);
  }

  public BaseOAuthFlow(ConfigRepository configRepository, HttpClient httpClient, Supplier<String> stateSupplier) {
    this(configRepository, httpClient, stateSupplier, TOKEN_REQUEST_CONTENT_TYPE.URL_ENCODED);
  }

  public BaseOAuthFlow(ConfigRepository configRepository,
                       HttpClient httpClient,
                       Supplier<String> stateSupplier,
                       TOKEN_REQUEST_CONTENT_TYPE tokenReqContentType) {
    super(configRepository);
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
                                    String responseType)
      throws IOException {
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
        redirectUrl,
        oAuthParamConfig);
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
        redirectUrl, oAuthParamConfig);
  }

  protected Map<String, Object> completeOAuthFlow(final String clientId,
                                                  final String clientSecret,
                                                  final String authCode,
                                                  final String redirectUrl,
                                                  JsonNode oAuthParamConfig)
      throws IOException {
    var accessTokenUrl = getAccessTokenUrl();
    final HttpRequest request = HttpRequest.newBuilder()
        .POST(HttpRequest.BodyPublishers
            .ofString(tokenReqContentType.converter.apply(getAccessTokenQueryParameters(clientId, clientSecret, authCode, redirectUrl))))
        .uri(URI.create(accessTokenUrl))
        .header("Content-Type", tokenReqContentType.contentType)
        .header("Accept", "application/json")
        .build();
    try {
      final HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
      return extractRefreshToken(Jsons.deserialize(response.body()), accessTokenUrl);
    } catch (final InterruptedException e) {
      throw new IOException("Failed to complete OAuth flow", e);
    }
  }

  /**
   * Query parameters to provide the access token url with.
   */
  protected Map<String, String> getAccessTokenQueryParameters(String clientId, String clientSecret, String authCode, String redirectUrl) {
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

  protected Map<String, Object> extractRefreshToken(final JsonNode data, String accessTokenUrl) throws IOException {
    final Map<String, Object> result = new HashMap<>();
    if (data.has("refresh_token")) {
      result.put("refresh_token", data.get("refresh_token").asText());
    } else if (data.has("access_token")) {
      result.put("access_token", data.get("access_token").asText());
    } else {
      LOGGER.info("Oauth flow failed. Data received from server: {}", data);
      throw new IOException(String.format("Missing 'refresh_token' in query params from %s. Response: %s", accessTokenUrl));
    }
    return Map.of("credentials", result);

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
    Type gsonType = new TypeToken<Map<String, String>>() {}.getType();
    return gson.toJson(body, gsonType);
  }

}
