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

  public TrelloOAuthFlow(ConfigRepository configRepository) {
    super(configRepository);
    transport = new NetHttpTransport();
  }

  @VisibleForTesting
  public TrelloOAuthFlow(ConfigRepository configRepository, HttpTransport transport) {
    super(configRepository);
    this.transport = transport;
  }

  public String getSourceConsentUrl(UUID workspaceId, UUID sourceDefinitionId, String redirectUrl) throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getSourceOAuthParamConfig(workspaceId, sourceDefinitionId);
    return getConsentUrl(oAuthParamConfig, redirectUrl);
  }

  public String getDestinationConsentUrl(UUID workspaceId, UUID destinationDefinitionId, String redirectUrl)
      throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getDestinationOAuthParamConfig(workspaceId, destinationDefinitionId);
    return getConsentUrl(oAuthParamConfig, redirectUrl);
  }

  private String getConsentUrl(JsonNode oAuthParamConfig, String redirectUrl) throws IOException, ConfigNotFoundException {
    final String clientKey = getClientIdUnsafe(oAuthParamConfig);
    final String clientSecret = getClientSecretUnsafe(oAuthParamConfig);
    final OAuthGetTemporaryToken oAuthGetTemporaryToken = new OAuthGetTemporaryToken(REQUEST_TOKEN_URL);
    signer.clientSharedSecret = clientSecret;
    signer.tokenSharedSecret = null;
    oAuthGetTemporaryToken.signer = signer;
    oAuthGetTemporaryToken.callback = redirectUrl;
    oAuthGetTemporaryToken.transport = transport;
    oAuthGetTemporaryToken.consumerKey = clientKey;
    OAuthCredentialsResponse temporaryTokenResponse = oAuthGetTemporaryToken.execute();

    final OAuthAuthorizeTemporaryTokenUrl oAuthAuthorizeTemporaryTokenUrl = new OAuthAuthorizeTemporaryTokenUrl(AUTHENTICATE_URL);
    oAuthAuthorizeTemporaryTokenUrl.temporaryToken = temporaryTokenResponse.token;
    signer.tokenSharedSecret = temporaryTokenResponse.tokenSecret;
    return oAuthAuthorizeTemporaryTokenUrl.build();
  }

  public Map<String, Object> completeSourceOAuth(UUID workspaceId, UUID sourceDefinitionId, Map<String, Object> queryParams, String redirectUrl)
      throws IOException, ConfigNotFoundException {

    final JsonNode oAuthParamConfig = getSourceOAuthParamConfig(workspaceId, sourceDefinitionId);
    return completeOAuth(oAuthParamConfig, queryParams, redirectUrl);
  }

  public Map<String, Object> completeDestinationOAuth(UUID workspaceId,
                                                      UUID destinationDefinitionId,
                                                      Map<String, Object> queryParams,
                                                      String redirectUrl)
      throws IOException, ConfigNotFoundException {
    final JsonNode oAuthParamConfig = getDestinationOAuthParamConfig(workspaceId, destinationDefinitionId);
    return completeOAuth(oAuthParamConfig, queryParams, redirectUrl);
  }

  private Map<String, Object> completeOAuth(JsonNode oAuthParamConfig, Map<String, Object> queryParams, String redirectUrl)
      throws IOException, ConfigNotFoundException {
    final String clientKey = getClientIdUnsafe(oAuthParamConfig);
    if (!queryParams.containsKey("oauth_verifier") || !queryParams.containsKey("oauth_token")) {
      throw new IOException(
          "Undefined " + (!queryParams.containsKey("oauth_verifier") ? "oauth_verifier" : "oauth_token") + " from consent redirected url.");
    }
    String temporaryToken = (String) queryParams.get("oauth_token");
    String verificationCode = (String) queryParams.get("oauth_verifier");
    final OAuthGetAccessToken oAuthGetAccessToken = new OAuthGetAccessToken(ACCESS_TOKEN_URL);
    oAuthGetAccessToken.signer = signer;
    oAuthGetAccessToken.transport = transport;
    oAuthGetAccessToken.temporaryToken = temporaryToken;
    oAuthGetAccessToken.verifier = verificationCode;
    oAuthGetAccessToken.consumerKey = clientKey;
    OAuthCredentialsResponse accessTokenResponse = oAuthGetAccessToken.execute();
    String accessToken = accessTokenResponse.token;
    return Map.of("token", accessToken, "key", clientKey);
  }

}
