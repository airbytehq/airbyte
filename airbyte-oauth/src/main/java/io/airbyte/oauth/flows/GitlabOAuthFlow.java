/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
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
 * Following docs from https://docs.gitlab.com/ee/api/oauth2.html#authorization-code-flow
 */
public class GitlabOAuthFlow extends BaseOAuth2Flow {

  private static final String ACCESS_TOKEN_URL = "https://%s/oauth/token";

  public GitlabOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  public GitlabOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String formatConsentUrl(final UUID definitionId, final String clientId, final String redirectUrl, final JsonNode inputOAuthConfiguration) throws IOException {
    final var domain = inputOAuthConfiguration.get("domain");
    final URIBuilder builder = new URIBuilder()
        .setScheme("https")
        .setHost(domain == null ? "gitlab.com" : domain.asText())
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
  protected String getClientIdUnsafe(final JsonNode oauthConfig) {
    // the config object containing client ID is nested inside the "credentials" object
    Preconditions.checkArgument(oauthConfig.hasNonNull("credentials"));
    return super.getClientIdUnsafe(oauthConfig.get("credentials"));
  }

  @Override
  protected String getClientSecretUnsafe(final JsonNode oauthConfig) {
    // the config object containing client SECRET is nested inside the "credentials" object
    Preconditions.checkArgument(oauthConfig.hasNonNull("credentials"));
    return super.getClientSecretUnsafe(oauthConfig.get("credentials"));
  }

  @Override
  protected String getAccessTokenUrl(final JsonNode inputOAuthConfiguration) {
    final var domain = inputOAuthConfiguration.get("domain");
    return String.format(ACCESS_TOKEN_URL, domain == null ? "gitlab.com" : domain.asText());
  }

  @Override
  protected Map<String, String> getAccessTokenQueryParameters(final String clientId, final String clientSecret, final String authCode, final String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        .put("client_id", clientId)
        .put("client_secret", clientSecret)
        .put("code", authCode)
        .put("grant_type", "authorization_code")
        .put("redirect_uri", redirectUrl)
        .build();
  }

}
