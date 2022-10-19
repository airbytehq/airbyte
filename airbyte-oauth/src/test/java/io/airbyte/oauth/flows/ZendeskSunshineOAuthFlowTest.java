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
class ZendeskSunshineOAuthFlowTest extends BaseOAuthFlowTest {

  @Override
  protected BaseOAuthFlow getOAuthFlow() {
    return new ZendeskSunshineOAuthFlow(getConfigRepository(), getHttpClient(), this::getConstantState);
  }

  @Override
  protected String getExpectedConsentUrl() {
    return "https://test_subdomain.zendesk.com/oauth/authorizations/new?response_type=code&redirect_uri=https%3A%2F%2Fairbyte.io&client_id=test_client_id&scope=read&state=state";
  }

  @Override
  protected JsonNode getInputOAuthConfiguration() {
    return Jsons.jsonNode(Map.of("subdomain", "test_subdomain"));
  }

  @Override
  protected JsonNode getUserInputFromConnectorConfigSpecification() {
    return getJsonSchema(Map.of("subdomain", Map.of("type", "string")));
  }

  @Test
  @Override
  void testEmptyOutputCompleteSourceOAuth() {}

  @Test
  @Override
  void testGetSourceConsentUrlEmptyOAuthSpec() {}

  @Test
  @Override
  void testValidateOAuthOutputFailure() {}

  @Test
  @Override
  void testCompleteSourceOAuth() {}

  @Test
  @Override
  void testEmptyInputCompleteDestinationOAuth() {}

  @Test
  @Override
  void testDeprecatedCompleteDestinationOAuth() {}

  @Test
  @Override
  void testDeprecatedCompleteSourceOAuth() {}

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
  void testEmptyInputCompleteSourceOAuth() {}

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
