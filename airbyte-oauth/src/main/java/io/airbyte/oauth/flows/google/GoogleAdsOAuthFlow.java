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
import java.util.Map;
import java.util.function.Supplier;

public class GoogleAdsOAuthFlow extends GoogleOAuthFlow {

  @VisibleForTesting
  static final String SCOPE_URL = "https://www.googleapis.com/auth/adwords";

  public GoogleAdsOAuthFlow(ConfigRepository configRepository) {
    super(configRepository);
  }

  @VisibleForTesting
  GoogleAdsOAuthFlow(ConfigRepository configRepository, HttpClient httpClient, Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String getScope() {
    return SCOPE_URL;
  }

  @Override
  protected String getClientIdUnsafe(JsonNode config) {
    // the config object containing client ID and secret is nested inside the "credentials" object
    Preconditions.checkArgument(config.hasNonNull("credentials"));
    return super.getClientIdUnsafe(config.get("credentials"));
  }

  @Override
  protected String getClientSecretUnsafe(JsonNode config) {
    // the config object containing client ID and secret is nested inside the "credentials" object
    Preconditions.checkArgument(config.hasNonNull("credentials"));
    return super.getClientSecretUnsafe(config.get("credentials"));
  }

  @Override
  protected Map<String, Object> extractRefreshToken(JsonNode data) throws IOException {
    // the config object containing refresh token is nested inside the "credentials" object
    return Map.of("credentials", super.extractRefreshToken(data));
  }

}
