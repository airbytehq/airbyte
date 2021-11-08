/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuthFlow;
import java.io.IOException;
import java.net.URISyntaxException;
import java.net.URLDecoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Map;
import java.util.UUID;
import org.apache.http.NameValuePair;
import org.apache.http.client.utils.URIBuilder;
import org.apache.http.message.BasicNameValuePair;

public class QuickbooksOAuthFlow extends BaseOAuthFlow {

  final String CONSENT_URL = "https://appcenter.intuit.com/app/connect/oauth2";
  final String TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer";

  public QuickbooksOAuthFlow(ConfigRepository configRepository, HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  public String getScopes() {
    return "com.intuit.quickbooks.accounting";
  }

  /**
   * Depending on the OAuth flow implementation, the URL to grant user's consent may differ,
   * especially in the query parameters to be provided. This function should generate such consent URL
   * accordingly.
   *
   * @param definitionId
   * @param clientId
   * @param redirectUrl
   */
  @Override
  protected String formatConsentUrl(UUID definitionId, String clientId, String redirectUrl) throws IOException {
    try {
      return URLDecoder.decode(
          new URIBuilder(CONSENT_URL)
              .addParameter("client_id", clientId)
              .addParameter("scope", getScopes())
              .addParameter("redirect_uri", redirectUrl)
              .addParameter("response_type", "code")
              .addParameter("state", getState())

              .build().toString(),
          StandardCharsets.UTF_8.toString());
    } catch (final URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  protected Map<String, Object> completeOAuthFlow(final String clientId,
                                                  final String clientSecret,
                                                  final String authCode,
                                                  final String redirectUrl,
                                                  JsonNode oAuthParamConfig)
      throws IOException {
    var accessTokenUrl = getAccessTokenUrl();
    try {
      var parametersMap = getAccessTokenQueryParameters(clientId, clientSecret, authCode, redirectUrl);
      var queryParameters = new ArrayList<NameValuePair>(parametersMap.size());
      for (var entry : parametersMap.entrySet()) {
        queryParameters.add(new BasicNameValuePair(entry.getKey(), entry.getValue()));
      }
      final HttpRequest request = HttpRequest.newBuilder()
          .POST(HttpRequest.BodyPublishers
              .ofString(getTokenReqContentType().getConverter().apply(getAccessTokenQueryParameters(clientId, clientSecret, authCode, redirectUrl))))
          .uri(new URIBuilder(getAccessTokenUrl()).addParameters(queryParameters).build())
          .header("Content-Type", getTokenReqContentType().getContentType())
          .header("Accept", "application/json")
          .build();

      HttpResponse<String> response;
      response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
      return extractRefreshToken(Jsons.deserialize(response.body()), accessTokenUrl);
    } catch (final InterruptedException | URISyntaxException e) {
      throw new IOException("Failed to complete OAuth flow", e);
    }
  }

  /**
   * Returns the URL where to retrieve the access token from.
   */
  @Override
  protected String getAccessTokenUrl() {
    return TOKEN_URL;
  }

}
