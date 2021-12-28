/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import io.airbyte.oauth.BaseOAuthFlow;

public class MondayOAuthFlowTest extends BaseOAuthFlowTest {

  @Override
  protected BaseOAuthFlow getOAuthFlow() {
    return new MondayOAuthFlow(getConfigRepository(), getHttpClient(), this::getConstantState);
  }

  @Override
  protected String getExpectedConsentUrl() {
    return "https://auth.monday.com/oauth2/authorize?client_id=test_client_id&redirect_uri=https%3A%2F%2Fairbyte.io&state=state&scope=me:read%20boards:read%20workspaces:read%20users:read%20account:read%20updates:read%20assets:read%20tags:read%20teams:read";
  }

}
