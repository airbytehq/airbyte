/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows.facebook;

import io.airbyte.config.persistence.ConfigRepository;

// Instagram Graph API require Facebook API User token
public class InstagramOAuthFlow extends FacebookMarketingOAuthFlow {

  private static final String SCOPES = "ads_management,instagram_basic,instagram_manage_insights,read_insights";

  public InstagramOAuthFlow(final ConfigRepository configRepository) {
    super(configRepository);
  }

  @Override
  protected String getScopes() {
    return SCOPES;
  }

}
