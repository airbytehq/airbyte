/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuth2Flow;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.http.client.utils.URIBuilder;

public class LinkedinAdsOAuthFlow extends BaseOAuth2Flow {

  private static final String AUTHORIZE_URL = "https://www.linkedin.com/oauth/v2/authorization";
  private static final String ACCESS_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken";
  private static final String SCOPES = "r_ads_reporting r_ads r_basicprofile";

  public LinkedinAdsOAuthFlow(ConfigRepository configRepository, HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @VisibleForTesting
  public LinkedinAdsOAuthFlow(ConfigRepository configRepository, final HttpClient httpClient, Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String formatConsentUrl(UUID definitionId, String clientId, String redirectUrl) throws IOException {
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
  protected Map<String, Object> extractOAuthOutput(final JsonNode data, final String accessTokenUrl) {
    // Intercom does not have refresh token but calls it "long lived access token" instead:
    // see https://developers.intercom.com/building-apps/docs/setting-up-oauth
    Preconditions.checkArgument(data.has("refresh_token"),
            "Missing 'refresh_token' in query params from %s", ACCESS_TOKEN_URL);
    return Map.of("refresh_token", data.get("refresh_token").asText());
  }

//  protected Map<String, Object> completeOAuthFlow(final String clientId,
//                                                  final String clientSecret,
//                                                  final String authCode,
//                                                  final String redirectUrl,
//                                                  final JsonNode oAuthParamConfig)
//          throws IOException {
//    final var result = super.completeOAuthFlow(clientId, clientSecret, authCode, redirectUrl, oAuthParamConfig);
//    // Refresh token can be used throughout 1 year but for this we need to forward client_id/client_secret additionally
//    return Map.of(
//            "client_secret", clientSecret,
//            "client_id", clientId,
//            "refresh_token", (String)result.get("refresh_token")
//    );
//  }

}
