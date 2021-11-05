/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.client.auth.oauth.OAuthAuthorizeTemporaryTokenUrl;
import com.google.api.client.auth.oauth.OAuthCredentialsResponse;
import com.google.api.client.auth.oauth.OAuthGetAccessToken;
import com.google.api.client.auth.oauth.OAuthGetTemporaryToken;
import com.google.api.client.auth.oauth.OAuthHmacSigner;
import com.google.api.client.http.HttpTransport;
import com.google.api.client.http.javanet.NetHttpTransport;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuthConfig;
import java.io.IOException;
import java.net.http.HttpClient;
import java.util.Map;
import java.util.UUID;

/*
 * Following docs from
 * https://developer.atlassian.com/cloud/trello/guides/rest-api/authorization/#using-basic-oauth
 */
public class TrelloOAuthFlow extends BaseOAuthConfig {

  private static final String REQUEST_TOKEN_URL = "https://trello.com/1/OAuthGetRequestToken";
  private static final String AUTHENTICATE_URL = "https://trello.com/1/OAuthAuthorizeToken";
  private static final String ACCESS_TOKEN_URL = "https://trello.com/1/OAuthGetAccessToken";

  // Airbyte webserver creates new TrelloOAuthFlow class instance for every API
  // call. Since oAuth 1.0 workflow requires data from previous step to build
  // correct signature.
  // Use static signer instance to share token secret for oAuth flow between
  // get_consent_url and complete_oauth API calls.
  private static final OAuthHmacSigner signer = new OAuthHmacSigner();
  private final HttpTransport transport;

  public TrelloOAuthFlow(final ConfigRepository configRepository, HttpClient httpClient) {
    super(configRepository);
    transport = new NetHttpTransport();
  }

  @VisibleForTesting
  public TrelloOAuthFlow(final ConfigRepository configRepository, final HttpTransport transport) {
    super(configRepository);
    this.transport = transport;
  }

  public String getSourceConsentUrl(final UUID workspaceId, final UUID sourceDefinitionId, final String redirectUrl)
      throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getSourceOAuthParamConfig(workspaceId, sourceDefinitionId);
    return getConsentUrl(oAuthParamConfig, redirectUrl);
  }

  public String getDestinationConsentUrl(final UUID workspaceId, final UUID destinationDefinitionId, final String redirectUrl)
      throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getDestinationOAuthParamConfig(workspaceId, destinationDefinitionId);
    return getConsentUrl(oAuthParamConfig, redirectUrl);
  }

  private String getConsentUrl(final JsonNode oAuthParamConfig, final String redirectUrl) throws IOException, ConfigNotFoundException {
    final String clientKey = getClientIdUnsafe(oAuthParamConfig);
    final String clientSecret = getClientSecretUnsafe(oAuthParamConfig);
    final OAuthGetTemporaryToken oAuthGetTemporaryToken = new OAuthGetTemporaryToken(REQUEST_TOKEN_URL);
    signer.clientSharedSecret = clientSecret;
    signer.tokenSharedSecret = null;
    oAuthGetTemporaryToken.signer = signer;
    oAuthGetTemporaryToken.callback = redirectUrl;
    oAuthGetTemporaryToken.transport = transport;
    oAuthGetTemporaryToken.consumerKey = clientKey;
    final OAuthCredentialsResponse temporaryTokenResponse = oAuthGetTemporaryToken.execute();

    final OAuthAuthorizeTemporaryTokenUrl oAuthAuthorizeTemporaryTokenUrl = new OAuthAuthorizeTemporaryTokenUrl(AUTHENTICATE_URL);
    oAuthAuthorizeTemporaryTokenUrl.temporaryToken = temporaryTokenResponse.token;
    signer.tokenSharedSecret = temporaryTokenResponse.tokenSecret;
    return oAuthAuthorizeTemporaryTokenUrl.build();
  }

  public Map<String, Object> completeSourceOAuth(
                                                 final UUID workspaceId,
                                                 final UUID sourceDefinitionId,
                                                 final Map<String, Object> queryParams,
                                                 final String redirectUrl)
      throws IOException, ConfigNotFoundException {

    final JsonNode oAuthParamConfig = getSourceOAuthParamConfig(workspaceId, sourceDefinitionId);
    return completeOAuth(oAuthParamConfig, queryParams, redirectUrl);
  }

  public Map<String, Object> completeDestinationOAuth(final UUID workspaceId,
                                                      final UUID destinationDefinitionId,
                                                      final Map<String, Object> queryParams,
                                                      final String redirectUrl)
      throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getDestinationOAuthParamConfig(workspaceId, destinationDefinitionId);
    return completeOAuth(oAuthParamConfig, queryParams, redirectUrl);
  }

  private Map<String, Object> completeOAuth(final JsonNode oAuthParamConfig, final Map<String, Object> queryParams, final String redirectUrl)
      throws IOException, ConfigNotFoundException {
    final String clientKey = getClientIdUnsafe(oAuthParamConfig);
    if (!queryParams.containsKey("oauth_verifier") || !queryParams.containsKey("oauth_token")) {
      throw new IOException(
          "Undefined " + (!queryParams.containsKey("oauth_verifier") ? "oauth_verifier" : "oauth_token") + " from consent redirected url.");
    }
    final String temporaryToken = (String) queryParams.get("oauth_token");
    final String verificationCode = (String) queryParams.get("oauth_verifier");
    final OAuthGetAccessToken oAuthGetAccessToken = new OAuthGetAccessToken(ACCESS_TOKEN_URL);
    oAuthGetAccessToken.signer = signer;
    oAuthGetAccessToken.transport = transport;
    oAuthGetAccessToken.temporaryToken = temporaryToken;
    oAuthGetAccessToken.verifier = verificationCode;
    oAuthGetAccessToken.consumerKey = clientKey;
    final OAuthCredentialsResponse accessTokenResponse = oAuthGetAccessToken.execute();
    final String accessToken = accessTokenResponse.token;
    return Map.of("token", accessToken, "key", clientKey);
  }

}
