/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows.facebook;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import io.airbyte.config.persistence.ConfigRepository;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.http.client.utils.URIBuilder;

/**
 * Following docs from https://developers.facebook.com/docs/instagram-basic-display-api/overview
 */
public class InstagramOAuthFlow extends FacebookOAuthFlow {

  private static final String AUTHORIZE_URL = "https://api.instagram.com/oauth/authorize";
  private static final String ACCESS_TOKEN_URL = "https://api.instagram.com/oauth/access_token";
  private static final String LONG_LIVED_ACCESS_TOKEN_URL = "https://graph.instagram.com/access_token";
  private static final String SCOPES = "user_profile,user_media";

  public InstagramOAuthFlow(final ConfigRepository configRepository) {
    super(configRepository);
  }

  @VisibleForTesting
  InstagramOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String formatConsentUrl(final UUID definitionId, final String clientId, final String redirectUrl) throws IOException {
    try {
      return new URIBuilder(AUTHORIZE_URL)
          .addParameter("client_id", clientId)
          .addParameter("redirect_uri", redirectUrl)
          .addParameter("response_type", "code")
          .addParameter("scope", SCOPES)
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
  protected Map<String, String> getAccessTokenQueryParameters(String clientId, String clientSecret, String authCode, String redirectUrl) {
    return ImmutableMap.<String, String>builder().putAll(super.getAccessTokenQueryParameters(clientId, clientSecret, authCode, redirectUrl))
        .put("grant_type", "authorization_code").build();
  }

  @Override
  protected URI createLongLivedTokenURI(final String clientId, final String clientSecret, final String shortLivedAccessToken)
      throws URISyntaxException {
    // Exchange Short-lived Access token for Long-lived one
    // https://developers.facebook.com/docs/instagram-basic-display-api/guides/long-lived-access-tokens#get-a-long-lived-token
    // It's valid for 60 days and need to be refreshed by connector by calling /refresh_access_token
    // endpoint:
    // https://developers.facebook.com/docs/instagram-basic-display-api/guides/long-lived-access-tokens#refresh-a-long-lived-token
    return new URIBuilder(LONG_LIVED_ACCESS_TOKEN_URL)
        .addParameter("client_secret", clientSecret)
        .addParameter("grant_type", "ig_exchange_token")
        .addParameter("access_token", shortLivedAccessToken)
        .build();
  }

}
