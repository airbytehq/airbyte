/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows.facebook;

import io.airbyte.config.persistence.ConfigRepository;

public class FacebookPagesOAuthFlow extends FacebookOAuthFlow {

  private static final String SCOPES = "pages_manage_ads,pages_manage_metadata,pages_read_engagement,pages_read_user_content";

  public FacebookPagesOAuthFlow(final ConfigRepository configRepository) {
    super(configRepository);
  }

  @Override
  protected String getScopes() {
    return SCOPES;
  }

}
