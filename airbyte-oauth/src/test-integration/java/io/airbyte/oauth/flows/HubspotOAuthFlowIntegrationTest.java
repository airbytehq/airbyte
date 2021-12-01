/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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

public class HubspotOAuthFlowIntegrationTest extends OAuthFlowIntegrationTest {

  @Override
  protected Path getCredentialsPath() {
    return Path.of("secrets/hubspot.json");
  }

  protected OAuthFlowImplementation getFlowObject(ConfigRepository configRepository) {
    return new HubspotOAuthFlow(configRepository, httpClient);
  }

  @Override
  protected OAuthFlowImplementation getFlowImplementation(ConfigRepository configRepository, HttpClient httpClient) {
    return new HubspotOAuthFlow(configRepository, httpClient);
  }

  @Test
  public void testFullOAuthFlow() throws InterruptedException, ConfigNotFoundException, IOException, JsonValidationException {
    int limit = 100;
    final UUID workspaceId = UUID.randomUUID();
    final UUID definitionId = UUID.randomUUID();
    final String fullConfigAsString = new String(Files.readAllBytes(getCredentialsPath()));
    final JsonNode credentialsJson = Jsons.deserialize(fullConfigAsString);
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(ImmutableMap.builder()
            .put("client_id", credentialsJson.get("credentials").get("client_id").asText())
            .put("client_secret", credentialsJson.get("credentials").get("client_secret").asText())
            .build()))));
    var flowObject = getFlowImplementation(configRepository, httpClient);
    final String url = flowObject.getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL, Jsons.emptyObject(), null);
    LOGGER.info("Waiting for user consent at: {}", url);
    // TODO: To automate, start a selenium job to navigate to the Consent URL and click on allowing
    // access...
    while (!serverHandler.isSucceeded() && limit > 0) {
      Thread.sleep(1000);
      limit -= 1;
    }
    assertTrue(serverHandler.isSucceeded(), "Failed to get User consent on time");
    final Map<String, Object> params = flowObject.completeSourceOAuth(workspaceId, definitionId,
        Map.of("code", serverHandler.getParamValue()), REDIRECT_URL);
    LOGGER.info("Response from completing OAuth Flow is: {}", params.toString());
    assertTrue(params.containsKey("credentials"));
    final Map<String, Object> credentials = (Map<String, Object>) params.get("credentials");
    assertTrue(credentials.containsKey("refresh_token"));
    assertTrue(credentials.get("refresh_token").toString().length() > 0);
    assertTrue(credentials.containsKey("access_token"));
    assertTrue(credentials.get("access_token").toString().length() > 0);
  }

}
