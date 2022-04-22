/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows.google;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.persistence.ConfigRepository;
import java.net.http.HttpClient;
import java.util.function.Supplier;

public class GoogleBigQueryOAuthFlow extends GoogleOAuthFlow {

  @VisibleForTesting
  static final String SCOPE_URL = "https://www.googleapis.com/auth/bigquery https://www.googleapis.com/auth/devstorage.read_write";

  public GoogleBigQueryOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @VisibleForTesting
  GoogleBigQueryOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String getScope() {
    return SCOPE_URL;
  }

}
