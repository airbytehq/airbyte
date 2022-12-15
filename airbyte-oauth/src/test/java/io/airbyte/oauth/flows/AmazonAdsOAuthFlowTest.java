/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import io.airbyte.oauth.BaseOAuthFlow;

public class AmazonAdsOAuthFlowTest extends BaseOAuthFlowTest {

  @Override
  protected BaseOAuthFlow getOAuthFlow() {
    return new AmazonAdsOAuthFlow(getConfigRepository(), getHttpClient(), this::getConstantState);
  }

  @Override
  protected String getExpectedConsentUrl() {
    return "https://www.amazon.com/ap/oa?client_id=test_client_id&scope=advertising%3A%3Acampaign_management&response_type=code&redirect_uri=https%3A%2F%2Fairbyte.io&state=state";
  }

}
