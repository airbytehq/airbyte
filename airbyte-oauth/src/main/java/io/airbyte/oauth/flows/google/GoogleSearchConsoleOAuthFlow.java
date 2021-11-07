/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows.google;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.config.persistence.ConfigRepository;
import java.io.IOException;
import java.net.http.HttpClient;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Supplier;

public class GoogleSearchConsoleOAuthFlow extends GoogleOAuthFlow {

  @VisibleForTesting
  static final String SCOPE_URL = "https://www.googleapis.com/auth/webmasters.readonly";

  public GoogleSearchConsoleOAuthFlow(final ConfigRepository configRepository, HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @VisibleForTesting
  GoogleSearchConsoleOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String getScope() {
    return SCOPE_URL;
  }

  @Override
  protected String getClientIdUnsafe(final JsonNode config) {
    // the config object containing client ID and secret is nested inside the "authorization" object
    Preconditions.checkArgument(config.hasNonNull("authorization"));
    return super.getClientIdUnsafe(config.get("authorization"));
  }

  @Override
  protected String getClientSecretUnsafe(final JsonNode config) {
    // the config object containing client ID and secret is nested inside the "authorization" object
    Preconditions.checkArgument(config.hasNonNull("authorization"));
    return super.getClientSecretUnsafe(config.get("authorization"));
  }

  @Override
  protected Map<String, Object> extractRefreshToken(final JsonNode data, String accessTokenUrl) throws IOException {
    // the config object containing refresh token is nested inside the "authorization" object
    final Map<String, Object> result = new HashMap<>();
    if (data.has("refresh_token")) {
      result.put("refresh_token", data.get("refresh_token").asText());
    }
    return Map.of("authorization", result);
  }

}
