/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows.google;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
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

public class GoogleSheetsOAuthFlowTest {

  private static final String REDIRECT_URL = "https://airbyte.io";

  private HttpClient httpClient;
  private ConfigRepository configRepository;
  private GoogleSheetsOAuthFlow googleSheetsOAuthFlow;

  private UUID workspaceId;
  private UUID definitionId;

  @BeforeEach
  public void setup() {
    httpClient = mock(HttpClient.class);
    configRepository = mock(ConfigRepository.class);
    googleSheetsOAuthFlow = new GoogleSheetsOAuthFlow(configRepository, httpClient, GoogleSheetsOAuthFlowTest::getConstantState);

    workspaceId = UUID.randomUUID();
    definitionId = UUID.randomUUID();
  }

  private static String getConstantState() {
    return "state";
  }

  @Test
  public void testCompleteSourceOAuth() throws IOException, ConfigNotFoundException, JsonValidationException, InterruptedException {
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(Map.of("credentials", ImmutableMap.builder()
            .put("client_id", "test_client_id")
            .put("client_secret", "test_client_secret")
            .build())))));

    final Map<String, String> returnedCredentials = Map.of("refresh_token", "refresh_token_response");
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(Jsons.serialize(returnedCredentials));
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final Map<String, Object> actualQueryParams = googleSheetsOAuthFlow.completeSourceOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL);

    assertEquals(Jsons.serialize(Map.of("credentials", returnedCredentials)), Jsons.serialize(actualQueryParams));
  }

  @Test
  public void testCompleteDestinationOAuth() throws IOException, ConfigNotFoundException, JsonValidationException, InterruptedException {
    when(configRepository.listDestinationOAuthParam()).thenReturn(List.of(new DestinationOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withDestinationDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(Map.of("credentials", ImmutableMap.builder()
            .put("client_id", "test_client_id")
            .put("client_secret", "test_client_secret")
            .build())))));

    final Map<String, String> returnedCredentials = Map.of("refresh_token", "refresh_token_response");
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(Jsons.serialize(returnedCredentials));
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final Map<String, Object> actualQueryParams =
        googleSheetsOAuthFlow.completeDestinationOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL);

    assertEquals(Jsons.serialize(Map.of("credentials", returnedCredentials)), Jsons.serialize(actualQueryParams));
  }

  @Test
  public void testGetClientIdUnsafe() {
    final String clientId = "123";
    final Map<String, String> clientIdMap = Map.of("client_id", clientId);
    final Map<String, Map<String, String>> nestedConfig = Map.of("credentials", clientIdMap);

    assertThrows(IllegalArgumentException.class, () -> googleSheetsOAuthFlow.getClientIdUnsafe(Jsons.jsonNode(clientIdMap)));
    assertEquals(clientId, googleSheetsOAuthFlow.getClientIdUnsafe(Jsons.jsonNode(nestedConfig)));
  }

  @Test
  public void testGetClientSecretUnsafe() {
    final String clientSecret = "secret";
    final Map<String, String> clientIdMap = Map.of("client_secret", clientSecret);
    final Map<String, Map<String, String>> nestedConfig = Map.of("credentials", clientIdMap);

    assertThrows(IllegalArgumentException.class, () -> googleSheetsOAuthFlow.getClientSecretUnsafe(Jsons.jsonNode(clientIdMap)));
    assertEquals(clientSecret, googleSheetsOAuthFlow.getClientSecretUnsafe(Jsons.jsonNode(nestedConfig)));
  }

}
