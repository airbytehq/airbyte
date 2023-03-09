/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.oauth.BaseOAuthFlow;
import io.airbyte.oauth.MoreOAuthParameters;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneId;
import java.util.Map;
import org.junit.jupiter.api.Test;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class GitlabOAuthFlowTest extends BaseOAuthFlowTest {

  @Override
  protected BaseOAuthFlow getOAuthFlow() {
    final Clock clock = Clock.fixed(Instant.ofEpochSecond(1673464409), ZoneId.of("UTC"));
    return new GitlabOAuthFlow(getConfigRepository(), getHttpClient(), this::getConstantState, clock);
  }

  @Override
  protected String getExpectedConsentUrl() {
    return "https://gitlab.com/oauth/authorize?client_id=test_client_id&redirect_uri=https%3A%2F%2Fairbyte.io&state=state&response_type=code&scope=read_api";
  }

  @Override
  @SuppressWarnings("PMD.AvoidDuplicateLiterals")
  protected JsonNode getCompleteOAuthOutputSpecification() {
    return getJsonSchema(Map.of(
        "token_expiry_date", Map.of("type", "string"),
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
        "expires_in", "720",
        "refresh_token", "refresh_token_response",
        "access_token", "access_token_response",
        "client_id", MoreOAuthParameters.SECRET_MASK,
        "client_secret", MoreOAuthParameters.SECRET_MASK);
  }

  @Override
  protected Map<String, String> getExpectedFilteredOutput() {
    return Map.of(
        "token_expiry_date", "2023-01-11T19:25:29Z",
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
