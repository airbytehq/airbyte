/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import io.airbyte.oauth.BaseOAuthFlow;

public class MailchimpOAuthFlowTest extends BaseOAuthFlowTest {

  @Override
  protected BaseOAuthFlow getOAuthFlow() {
    return new MailchimpOAuthFlow(getConfigRepository(), getHttpClient(), this::getConstantState);
  }

  @Override
  protected String getExpectedConsentUrl() {
    return "https://login.mailchimp.com/oauth2/authorize?client_id=test_client_id&redirect_uri=https%3A%2F%2Fairbyte.io&response_type=code";
  }

}
