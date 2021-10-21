/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.client.util.Preconditions;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuthFlow;
import java.io.IOException;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.http.client.utils.URIBuilder;

public class ShopifyOAuthFlow extends BaseOAuthFlow {

  private static final String ACCESS_TOKEN_URL = "https://airbyte-integration-test.myshopify.com/admin/oauth/access_token";
  private static final List<String> SCOPES = Arrays.asList(
      "read_themes",
      "read_orders",
      "read_all_orders",
      "read_assigned_fulfillment_orders",
      "read_checkouts",
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

  private String authPrefix = "airbyte-integration-test";

  public ShopifyOAuthFlow(ConfigRepository configRepository) {
    super(configRepository);
  }

  public String getScopes() {
    return String.join(",", SCOPES);
  }

  public void setAuthPrefix(String authPrefix) {
    this.authPrefix = authPrefix;
  }

  @VisibleForTesting
  ShopifyOAuthFlow(ConfigRepository configRepository, HttpClient httpClient,
      Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String formatConsentUrl(UUID definitionId, String clientId, String redirectUrl)
      throws IOException {
    String host = authPrefix + ".myshopify.com";
    final URIBuilder builder = new URIBuilder()
        .setScheme("https")
        .setHost(host)
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
  protected String extractCodeParameter(Map<String, Object> queryParams) throws IOException {
    if (queryParams.containsKey("code")) {
      return (String) queryParams.get("code");
    } else {
      throw new IOException("Undefined 'code' from consent redirected url.");
    }
  }

  @Override
  protected String getClientIdUnsafe(JsonNode config) {
    // the config object containing client ID is nested inside the "credentials" object
    Preconditions.checkArgument(config.hasNonNull("credentials"));
    return super.getClientIdUnsafe(config.get("credentials"));
  }

  @Override
  protected String getClientSecretUnsafe(JsonNode config) {
    // the config object containing client SECRET is nested inside the "credentials" object
    Preconditions.checkArgument(config.hasNonNull("credentials"));
    return super.getClientSecretUnsafe(config.get("credentials"));
  }

  @Override
  protected String getAccessTokenUrl() {
    return ACCESS_TOKEN_URL;
  }

  @Override
  protected Map<String, String> getAccessTokenQueryParameters(String clientId, String clientSecret,
      String authCode, String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        .put("client_id", clientId)
        .put("client_secret", clientSecret)
        .put("code", authCode)
        .build();
  }

  @Override
  protected Map<String, Object> extractRefreshToken(JsonNode data) throws IOException {
    // Shopify does not have refresh token but calls it "long lived access token" instead:
    if (data.has("access_token")) {
      return Map.of("credentials", Map.of("access_token", data.get("access_token").asText()));
    } else {
      throw new IOException(
          String.format("Missing 'access_token' in query params from %s", getAccessTokenUrl()));
    }
  }

}
