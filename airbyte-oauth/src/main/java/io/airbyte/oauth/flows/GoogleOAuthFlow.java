/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.BaseOAuthFlow;
import java.io.IOException;
import java.net.http.HttpClient;
import java.util.Map;
import java.util.UUID;

/**
 * Following docs from https://developers.google.com/identity/protocols/oauth2/web-server
 */
public abstract class GoogleOAuthFlow extends BaseOAuthFlow {

  private final String consentUrl = "https://accounts.google.com/o/oauth2/v2/auth";
  private final String accessTokenUrl = "https://oauth2.googleapis.com/token";

  public GoogleOAuthFlow(ConfigRepository configRepository) {
    super(configRepository);
  }

  public GoogleOAuthFlow(ConfigRepository configRepository, HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @Override
  protected String getBaseConsentUrl() {
    return consentUrl;
  }

  @Override
  protected Map<String, String> getConsentQueryParameters(UUID definitionId, String clientId, String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        // required
        .put("client_id", clientId)
        .put("redirect_uri", redirectUrl)
        .put("response_type", "code")
        .put("scope", getScopeUrl())
        // recommended
        .put("access_type", "offline")
        .put("state", getState(definitionId))
        // optional
        .put("include_granted_scopes", "true")
        //.put("login_hint", "user_email")
        .put("prompt", "consent")
        .build();
  }

  protected abstract String getScopeUrl();

  @Override
  protected String extractCodeParameter(Map<String, Object> queryParams) throws IOException {
    if (queryParams.containsKey("code")) {
      return (String) queryParams.get("code");
    } else {
      throw new IOException("Undefined 'code' from consent redirected url.");
    }
  }

  @Override
  protected String getAccessTokenUrl() {
    return accessTokenUrl;
  }

  @Override
  protected Map<String, String> getAccessTokenQueryParameters(String clientId, String clientSecret, String authCode, String redirectUrl) {
    return ImmutableMap.<String, String>builder()
        .put("client_id", clientId)
        .put("client_secret", clientSecret)
        .put("code", authCode)
        .put("grant_type", "authorization_code")
        .put("redirect_uri", redirectUrl)
        .build();
  }

  @Override
  protected Map<String, Object> extractRefreshToken(JsonNode data) throws IOException {
    if (data.has("refresh_token")) {
      return Map.of("refresh_token", data.get("refresh_token").asText());
    } else {
      throw new IOException(String.format("Missing 'refresh_token' in query params from %s", accessTokenUrl));
    }
  }

}
