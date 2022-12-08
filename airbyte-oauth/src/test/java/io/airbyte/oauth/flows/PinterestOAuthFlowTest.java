/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.oauth.BaseOAuthFlow;
import io.airbyte.oauth.MoreOAuthParameters;
import java.util.Map;
import org.junit.jupiter.api.Test;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class PinterestOAuthFlowTest extends BaseOAuthFlowTest {

  @Override
  protected BaseOAuthFlow getOAuthFlow() {
    return new PinterestOAuthFlow(getConfigRepository(), getHttpClient(), this::getConstantState);
  }

  @Override
  protected String getExpectedConsentUrl() {
    return "https://pinterest.com/oauth?client_id=test_client_id&redirect_uri=https%3A%2F%2Fairbyte.io&response_type=code&scope=ads%3Aread%2Cboards%3Aread%2Cboards%3Aread_secret%2Ccatalogs%3Aread%2Cpins%3Aread%2Cpins%3Aread_secret%2Cuser_accounts%3Aread&state=state";
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
