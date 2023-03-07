/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
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
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.http.client.utils.URIBuilder;

public class PayPalTransactionOAuthFlow extends BaseOAuth2Flow {

  private static final String AUTHORIZE_URL = "https://www.paypal.com/connect";
  private static final String ACCESS_TOKEN_URL = "https://api-m.paypal.com/v1/oauth2/token";
  private static final String SCOPES = "openid email profile";

  public PayPalTransactionOAuthFlow(ConfigRepository configRepository, HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @VisibleForTesting
  public PayPalTransactionOAuthFlow(ConfigRepository configRepository, final HttpClient httpClient, Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String formatConsentUrl(UUID definitionId,
                                    String clientId,
                                    String redirectUrl,
                                    final JsonNode inputOAuthConfiguration)
      throws IOException {
    try {
      return new URIBuilder(AUTHORIZE_URL)
          .addParameter("flowEntry", "static")
          .addParameter("client_id", clientId)
          .addParameter("response_type", "code")
          .addParameter("scope", SCOPES)
          .addParameter("redirect_uri", redirectUrl)
          .addParameter("state", getState())
          .build().toString();
    } catch (URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  @Override
  protected String getAccessTokenUrl(final JsonNode inputOAuthConfiguration) {
    return ACCESS_TOKEN_URL;
  }

  @Override
  protected Map<String, Object> completeOAuthFlow(final String clientId,
                                                  final String clientSecret,
                                                  final String authCode,
                                                  final String redirectUrl,
                                                  final JsonNode inputOAuthConfiguration,
                                                  final JsonNode oAuthParamConfig)
      throws IOException {
    final var accessTokenUrl = getAccessTokenUrl(inputOAuthConfiguration);
    final String authorization = Base64.getEncoder()
        .encodeToString((clientId + ":" + clientSecret).getBytes(StandardCharsets.UTF_8));
    final HttpRequest request = HttpRequest.newBuilder()
        .POST(HttpRequest.BodyPublishers
            .ofString(tokenReqContentType.getConverter().apply(
                getAccessTokenQueryParameters(clientId, clientSecret, authCode, redirectUrl))))
        .uri(URI.create(accessTokenUrl))
        .header("Content-Type", tokenReqContentType.getContentType())
        .header("Authorization", "Basic " + authorization)
        .build();

    try {
      final HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
      return extractOAuthOutput(Jsons.deserialize(response.body()), accessTokenUrl);
    } catch (final InterruptedException e) {
      throw new IOException("Failed to complete PayPal OAuth flow", e);
    }
  }

  @Override
  protected Map<String, String> getAccessTokenQueryParameters(final String clientId,
                                                              final String clientSecret,
                                                              final String authCode,
                                                              final String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        .put("grant_type", "authorization_code")
        .put("code", authCode)
        .build();
  }

}
