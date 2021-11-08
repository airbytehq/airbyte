package io.airbyte.oauth.flows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.OAuthFlowImplementation;
import io.airbyte.validation.json.JsonValidationException;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.net.http.HttpClient;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.when;

public class QuickbooksOAuthFlowIntegrationTest extends OAuthFlowIntegrationTest{
  protected static final Path CREDENTIALS_PATH = Path.of("secrets/quickbooks.json");
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
  protected OAuthFlowImplementation getFlowImplementation(ConfigRepository configRepository, HttpClient httpClient) {
    return new QuickbooksOAuthFlow(configRepository, httpClient);
  }

  //https://appcenter.intuit.com/app/connect/oauth2?client_id=ABy25v4o09iEIHzwpFA61Dmu7Bs3hL8S4EgTVI6KxsTgTJC0sz&scope=com.intuit.quickbooks.accounting%20com.intuit.quickbooks.payment&redirect_uri=http://localhost:3000/auth_flow&response_type=code&state=PlaygroundAuth#/OpenIdAuthorize
  //https://appcenter.intuit.com/connect/oauth2?client_id=ABRLiF1l4w058BbowtFnAzwB83fbLLVIOGaLqBm8xFxQicZunK&redirect_uri=http://localhost:3000/auth_flow&state=IWLq46B&scope=com.intuit.quickbooks.accounting&response_type=code
  //https://appcenter.intuit.com/app/connect/oauth2?client_id=ABRLiF1l4w058BbowtFnAzwB83fbLLVIOGaLqBm8xFxQicZunK&redirect_uri=http://localhost:3000/auth_flow&state=lolTKn8&scope=com.intuit.quickbooks.accounting&response_type=code
  @Test
  public void testFullOAuthFlow() throws InterruptedException, ConfigNotFoundException, IOException, JsonValidationException {
    int limit = 20;
    final UUID workspaceId = UUID.randomUUID();
    final UUID definitionId = UUID.randomUUID();
    final String fullConfigAsString = new String(Files.readAllBytes(CREDENTIALS_PATH));
    final JsonNode credentialsJson = Jsons.deserialize(fullConfigAsString);
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
            .withOauthParameterId(UUID.randomUUID())
            .withSourceDefinitionId(definitionId)
            .withWorkspaceId(workspaceId)
            .withConfiguration(Jsons.jsonNode(ImmutableMap.builder()
                    .put("client_id", credentialsJson.get("client_id").asText())
                    .put("client_secret", credentialsJson.get("client_secret").asText())
                    .build()))));
    final String url = getFlowImplementation(configRepository, httpClient).getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL);
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
    assertTrue(params.containsKey("access_token"));
    assertTrue(params.get("access_token").toString().length() > 0);
  }
}
