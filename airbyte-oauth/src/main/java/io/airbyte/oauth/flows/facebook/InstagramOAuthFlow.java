/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows.facebook;

import io.airbyte.config.persistence.ConfigRepository;
import java.net.http.HttpClient;

// Instagram Graph API require Facebook API User token
public class InstagramOAuthFlow extends FacebookMarketingOAuthFlow {

  private static final String SCOPES = "ads_management,instagram_basic,instagram_manage_insights,read_insights";

  public InstagramOAuthFlow(final ConfigRepository configRepository, final HttpClient httpClient) {
    super(configRepository, httpClient);
  }

  @Override
  protected String getScopes() {
    return SCOPES;
  }

}
