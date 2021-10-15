/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.api.client.http.HttpTransport;
import com.google.api.client.http.LowLevelHttpRequest;
import com.google.api.client.http.LowLevelHttpResponse;
import com.google.api.client.testing.http.MockHttpTransport;
import com.google.api.client.testing.http.MockLowLevelHttpRequest;
import com.google.api.client.testing.http.MockLowLevelHttpResponse;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class TrelloOAuthFlowTest {

  private static final String REDIRECT_URL = "https://airbyte.io";

  private UUID workspaceId;
  private UUID definitionId;
  private ConfigRepository configRepository;
  private TrelloOAuthFlow trelloOAuthFlow;
  private HttpTransport transport;

  @BeforeEach
  public void setup() throws IOException, JsonValidationException {
    workspaceId = UUID.randomUUID();
    definitionId = UUID.randomUUID();

    transport = new MockHttpTransport() {

      @Override
      public LowLevelHttpRequest buildRequest(String method, String url) throws IOException {
        return new MockLowLevelHttpRequest() {

          @Override
          public LowLevelHttpResponse execute() throws IOException {
            MockLowLevelHttpResponse response = new MockLowLevelHttpResponse();
            response.setStatusCode(200);
            response.setContentType("application/x-www-form-urlencoded");
            response.setContent("oauth_token=test_token&oauth_token_secret=test_secret&oauth_callback_confirmed=true");
            return response;
          }

        };
      }

    };
    configRepository = mock(ConfigRepository.class);
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(ImmutableMap.builder()
            .put("client_id", "test_client_id")
            .put("client_secret", "test_client_secret")
            .build()))));
    trelloOAuthFlow = new TrelloOAuthFlow(configRepository, transport);
  }

  @Test
  public void testGetSourceConcentUrl() throws IOException, InterruptedException, ConfigNotFoundException {
    final String concentUrl =
        trelloOAuthFlow.getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL);
    assertEquals(concentUrl, "https://trello.com/1/OAuthAuthorizeToken?oauth_token=test_token");
  }

  @Test
  public void testCompleteSourceAuth() throws IOException, InterruptedException, ConfigNotFoundException {
    final Map<String, String> expectedParams = Map.of("key", "test_client_id", "token", "test_token");
    final Map<String, Object> queryParams = Map.of("oauth_token", "token", "oauth_verifier", "verifier");
    final Map<String, Object> returnedParams =
        trelloOAuthFlow.completeSourceOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL);
    assertEquals(returnedParams, expectedParams);
  }

}
