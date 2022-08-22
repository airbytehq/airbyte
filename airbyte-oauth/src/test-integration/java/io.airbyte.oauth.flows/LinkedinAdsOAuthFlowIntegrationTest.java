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
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Test;

public class LinkedinAdsOAuthFlowIntegrationTest extends OAuthFlowIntegrationTest {

  protected static final Path CREDENTIALS_PATH = Path.of("secrets/config_oauth.json");
  protected static final String REDIRECT_URL = "http://localhost:3000/auth_flow";

  @Override
  protected int getServerListeningPort() {
    return 3000;
  }

  @Override
  protected Path getCredentialsPath() {
    return CREDENTIALS_PATH;
  }

  @Override
  protected OAuthFlowImplementation getFlowImplementation(final ConfigRepository configRepository, final HttpClient httpClient) {
    return new LinkedinAdsOAuthFlow(configRepository, httpClient);
  }

  @SuppressWarnings({"BusyWait", "unchecked"})
  @Test
  public void testFullOAuthFlow() throws InterruptedException, ConfigNotFoundException, IOException, JsonValidationException {
    int limit = 20;
    final UUID workspaceId = UUID.randomUUID();
    final UUID definitionId = UUID.randomUUID();
    final String fullConfigAsString = Files.readString(CREDENTIALS_PATH);
    final JsonNode credentialsJson = Jsons.deserialize(fullConfigAsString);
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(Map.of("credentials", ImmutableMap.builder()
            .put("client_id", credentialsJson.get("client_id").asText())
            .put("client_secret", credentialsJson.get("client_secret").asText())
            .build())))));
    final String url =
        getFlowImplementation(configRepository, httpClient).getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL, Jsons.emptyObject(), null);
    LOGGER.info("Waiting for user consent at: {}", url);
    // TODO: To automate, start a selenium job to navigate to the Consent URL and click on allowing
    // access...
    while (!serverHandler.isSucceeded() && limit > 0) {
      Thread.sleep(1000);
      limit -= 1;
    }
    assertTrue(serverHandler.isSucceeded(), "Failed to get User consent on time");
    final Map<String, Object> params = flow.completeSourceOAuth(workspaceId, definitionId,
        Map.of("code", serverHandler.getParamValue()), REDIRECT_URL);

    LOGGER.info("Response from completing OAuth Flow is: {}", params.toString());
    assertTrue(params.containsKey("credentials"));
    final Map<String, Object> credentials;
    credentials = Collections.unmodifiableMap((Map<String, Object>) params.get("credentials"));
    assertTrue(credentials.containsKey("refresh_token"));
    assertTrue(credentials.get("refresh_token").toString().length() > 0);
  }

}
