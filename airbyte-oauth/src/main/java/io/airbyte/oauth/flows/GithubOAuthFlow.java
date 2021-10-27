/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuthFlow;
import java.io.IOException;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.http.client.utils.URIBuilder;

/**
 * Following docs from
 * https://docs.github.com/en/developers/apps/building-oauth-apps/authorizing-oauth-apps#web-application-flow
 */
public class GithubOAuthFlow extends BaseOAuthFlow {

  private static final String AUTHORIZE_URL = "https://github.com/login/oauth/authorize";
  private static final String ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token";

  public GithubOAuthFlow(final ConfigRepository configRepository) {
    super(configRepository);
  }

  @VisibleForTesting
  GithubOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String formatConsentUrl(final UUID definitionId, final String clientId, final String redirectUrl) throws IOException {
    try {
      // No scope means read-only access to public information
      // https://docs.github.com/en/developers/apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes
      return new URIBuilder(AUTHORIZE_URL)
          .addParameter("client_id", clientId)
          .addParameter("redirect_uri", redirectUrl)
          .addParameter("state", getState())
          .build().toString();
    } catch (URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  @Override
  protected String getAccessTokenUrl() {
    return ACCESS_TOKEN_URL;
  }

  @Override
  protected Map<String, Object> extractRefreshToken(final JsonNode data, String accessTokenUrl) throws IOException {
    System.out.println(data);
    if (data.has("access_token")) {
      return Map.of("credentials", Map.of("access_token", data.get("access_token").asText()));
    } else {
      throw new IOException(String.format("Missing 'access_token' in query params from %s", ACCESS_TOKEN_URL));
    }
  }

  @Override
  protected String getClientIdUnsafe(final JsonNode config) {
    // the config object containing client ID and secret is nested inside the "credentials" object
    Preconditions.checkArgument(config.hasNonNull("credentials"));
    return super.getClientIdUnsafe(config.get("credentials"));
  }

  @Override
  protected String getClientSecretUnsafe(final JsonNode config) {
    // the config object containing client ID and secret is nested inside the "credentials" object
    Preconditions.checkArgument(config.hasNonNull("credentials"));
    return super.getClientSecretUnsafe(config.get("credentials"));
  }

}
