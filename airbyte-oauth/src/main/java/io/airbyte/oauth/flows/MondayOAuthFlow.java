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
 * Following docs from https://developer.zendesk.com/documentation/live-chat/getting-started/auth/
 */
public class MondayOAuthFlow extends BaseOAuth2Flow {

  private static final String ACCESS_TOKEN_URL = "https://auth.monday.com/oauth2/token";

  public MondayOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @VisibleForTesting
  public MondayOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
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
        .setHost("auth.monday.com")
        .setPath("oauth2/authorize")
        // required
        .addParameter("client_id", clientId)
        .addParameter("redirect_uri", redirectUrl)
        .addParameter("scope", "me:read boards:read workspaces:read users:read account:read updates:read assets:read tags:read teams:read")
        .addParameter("state", getState());

    try {
      // applying optional parameter of subdomain, if there is any value
      if (!subdomain.isEmpty()) {
        builder.addParameter("subdomain", subdomain);
      }
      return builder.build().toString();
    } catch (final URISyntaxException e) {
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
        .put("code", authCode)
        .put("client_id", clientId)
        .put("client_secret", clientSecret)
        .put("redirect_uri", redirectUrl)
        .build();
  }

  @Override
  protected String getAccessTokenUrl(final JsonNode inputOAuthConfiguration) {
    return ACCESS_TOKEN_URL;
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
