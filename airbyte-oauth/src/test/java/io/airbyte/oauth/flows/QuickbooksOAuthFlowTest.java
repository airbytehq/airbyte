/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import io.airbyte.oauth.BaseOAuthFlow;

public class QuickbooksOAuthFlowTest extends BaseOAuthFlowTest {

  @Override
  protected BaseOAuthFlow getOAuthFlow() {
    return new QuickbooksOAuthFlow(getConfigRepository(), getHttpClient(), this::getConstantState);
  }

  @Override
  protected String getExpectedConsentUrl() {
    return "https://appcenter.intuit.com/app/connect/oauth2?client_id=test_client_id&scope=com.intuit.quickbooks.accounting&redirect_uri=https%3A%2F%2Fairbyte.io&response_type=code&state=state";
  }

}
