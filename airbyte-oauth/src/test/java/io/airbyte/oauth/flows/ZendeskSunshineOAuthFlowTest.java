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

public class ZendeskSunshineOAuthFlowTest extends BaseOAuthFlowTest {

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
  public void testEmptyOutputCompleteSourceOAuth() {}

  @Test
  @Override
  public void testGetSourceConsentUrlEmptyOAuthSpec() {}

  @Test
  @Override
  public void testValidateOAuthOutputFailure() {}

  @Test
  @Override
  public void testCompleteSourceOAuth() {}

  @Test
  @Override
  public void testEmptyInputCompleteDestinationOAuth() {}

  @Test
  @Override
  public void testDeprecatedCompleteDestinationOAuth() {}

  @Test
  @Override
  public void testDeprecatedCompleteSourceOAuth() {}

  @Test
  @Override
  public void testEmptyOutputCompleteDestinationOAuth() {}

  @Test
  @Override
  public void testCompleteDestinationOAuth() {}

  @Test
  @Override
  public void testGetDestinationConsentUrlEmptyOAuthSpec() {}

  @Test
  @Override
  public void testEmptyInputCompleteSourceOAuth() {}

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
