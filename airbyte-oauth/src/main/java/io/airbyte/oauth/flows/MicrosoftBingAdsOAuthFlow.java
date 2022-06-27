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
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.http.client.utils.URIBuilder;

public class MicrosoftBingAdsOAuthFlow extends BaseOAuth2Flow {

  private static final String fieldName = "tenant_id";

  public MicrosoftBingAdsOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @VisibleForTesting
  public MicrosoftBingAdsOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  private String getScopes() {
    return "offline_access%20https://ads.microsoft.com/msads.manage";
  }

  @Override
  protected String formatConsentUrl(final UUID definitionId,
                                    final String clientId,
                                    final String redirectUrl,
                                    final JsonNode inputOAuthConfiguration)
      throws IOException {

    final String tenantId;
    try {
      tenantId = getConfigValueUnsafe(inputOAuthConfiguration, fieldName);
    } catch (final IllegalArgumentException e) {
      throw new IOException("Failed to get " + fieldName + " value from input configuration", e);
    }

    try {
      return new URIBuilder()
          .setScheme("https")
          .setHost("login.microsoftonline.com")
          .setPath(tenantId + "/oauth2/v2.0/authorize")
          .addParameter("client_id", clientId)
          .addParameter("response_type", "code")
          .addParameter("redirect_uri", redirectUrl)
          .addParameter("response_mode", "query")
          .addParameter("state", getState())
          .build().toString() + "&scope=" + getScopes();
    } catch (final URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  @Override
  protected Map<String, String> getAccessTokenQueryParameters(final String clientId,
                                                              final String clientSecret,
                                                              final String authCode,
                                                              final String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        .put("client_id", clientId)
        .put("code", authCode)
        .put("redirect_uri", redirectUrl)
        .put("grant_type", "authorization_code")
        .build();
  }

  @Override
  protected String getAccessTokenUrl(final JsonNode inputOAuthConfiguration) {
    final String tenantId = getConfigValueUnsafe(inputOAuthConfiguration, fieldName);
    return "https://login.microsoftonline.com/" + tenantId + "/oauth2/v2.0/token";
  }

}
