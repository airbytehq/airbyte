/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.oauth.BaseOAuthFlow;
import io.airbyte.protocol.models.OAuthConfigSpecification;
import java.util.Map;
import org.junit.jupiter.api.Test;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class TikTokMarketingOAuthFlowTest extends BaseOAuthFlowTest {

  @Override
  protected BaseOAuthFlow getOAuthFlow() {
    return new TikTokMarketingOAuthFlow(getConfigRepository(), getHttpClient(), this::getConstantState);
  }

  @Override
  protected String getExpectedConsentUrl() {
    return "https://ads.tiktok.com/marketing_api/auth?app_id=app_id" +
        "&redirect_uri=https%3A%2F%2Fairbyte.io" +
        "&state=state";
  }

  @Override
  protected JsonNode getOAuthParamConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("app_id", "app_id")
        .put("secret", "secret")
        .build());
  }

  @Override
  protected OAuthConfigSpecification getOAuthConfigSpecification() {
    return getoAuthConfigSpecification()
        // change property types to induce json validation errors.
        .withCompleteOauthServerOutputSpecification(getJsonSchema(Map.of("app_id", Map.of("type", "integer"))))
        .withCompleteOauthOutputSpecification(getJsonSchema(Map.of("access_token", Map.of("type", "integer"))));
  }

  @Override
  protected String getMockedResponse() {
    return "{\n"
        + "   \"data\":{\n"
        + "      \"access_token\":\"access_token_response\"\n"
        + "   }\n"
        + "}";
  }

  @Override
  protected JsonNode getCompleteOAuthOutputSpecification() {
    return getJsonSchema(Map.of("access_token", Map.of("type", "string")));
  }

  @Override
  protected Map<String, String> getExpectedFilteredOutput() {
    return Map.of("access_token", "access_token_response");
  }

  @Test
  @Override
  void testDeprecatedCompleteDestinationOAuth() {}

  @Test
  @Override
  void testDeprecatedCompleteSourceOAuth() {}

}
