/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.oauth.BaseOAuthFlow;
import java.util.Map;
import org.junit.jupiter.api.Test;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class MicrosoftTeamsOAuthFlowTest extends BaseOAuthFlowTest {

  @Override
  protected BaseOAuthFlow getOAuthFlow() {
    return new MicrosoftTeamsOAuthFlow(getConfigRepository(), getHttpClient(), this::getConstantState);
  }

  @Override
  protected String getExpectedConsentUrl() {
    return "https://login.microsoftonline.com/test_tenant_id/oauth2/v2.0/authorize?client_id=test_client_id&redirect_uri=https%3A%2F%2Fairbyte.io&state=state&scope=offline_access+Application.Read.All+Channel.ReadBasic.All+ChannelMember.Read.All+ChannelMember.ReadWrite.All+ChannelSettings.Read.All+ChannelSettings.ReadWrite.All+Directory.Read.All+Directory.ReadWrite.All+Files.Read.All+Files.ReadWrite.All+Group.Read.All+Group.ReadWrite.All+GroupMember.Read.All+Reports.Read.All+Sites.Read.All+Sites.ReadWrite.All+TeamsTab.Read.All+TeamsTab.ReadWrite.All+User.Read.All+User.ReadWrite.All&response_type=code";
  }

  @Override
  protected JsonNode getInputOAuthConfiguration() {
    return Jsons.jsonNode(Map.of("tenant_id", "test_tenant_id"));
  }

  @Override
  protected JsonNode getUserInputFromConnectorConfigSpecification() {
    return getJsonSchema(Map.of("tenant_id", Map.of("type", "string")));
  }

  @Test
  @Override
  void testEmptyInputCompleteSourceOAuth() {}

  @Test
  @Override
  void testEmptyInputCompleteDestinationOAuth() {}

}
