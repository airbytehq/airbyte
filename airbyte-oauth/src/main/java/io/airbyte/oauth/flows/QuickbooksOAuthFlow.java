/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.google.common.collect.ImmutableMap;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuth2Flow;
import java.io.IOException;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.apache.http.client.utils.URIBuilder;

public class QuickbooksOAuthFlow extends BaseOAuth2Flow {

  final String CONSENT_URL = "https://appcenter.intuit.com/app/connect/oauth2";
  final String TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer";

  public QuickbooksOAuthFlow(ConfigRepository configRepository, HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  public String getScopes() {
    return "com.intuit.quickbooks.accounting";
  }

  @Override
  protected String formatConsentUrl(UUID definitionId, String clientId, String redirectUrl) throws IOException {
    try {

      return (new URIBuilder(CONSENT_URL)
          .addParameter("client_id", clientId)
          .addParameter("scope", getScopes())
          .addParameter("redirect_uri", redirectUrl)
          .addParameter("response_type", "code")
          .addParameter("state", getState())
          .build()).toString();

    } catch (final URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  protected Map<String, String> getAccessTokenQueryParameters(String clientId, String clientSecret, String authCode, String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        // required
        .put("redirect_uri", redirectUrl)
        .put("grant_type", "authorization_code")
        .put("code", authCode)
        .put("client_id", clientId)
        .put("client_secret", clientSecret)
        .build();
  }

  /**
   * Returns the URL where to retrieve the access token from.
   */
  @Override
  protected String getAccessTokenUrl() {
    return TOKEN_URL;
  }

  /**
   * This function should be redefined in each OAuthFlow implementation to isolate such "hardcoded"
   * values.
   */
  @Override
  protected List<String> getDefaultOAuthOutputPath() {
    return List.of("credentials");
  }

}
