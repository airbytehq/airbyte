/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows.google;

import io.airbyte.oauth.BaseOAuthFlow;
import io.airbyte.oauth.flows.BaseOAuthFlowTest;
import java.util.List;

public class GoogleBigQueryOAuthFlowTest extends BaseOAuthFlowTest {

  @Override
  protected BaseOAuthFlow getOAuthFlow() {
    return new GoogleBigQueryOAuthFlow(getConfigRepository(), getHttpClient(), this::getConstantState);
  }

  @Override
  protected String getExpectedConsentUrl() {
    return "https://accounts.google.com/o/oauth2/v2/auth?client_id=test_client_id&redirect_uri=https%3A%2F%2Fairbyte.io&response_type=code&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fbigquery+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdevstorage.read_write&access_type=offline&state=state&include_granted_scopes=true&prompt=consent";
  }
}
