/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuth2Flow;
import java.io.IOException;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.http.client.utils.URIBuilder;

/**
 * Following docs from
 * https://docs.github.com/en/developers/apps/building-oauth-apps/authorizing-oauth-apps#web-application-flow
 */
public class GithubOAuthFlow extends BaseOAuth2Flow {

  private static final String AUTHORIZE_URL = "https://github.com/login/oauth/authorize";
  private static final String ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token";
  // Setting "repo" scope would allow grant not only read but also write
  // access to our application. Unfortunatelly we cannot follow least
  // privelege principle here cause github has no option of granular access
  // tune up.
  // This is necessary to pull data from private repositories.
  // https://docs.github.com/en/developers/apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes

  private static final List<String> SCOPES = Arrays.asList(
      "repo",
      "read:org",
      "read:repo_hook",
      "read:user",
      "read:discussion",
      "workflow");

  public String getScopes() {
    return String.join("%20", SCOPES);
  }

  public GithubOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @VisibleForTesting
  GithubOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
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
          .addParameter("redirect_uri", redirectUrl)
          // we add `scopes` and `state` after we've already built the url, to prevent url encoding for scopes
          // https://docs.github.com/en/developers/apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes
          // we need to keep scopes in the format of: < scope1%20scope2:sub_scope%20scope3 >
          .build().toString() + "&scope=" + getScopes() + "&state=" + getState();
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
    if (data.has("access_token")) {
      return Map.of("access_token", data.get("access_token").asText());
    } else {
      throw new IOException(String.format("Missing 'access_token' in query params from %s", ACCESS_TOKEN_URL));
    }
  }

}
