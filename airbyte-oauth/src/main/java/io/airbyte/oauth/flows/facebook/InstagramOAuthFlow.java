/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows.facebook;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.persistence.ConfigRepository;
import java.net.http.HttpClient;
import java.util.function.Supplier;

// Instagram Graph API require Facebook API User token
public class InstagramOAuthFlow extends FacebookMarketingOAuthFlow {

  private static final String SCOPES = "ads_management,instagram_basic,instagram_manage_insights,pages_show_list,pages_read_engagement";

  public InstagramOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @VisibleForTesting
  InstagramOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient, final Supplier<String> stateSupplier) {
    super(configRepository, httpClient, stateSupplier);
  }

  @Override
  protected String getScopes() {
    return SCOPES;
  }

}
