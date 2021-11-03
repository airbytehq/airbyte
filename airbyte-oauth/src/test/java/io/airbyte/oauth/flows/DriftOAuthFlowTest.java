/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.http.HttpClient;
import java.net.http.HttpResponse;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class DriftOAuthFlowTest {

  private UUID workspaceId;
  private UUID definitionId;
  private ConfigRepository configRepository;
  private DriftOAuthFlow driftOAuthFlow;
  private HttpClient httpClient;

  private static final String REDIRECT_URL = "https://airbyte.io";

  @BeforeEach
  public void setup() throws IOException, JsonValidationException {
    workspaceId = UUID.randomUUID();
    definitionId = UUID.randomUUID();
    configRepository = mock(ConfigRepository.class);
    httpClient = mock(HttpClient.class);
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(
            Map.of("credentials",
                ImmutableMap.builder()
                    .put("client_id", "test_client_id")
                    .put("client_secret", "test_client_secret")
                    .build())))));

    driftOAuthFlow = new DriftOAuthFlow(configRepository, httpClient,
        DriftOAuthFlowTest::getConstantState);

  }

  @Test
  public void testGetSourceConsentUrl()
      throws IOException, InterruptedException, ConfigNotFoundException {
    final String consentUrl =
        driftOAuthFlow.getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL);
    assertEquals(consentUrl,
        "https://dev.drift.com/authorize?response_type=code&client_id=test_client_id&redirect_uri=https%3A%2F%2Fairbyte.io&state=state");
  }

  @Test
  public void testCompleteSourceOAuth()
      throws IOException, JsonValidationException, InterruptedException, ConfigNotFoundException {
    Map<String, String> returnedCredentials = Map.of("access_token", "access_token_response");
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(Jsons.serialize(returnedCredentials));
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final Map<String, Object> actualQueryParams =
        driftOAuthFlow.completeSourceOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL);
    assertEquals(Jsons.serialize(Map.of("credentials", returnedCredentials)),
        Jsons.serialize(actualQueryParams));
  }

  @Test
  public void testCompleteDestinationOAuth()
      throws IOException, ConfigNotFoundException, JsonValidationException, InterruptedException {
    when(configRepository.listDestinationOAuthParam()).thenReturn(
        List.of(new DestinationOAuthParameter()
            .withOauthParameterId(UUID.randomUUID())
            .withDestinationDefinitionId(definitionId)
            .withWorkspaceId(workspaceId)
            .withConfiguration(Jsons.jsonNode(
                Map.of("credentials",
                    ImmutableMap.builder()
                        .put("client_id", "test_client_id")
                        .put("client_secret", "test_client_secret")
                        .build())))));

    final Map<String, String> returnedCredentials = Map.of("access_token",
        "access_token_response");
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(Jsons.serialize(returnedCredentials));
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final Map<String, Object> actualQueryParams =
        driftOAuthFlow.completeDestinationOAuth(workspaceId, definitionId, queryParams,
            REDIRECT_URL);

    assertEquals(Jsons.serialize(Map.of("credentials", returnedCredentials)),
        Jsons.serialize(actualQueryParams));
  }

  private static String getConstantState() {
    return "state";
  }

}
