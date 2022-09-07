/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import io.airbyte.oauth.BaseOAuthFlow;
import java.util.List;

public class PinterestOAuthFlowTest extends BaseOAuthFlowTest {

  @Override
  protected BaseOAuthFlow getOAuthFlow() {
    return new PinterestOAuthFlow(getConfigRepository(), getHttpClient(), this::getConstantState);
  }

  @Override
  protected String getExpectedConsentUrl() {
    return "https://pinterest.com/oauth/client_id=test_client_id&redirect_uri=https%3A%2F%2Fairbyte.io&response_type=code&scope=ads:read,boards:read,boards:read_secret,catalogs:read,pins:read,pins:read_secret,user_accounts:read&state=state";
  }

  @Override
  protected List<String> getExpectedOutputPath() {
    return List.of("authorization");
  }

}
