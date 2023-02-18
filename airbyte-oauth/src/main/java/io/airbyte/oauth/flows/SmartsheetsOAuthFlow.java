/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
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

public class SmartsheetsOAuthFlow extends BaseOAuth2Flow {

  private static final String AUTHORIZE_URL = "https://app.smartsheet.com/b/authorize";
  private static final String ACCESS_TOKEN_URL = "https://api.smartsheet.com/2.0/token";
  private final Clock clock;

  public SmartsheetsOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient) {
    super(configRepository, httpClient);
    this.clock = Clock.systemUTC();
  }

  @VisibleForTesting
  public SmartsheetsOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
    this.clock = Clock.systemUTC();
  }

  @Override
  protected String formatConsentUrl(final UUID definitionId,
                                    final String clientId,
                                    final String redirectUrl,
                                    final JsonNode inputOAuthConfiguration)
      throws IOException {
    try {
      return new URIBuilder(AUTHORIZE_URL)
          .addParameter("client_id", clientId)
          .addParameter("response_type", "code")
          .addParameter("state", getState())
          .addParameter("scope", "READ_SHEETS")
          .build().toString();
    } catch (final URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  @Override
  protected String getAccessTokenUrl(final JsonNode inputOAuthConfiguration) {
    return ACCESS_TOKEN_URL;
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
  protected Map<String, String> getAccessTokenQueryParameters(final String clientId,
                                                              final String clientSecret,
                                                              final String authCode,
                                                              final String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        // required
        .put("grant_type", "authorization_code")
        .put("client_id", clientId)
        .put("client_secret", clientSecret)
        .put("code", authCode)
        .build();
  }

}
