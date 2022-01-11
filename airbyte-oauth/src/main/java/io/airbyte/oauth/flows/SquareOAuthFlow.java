/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuth2Flow;
import java.io.IOException;
import java.net.URISyntaxException;
import java.net.URLDecoder;
import java.net.http.HttpClient;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.http.client.utils.URIBuilder;

public class SquareOAuthFlow extends BaseOAuth2Flow {

  private static final String SCOPE_VALUE =
      "ITEMS_READ+CUSTOMERS_WRITE+MERCHANT_PROFILE_READ+EMPLOYEES_READ+PAYMENTS_READ+CUSTOMERS_READ+TIMECARDS_READ+ORDERS_READ";
  private static final String AUTHORIZE_URL = "https://connect.squareup.com/oauth2/authorize";
  private static final String ACCESS_TOKEN_URL = "https://connect.squareup.com/oauth2/token";

  public SquareOAuthFlow(ConfigRepository configRepository, final HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @VisibleForTesting
  public SquareOAuthFlow(ConfigRepository configRepository,
                         HttpClient httpClient,
                         Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String formatConsentUrl(final UUID definitionId,
                                    final String clientId,
                                    final String redirectUrl,
                                    final JsonNode inputOAuthConfiguration)
      throws IOException {
    try {
      // Need to have decoded format, otherwise square fails saying that scope is incorrect
      return URLDecoder.decode(new URIBuilder(AUTHORIZE_URL)
          .addParameter("client_id", clientId)
          .addParameter("scope", SCOPE_VALUE)
          .addParameter("session", "False")
          .addParameter("state", getState())
          .build().toString(), StandardCharsets.UTF_8);
    } catch (URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  @Override
  protected String getAccessTokenUrl(final JsonNode inputOAuthConfiguration) {
    return ACCESS_TOKEN_URL;
  }

  @Override
  protected Map<String, String> getAccessTokenQueryParameters(String clientId,
                                                              String clientSecret,
                                                              String authCode,
                                                              String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        // required
        .put("client_id", clientId)
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

}
