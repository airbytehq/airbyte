/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.apache.http.client.utils.URIBuilder;

public class SquareOAuthFlow extends BaseOAuth2Flow {

  private static final List<String> SCOPES = Arrays.asList(
      "CUSTOMERS_READ",
      "EMPLOYEES_READ",
      "ITEMS_READ",
      "MERCHANT_PROFILE_READ",
      "ORDERS_READ",
      "PAYMENTS_READ",
      "TIMECARDS_READ"
  // OAuth Permissions:
  // https://developer.squareup.com/docs/oauth-api/square-permissions
  // https://developer.squareup.com/reference/square/enums/OAuthPermission
  // "DISPUTES_READ",
  // "GIFTCARDS_READ",
  // "INVENTORY_READ",
  // "INVOICES_READ",
  // "TIMECARDS_SETTINGS_READ",
  // "LOYALTY_READ",
  // "ONLINE_STORE_SITE_READ",
  // "ONLINE_STORE_SNIPPETS_READ",
  // "SUBSCRIPTIONS_READ",
  );
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
          .addParameter("scope", String.join("+", SCOPES))
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
    String scopes = SCOPES.stream()
        .map(name -> ('"' + name + '"'))
        .collect(Collectors.joining(","));
    scopes = '[' + scopes + ']';

    return ImmutableMap.<String, String>builder()
        // required
        .put("client_id", clientId)
        .put("client_secret", clientSecret)
        .put("code", authCode)
        .put("grant_type", "authorization_code")
        .put("scopes", scopes)
        .build();
  }

}
