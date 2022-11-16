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
import java.net.http.HttpClient;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.http.client.utils.URIBuilder;

public class ShopifyOAuthFlow extends BaseOAuth2Flow {

  private static final List<String> SCOPES = Arrays.asList(
      "read_themes",
      "read_orders",
      "read_all_orders",
      "read_assigned_fulfillment_orders",
      "read_content",
      "read_customers",
      "read_discounts",
      "read_draft_orders",
      "read_fulfillments",
      "read_locales",
      "read_locations",
      "read_price_rules",
      "read_products",
      "read_product_listings",
      "read_shopify_payments_payouts");

  public String getScopes() {
    return String.join(",", SCOPES);
  }

  public ShopifyOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @VisibleForTesting
  public ShopifyOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String formatConsentUrl(final UUID definitionId,
                                    final String clientId,
                                    final String redirectUrl,
                                    final JsonNode inputOAuthConfiguration)
      throws IOException {

    // getting shop value from user's config
    final String shop = getConfigValueUnsafe(inputOAuthConfiguration, "shop");
    // building consent url
    final URIBuilder builder = new URIBuilder()
        .setScheme("https")
        .setHost(shop + ".myshopify.com")
        .setPath("admin/oauth/authorize")
        .addParameter("client_id", clientId)
        .addParameter("redirect_uri", redirectUrl)
        .addParameter("state", getState())
        .addParameter("grant_options[]", "value")
        .addParameter("scope", getScopes());

    try {
      return builder.build().toString();
    } catch (URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  @Override
  protected Map<String, String> getAccessTokenQueryParameters(String clientId,
                                                              String clientSecret,
                                                              String authCode,
                                                              String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        .put("client_id", clientId)
        .put("client_secret", clientSecret)
        .put("code", authCode)
        .build();
  }

  @Override
  protected String getAccessTokenUrl(final JsonNode inputOAuthConfiguration) {
    // getting shop value from user's config
    final String shop = getConfigValueUnsafe(inputOAuthConfiguration, "shop");
    // building the access_token_url
    return "https://" + shop + ".myshopify.com/admin/oauth/access_token";
  }

  @Override
  protected Map<String, Object> extractOAuthOutput(final JsonNode data, final String accessTokenUrl) throws IOException {
    final Map<String, Object> result = new HashMap<>();
    // getting out access_token
    if (data.has("access_token")) {
      result.put("access_token", data.get("access_token").asText());
    } else {
      throw new IOException(String.format("Missing 'access_token' in query params from %s", accessTokenUrl));
    }

    return result;
  }

}
