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
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.http.client.utils.URIBuilder;

/**
 * Following docs from
 * https://help.salesforce.com/s/articleView?language=en_US&amp;id=sf.remoteaccess_oauth_web_server_flow.htm
 */
public class SalesforceOAuthFlow extends BaseOAuth2Flow {
  // Clickable link for IDE
  // https://help.salesforce.com/s/articleView?language=en_US&id=sf.remoteaccess_oauth_web_server_flow.htm

  private static final String AUTHORIZE_URL = "https://%s.salesforce.com/services/oauth2/authorize";
  private static final String ACCESS_TOKEN_URL = "https://%s.salesforce.com/services/oauth2/token";

  public SalesforceOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @VisibleForTesting
  SalesforceOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String formatConsentUrl(final UUID definitionId,
                                    final String clientId,
                                    final String redirectUrl,
                                    final JsonNode inputOAuthConfiguration)
      throws IOException {
    try {
      return new URIBuilder(String.format(AUTHORIZE_URL, getEnvironment(inputOAuthConfiguration)))
          .addParameter("client_id", clientId)
          .addParameter("redirect_uri", redirectUrl)
          .addParameter("response_type", "code")
          .addParameter("state", getState())
          .build().toString();
    } catch (final URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  @Override
  protected String getAccessTokenUrl(final JsonNode inputOAuthConfiguration) {
    return String.format(ACCESS_TOKEN_URL, getEnvironment(inputOAuthConfiguration));
  }

  @Override
  protected Map<String, String> getAccessTokenQueryParameters(final String clientId,
                                                              final String clientSecret,
                                                              final String authCode,
                                                              final String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        .putAll(super.getAccessTokenQueryParameters(clientId, clientSecret, authCode, redirectUrl))
        .put("grant_type", "authorization_code")
        .build();
  }

  @Override
  public List<String> getDefaultOAuthOutputPath() {
    return List.of();
  }

  private String getEnvironment(JsonNode inputOAuthConfiguration) {
    var isSandbox = inputOAuthConfiguration.get("is_sandbox");
    if (isSandbox == null) {
      return "login";
    }
    return (isSandbox.asBoolean() == true) ? "test" : "login";
  }

}
