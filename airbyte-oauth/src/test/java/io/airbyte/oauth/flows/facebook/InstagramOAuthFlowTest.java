/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows.facebook;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.oauth.BaseOAuthFlow;
import io.airbyte.oauth.MoreOAuthParameters;
import io.airbyte.oauth.flows.BaseOAuthFlowTest;
import java.util.List;
import java.util.Map;

public class InstagramOAuthFlowTest extends BaseOAuthFlowTest {

  @Override
  protected BaseOAuthFlow getOAuthFlow() {
    return new InstagramOAuthFlow(getConfigRepository(), getHttpClient(), this::getConstantState);
  }

  @Override
  protected String getExpectedConsentUrl() {
    return "https://www.facebook.com/v12.0/dialog/oauth?client_id=test_client_id&redirect_uri=https%3A%2F%2Fairbyte.io&state=state&scope=ads_management%2Cinstagram_basic%2Cinstagram_manage_insights%2Cpages_show_list%2Cpages_read_engagement";
  }

  @Override
  protected List<String> getExpectedOutputPath() {
    return List.of();
  }

  @Override
  protected Map<String, String> getExpectedOutput() {
    return Map.of(
        "access_token", "access_token_response",
        "client_id", MoreOAuthParameters.SECRET_MASK,
        "client_secret", MoreOAuthParameters.SECRET_MASK);
  }

  @Override
  protected JsonNode getCompleteOAuthOutputSpecification() {
    return getJsonSchema(Map.of("access_token", Map.of("type", "string")));
  }

  @Override
  protected Map<String, String> getExpectedFilteredOutput() {
    return Map.of(
        "access_token", "access_token_response",
        "client_id", MoreOAuthParameters.SECRET_MASK);
  }

}
