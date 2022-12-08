/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.oauth.BaseOAuthFlow;
import io.airbyte.oauth.MoreOAuthParameters;
import java.util.Map;
import org.junit.jupiter.api.Test;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class GitlabOAuthFlowTest extends BaseOAuthFlowTest {

  @Override
  protected BaseOAuthFlow getOAuthFlow() {
    return new GitlabOAuthFlow(getConfigRepository(), getHttpClient(), this::getConstantState);
  }

  @Override
  protected String getExpectedConsentUrl() {
    return "https://gitlab.com/oauth/authorize?client_id=test_client_id&redirect_uri=https%3A%2F%2Fairbyte.io&state=state&response_type=code&scope=read_api";
  }

  @Override
  protected JsonNode getCompleteOAuthOutputSpecification() {
    return getJsonSchema(Map.of(
        "access_token", Map.of("type", "string"),
        "refresh_token", Map.of("type", "string")));
  }

  @Override
  protected JsonNode getInputOAuthConfiguration() {
    return Jsons.jsonNode(Map.of("domain", "gitlab.com"));
  }

  @Override
  protected JsonNode getUserInputFromConnectorConfigSpecification() {
    return getJsonSchema(Map.of("domain", Map.of("type", "string")));
  }

  @Override
  protected Map<String, String> getExpectedOutput() {
    return Map.of(
        "refresh_token", "refresh_token_response",
        "access_token", "access_token_response",
        "client_id", MoreOAuthParameters.SECRET_MASK,
        "client_secret", MoreOAuthParameters.SECRET_MASK);
  }

  @Override
  protected Map<String, String> getExpectedFilteredOutput() {
    return Map.of(
        "refresh_token", "refresh_token_response",
        "access_token", "access_token_response",
        "client_id", MoreOAuthParameters.SECRET_MASK);
  }

  @Test
  @Override
  void testEmptyInputCompleteDestinationOAuth() {}

  @Test
  @Override
  void testDeprecatedCompleteDestinationOAuth() {}

  @Test
  @Override
  void testEmptyOutputCompleteDestinationOAuth() {}

  @Test
  @Override
  void testCompleteDestinationOAuth() {}

  @Test
  @Override
  void testGetDestinationConsentUrlEmptyOAuthSpec() {}

  @Test
  @Override
  void testGetDestinationConsentUrl() {}

}
