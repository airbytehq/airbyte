/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.OAuthFlowImplementation;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.http.HttpClient;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;

public class SnapchatMarketingOAuthFlowIntegrationTest extends OAuthFlowIntegrationTest {

  @Override
  protected Path getCredentialsPath() {
    return Path.of("secrets/snapchat.json");
  }

  @Override
  protected String getRedirectUrl() {
    return "https://f215-195-114-147-152.ngrok.io/auth_flow";
  }

  @Override
  protected int getServerListeningPort() {
    return 3000;
  }

  @Override
  protected OAuthFlowImplementation getFlowImplementation(final ConfigRepository configRepository, final HttpClient httpClient) {
    return new SnapchatMarketingOAuthFlow(configRepository, httpClient);
  }

  @Test
  public void testFullSnapchatMarketingOAuthFlow() throws InterruptedException, ConfigNotFoundException, IOException, JsonValidationException {
    final UUID workspaceId = UUID.randomUUID();
    final UUID definitionId = UUID.randomUUID();
    final String fullConfigAsString = Files.readString(getCredentialsPath());
    final JsonNode credentialsJson = Jsons.deserialize(fullConfigAsString);
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(ImmutableMap.builder()
            .put("client_id", credentialsJson.get("client_id").asText())
            .put("client_secret", credentialsJson.get("client_secret").asText())
            .build()))));
    final String url = getFlowImplementation(configRepository, httpClient).getSourceConsentUrl(workspaceId, definitionId, getRedirectUrl(),
        Jsons.emptyObject(), null);
    LOGGER.info("Waiting for user consent at: {}", url);
    waitForResponse(20);
    assertTrue(serverHandler.isSucceeded(), "Failed to get User consent on time");
    final Map<String, Object> params = flow.completeSourceOAuth(workspaceId, definitionId,
        Map.of("code", serverHandler.getParamValue()), getRedirectUrl());
    LOGGER.info("Response from completing OAuth Flow is: {}", params.toString());
    assertTrue(params.containsKey("refresh_token"));
    assertTrue(params.get("refresh_token").toString().length() > 0);
  }

}
