/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows.google;

import io.airbyte.oauth.BaseOAuthFlow;
import io.airbyte.oauth.flows.BaseOAuthFlowTest;

public class GoogleAnalyticsOAuthFlowTest extends BaseOAuthFlowTest {

  @Override
  protected BaseOAuthFlow getOAuthFlow() {
    return new GoogleAnalyticsViewIdOAuthFlow(getConfigRepository(), getHttpClient(), this::getConstantState);
  }

  @Override
  protected String getExpectedConsentUrl() {
    return "https://accounts.google.com/o/oauth2/v2/auth?client_id=test_client_id&redirect_uri=https%3A%2F%2Fairbyte.io&response_type=code&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fanalytics.readonly&access_type=offline&state=state&include_granted_scopes=true&prompt=consent";
  }

}
