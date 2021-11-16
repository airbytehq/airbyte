/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
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

public class TypeformOAuthFlow extends BaseOAuth2Flow {

  private static final String AUTHORIZE_URL = "https://api.typeform.com/oauth/authorize";
  private static final String ACCESS_TOKEN_URL = "https://api.typeform.com/oauth/token";

  public TypeformOAuthFlow(ConfigRepository configRepository, HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @VisibleForTesting
  public TypeformOAuthFlow(ConfigRepository configRepository, final HttpClient httpClient, Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String formatConsentUrl(UUID definitionId, String clientId, String redirectUrl) throws IOException {
    try {
      return new URIBuilder(AUTHORIZE_URL)
          .addParameter("client_id", clientId)
          .addParameter("redirect_uri", redirectUrl)
          .addParameter("response_type", "code")
          .addParameter("state", getState())
          .addParameter("scope", getScopes())
          .build().toString();
    } catch (URISyntaxException e) {
      throw new IOException("Failed to format Consent URL for OAuth flow", e);
    }
  }

  private String getScopes() {
    return String.join(" ", "forms:read",
        "responses:read");
  }

  @Override
  protected String getAccessTokenUrl() {
    return ACCESS_TOKEN_URL;
  }

  @Override
  protected Map<String, Object> extractOAuthOutput(final JsonNode data, final String accessTokenUrl) {
    Preconditions.checkArgument(data.has("access_token"), "Missing 'access_token' in query params from %s", ACCESS_TOKEN_URL);
    return Map.of("token", data.get("access_token").asText());
  }

  @Override
  protected List<String> getDefaultOAuthOutputPath() {
    return List.of();
  }

}
