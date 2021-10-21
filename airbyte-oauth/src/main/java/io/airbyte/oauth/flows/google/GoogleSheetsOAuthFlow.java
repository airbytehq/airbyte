/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows.google;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.config.persistence.ConfigRepository;
import java.net.http.HttpClient;
import java.util.function.Supplier;

public class GoogleSheetsOAuthFlow extends GoogleOAuthFlow {

  // space-delimited string for multiple scopes, see:
  // https://datatracker.ietf.org/doc/html/rfc6749#section-3.3
  @VisibleForTesting
  static final String SCOPE_URL = "https://www.googleapis.com/auth/spreadsheets.readonly https://www.googleapis.com/auth/drive.readonly";

  public GoogleSheetsOAuthFlow(final ConfigRepository configRepository) {
    super(configRepository);
  }

  @VisibleForTesting
  GoogleSheetsOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String getScope() {
    return SCOPE_URL;
  }

  @Override
  protected String getClientIdUnsafe(final JsonNode config) {
    // the config object containing client ID and secret is nested inside the "credentials" object
    Preconditions.checkArgument(config.hasNonNull("credentials"));
    return super.getClientIdUnsafe(config.get("credentials"));
  }

  @Override
  protected String getClientSecretUnsafe(final JsonNode config) {
    // the config object containing client ID and secret is nested inside the "credentials" object
    Preconditions.checkArgument(config.hasNonNull("credentials"));
    return super.getClientSecretUnsafe(config.get("credentials"));
  }

}
