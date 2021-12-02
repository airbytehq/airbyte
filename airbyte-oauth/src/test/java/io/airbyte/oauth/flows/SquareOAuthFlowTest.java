/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import io.airbyte.oauth.BaseOAuthFlow;

public class SquareOAuthFlowTest extends BaseOAuthFlowTest {

  @Override
  protected BaseOAuthFlow getOAuthFlow() {
    return new SquareOAuthFlow(getConfigRepository(), getHttpClient(), this::getConstantState);
  }

  @Override
  protected String getExpectedConsentUrl() {
    return "https://connect.squareup.com/oauth2/authorize?client_id=test_client_id&scope=ITEMS_READ"
        + "+CUSTOMERS_WRITE+MERCHANT_PROFILE_READ+EMPLOYEES_READ+PAYMENTS_READ+CUSTOMERS_READ"
        + "+TIMECARDS_READ+ORDERS_READ&session=False&state=state";
  }

}
