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
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.http.client.utils.URIBuilder;

/**
 * Following docs from
 * https://support.zendesk.com/hc/en-us/articles/4408845965210-Using-OAuth-authentication-with-your-application
 */
public class ZendeskSupportOAuthFlow extends BaseOAuth2Flow {

  public ZendeskSupportOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @VisibleForTesting
  public ZendeskSupportOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String formatConsentUrl(final UUID definitionId,
                                    final String clientId,
                                    final String redirectUrl,
                                    final JsonNode inputOAuthConfiguration)
      throws IOException {

    // getting subdomain value from user's config
    final String subdomain = getConfigValueUnsafe(inputOAuthConfiguration, "subdomain");

    final URIBuilder builder = new URIBuilder()
        .setScheme("https")
        .setHost(subdomain + ".zendesk.com")
        .setPath("oauth/authorizations/new")
        // required
        .addParameter("client_id", clientId)
        .addParameter("redirect_uri", redirectUrl)
        .addParameter("response_type", "code")
        .addParameter("scope", "read")
        .addParameter("state", getState());

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
        // required
        .put("grant_type", "authorization_code")
        .put("code", authCode)
        .put("client_id", clientId)
        .put("client_secret", clientSecret)
        .put("redirect_uri", redirectUrl)
        .put("scope", "read")
        .build();
  }

  @Override
  protected String getAccessTokenUrl(final JsonNode inputOAuthConfiguration) {
    // getting subdomain value from user's config
    final String subdomain = getConfigValueUnsafe(inputOAuthConfiguration, "subdomain");
    return "https://" + subdomain + ".zendesk.com/oauth/tokens";
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
