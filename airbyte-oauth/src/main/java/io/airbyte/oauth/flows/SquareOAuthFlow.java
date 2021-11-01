/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuthFlow;
import java.io.IOException;
import java.net.URISyntaxException;
import java.net.URLDecoder;
import java.net.http.HttpClient;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.http.client.utils.URIBuilder;

public class SquareOAuthFlow extends BaseOAuthFlow {

  private static final String SCOPE_VALUE =
      "ITEMS_READ+CUSTOMERS_WRITE+MERCHANT_PROFILE_READ+EMPLOYEES_READ+PAYMENTS_READ+CUSTOMERS_READ+TIMECARDS_READ+ORDERS_READ";
  private static final String AUTHORIZE_URL = "https://connect.squareup.com/oauth2/authorize";
  private static final String ACCESS_TOKEN_URL = "https://connect.squareup.com/oauth2/token";

  public SquareOAuthFlow(ConfigRepository configRepository) {
    super(configRepository);
  }

  @VisibleForTesting
  public SquareOAuthFlow(ConfigRepository configRepository,
                         HttpClient httpClient,
                         Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String formatConsentUrl(UUID definitionId, String clientId, String redirectUrl)
      throws IOException {
    try {
      // Need to have decoded format, otherwice square fails saying that scope is incorrect
      return URLDecoder.decode(new URIBuilder(AUTHORIZE_URL)
          .addParameter("client_id", clientId)
          // .addParameter("redirect_uri", redirectUrl)
          .addParameter("scope", SCOPE_VALUE)
          .addParameter("session", "False")
          .addParameter("state", getState())
          .build().toString(), StandardCharsets.UTF_8);
    } catch (URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  @Override
  protected String getAccessTokenUrl() {
    return ACCESS_TOKEN_URL;
  }

  @Override
  protected Map<String, Object> extractRefreshToken(final JsonNode data, String accessTokenUrl)
      throws IOException {
    System.out.println(data);
    if (data.has("refresh_token")) {
      return Map.of("authorization", Map.of("refresh_token", data.get("refresh_token").asText()));
    } else {
      throw new IOException(
          String.format("Missing 'refresh_token' in query params from %s", ACCESS_TOKEN_URL));
    }
  }

  @Override
  protected Map<String, String> getAccessTokenQueryParameters(String clientId,
                                                              String clientSecret,
                                                              String authCode,
                                                              String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        // required
        .put("client_id", clientId)
        // .put("redirect_uri", redirectUrl)
        .put("client_secret", clientSecret)
        .put("code", authCode)
        .put("grant_type", "authorization_code")
        .put("scopes", "[\n"
            + "      \"ITEMS_READ\",\n"
            + "      \"MERCHANT_PROFILE_READ\",\n"
            + "      \"EMPLOYEES_READ\",\n"
            + "      \"PAYMENTS_READ\",\n"
            + "      \"CUSTOMERS_READ\",\n"
            + "      \"TIMECARDS_READ\",\n"
            + "      \"ORDERS_READ\"\n"
            + "      ]")
        .build();

  }

  @Override
  protected String getClientIdUnsafe(final JsonNode config) {
    // the config object containing client ID and secret is nested inside the "authorization" object
    Preconditions.checkArgument(config.hasNonNull("authorization"));
    return super.getClientIdUnsafe(config.get("authorization"));
  }

  @Override
  protected String getClientSecretUnsafe(final JsonNode config) {
    // the config object containing client ID and secret is nested inside the "authorization" object
    Preconditions.checkArgument(config.hasNonNull("authorization"));
    return super.getClientSecretUnsafe(config.get("authorization"));
  }

}
