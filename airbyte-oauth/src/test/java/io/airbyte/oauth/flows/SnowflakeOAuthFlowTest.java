/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.oauth.BaseOAuthFlow;
import io.airbyte.oauth.MoreOAuthParameters;
import java.util.Map;
import org.junit.jupiter.api.Test;

public class SnowflakeOAuthFlowTest extends BaseOAuthFlowTest {

  @Override
  protected BaseOAuthFlow getOAuthFlow() {
    return new SourceSnowflakeOAuthFlow(getConfigRepository(), getHttpClient(), this::getConstantState);
  }

  @Override
  protected String getExpectedConsentUrl() {
    return "https://account.aws.snowflakecomputing.com/oauth/authorize?client_id=test_client_id&redirect_uri=https%3A%2F%2Fairbyte.io&response_type=code&state=state";
  }

  @Override
  protected Map<String, String> getExpectedOutput() {
    return Map.of(
        "access_token", "access_token_response",
        "refresh_token", "refresh_token_response",
        "username", "username");
  }

  @Override
  protected JsonNode getCompleteOAuthOutputSpecification() {
    return getJsonSchema(Map.of("access_token", Map.of("type", "string"), "refresh_token", Map.of("type", "string")));
  }

  @Override
  protected Map<String, String> getExpectedFilteredOutput() {
    return Map.of(
        "access_token", "access_token_response",
        "refresh_token", "refresh_token_response",
        "client_id", MoreOAuthParameters.SECRET_MASK);
  }

  protected JsonNode getOAuthParamConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("client_id", "test_client_id")
        .put("client_secret", "test_client_secret")
        .build());
  }

  @Override
  protected JsonNode getInputOAuthConfiguration() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", "account.aws.snowflakecomputing.com")
        .build());
  }

  protected JsonNode getUserInputFromConnectorConfigSpecification() {
    return getJsonSchema(Map.of("host", Map.of("type", "string")));
  }

  @Test
  public void testGetSourceConsentUrlEmptyOAuthSpec() {}

  @Test
  public void testGetDestinationConsentUrlEmptyOAuthSpec() {}

  @Test
  public void testDeprecatedCompleteDestinationOAuth() {}

  @Test
  public void testDeprecatedCompleteSourceOAuth() {}

}
