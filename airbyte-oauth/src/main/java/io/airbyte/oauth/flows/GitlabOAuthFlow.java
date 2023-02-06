/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuth2Flow;
import java.io.IOException;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.time.Clock;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.http.client.utils.URIBuilder;

/**
 * Following docs from https://docs.gitlab.com/ee/api/oauth2.html#authorization-code-flow
 */
public class GitlabOAuthFlow extends BaseOAuth2Flow {

  private static final String ACCESS_TOKEN_URL = "https://%s/oauth/token";
  private final Clock clock;

  public GitlabOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient) {
    super(configRepository, httpClient);
    this.clock = Clock.systemUTC();
  }

  public GitlabOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
    this.clock = Clock.systemUTC();
  }

  public GitlabOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier, Clock clock) {
    super(configRepository, httpClient, stateSupplier);
    this.clock = clock;
  }

  protected static String getDomain(JsonNode inputOAuthConfiguration) throws IOException {
    final var domain = inputOAuthConfiguration.get("domain");
    if (domain == null) {
      throw new IOException("Domain field is empty.");
    }
    return domain.asText();
  }

  @Override
  protected String formatConsentUrl(final UUID definitionId, final String clientId, final String redirectUrl, final JsonNode inputOAuthConfiguration)
      throws IOException {
    final URIBuilder builder = new URIBuilder()
        .setScheme("https")
        .setHost(getDomain(inputOAuthConfiguration))
        .setPath("oauth/authorize")
        .addParameter("client_id", clientId)
        .addParameter("redirect_uri", redirectUrl)
        .addParameter("state", getState())
        .addParameter("response_type", "code")
        .addParameter("scope", "read_api");
    try {
      return builder.build().toString();
    } catch (URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  @Override
  protected String getAccessTokenUrl(final JsonNode inputOAuthConfiguration) {
    final var domain = inputOAuthConfiguration.get("domain");
    return String.format(ACCESS_TOKEN_URL, domain == null ? "gitlab.com" : domain.asText());
  }

  @Override
  protected Map<String, String> getAccessTokenQueryParameters(final String clientId,
                                                              final String clientSecret,
                                                              final String authCode,
                                                              final String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        .put("client_id", clientId)
        .put("client_secret", clientSecret)
        .put("code", authCode)
        .put("grant_type", "authorization_code")
        .put("redirect_uri", redirectUrl)
        .build();
  }

  @Override
  protected Map<String, Object> extractOAuthOutput(final JsonNode data, final String accessTokenUrl) throws IOException {
    final Map<String, Object> result = new HashMap<>();
    if (data.has("refresh_token")) {
      result.put("refresh_token", data.get("refresh_token").asText());
    } else {
      throw new IOException(String.format("Missing 'refresh_token' in query params from %s", accessTokenUrl));
    }
    if (data.has("access_token")) {
      result.put("access_token", data.get("access_token").asText());
    } else {
      throw new IOException(String.format("Missing 'access_token' in query params from %s", accessTokenUrl));
    }
    if (data.has("expires_in")) {
      Instant expires_in = Instant.now(this.clock).plusSeconds(data.get("expires_in").asInt());
      result.put("token_expiry_date", expires_in.toString());
    } else {
      throw new IOException(String.format("Missing 'expires_in' in query params from %s", accessTokenUrl));
    }
    return result;
  }

  @Override
  @Deprecated
  public Map<String, Object> completeSourceOAuth(final UUID workspaceId,
                                                 final UUID sourceDefinitionId,
                                                 final Map<String, Object> queryParams,
                                                 final String redirectUrl)
      throws IOException, ConfigNotFoundException {
    throw new IOException("Deprecated API not supported by this connector");
  }

}
