/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows.google;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
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
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GoogleAnalyticsOAuthFlowTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(GoogleAnalyticsOAuthFlowTest.class);
  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");
  private static final String REDIRECT_URL = "https://airbyte.io";
  private static final String EXPECTED_REDIRECT_URL = "https%3A%2F%2Fairbyte.io";
  private static final String EXPECTED_SCOPE = "https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fanalytics.readonly";

  private HttpClient httpClient;
  private ConfigRepository configRepository;
  private GoogleAnalyticsOAuthFlow googleAnalyticsOAuthFlow;

  private UUID workspaceId;
  private UUID definitionId;

  @BeforeEach
  public void setup() {
    httpClient = mock(HttpClient.class);
    configRepository = mock(ConfigRepository.class);
    googleAnalyticsOAuthFlow = new GoogleAnalyticsOAuthFlow(configRepository, httpClient, GoogleAnalyticsOAuthFlowTest::getConstantState);

    workspaceId = UUID.randomUUID();
    definitionId = UUID.randomUUID();
  }

  private static String getConstantState() {
    return "state";
  }

  @Test
  public void testGetConsentUrlEmptyOAuthParameters() {
    assertThrows(ConfigNotFoundException.class, () -> googleAnalyticsOAuthFlow.getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL));
    assertThrows(ConfigNotFoundException.class, () -> googleAnalyticsOAuthFlow.getDestinationConsentUrl(workspaceId, definitionId, REDIRECT_URL));
  }

  @Test
  public void testGetConsentUrlIncompleteOAuthParameters() throws IOException, JsonValidationException {
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.emptyObject())));
    when(configRepository.listDestinationOAuthParam()).thenReturn(List.of(new DestinationOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withDestinationDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.emptyObject())));
    assertThrows(IllegalArgumentException.class, () -> googleAnalyticsOAuthFlow.getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL));
    assertThrows(IllegalArgumentException.class, () -> googleAnalyticsOAuthFlow.getDestinationConsentUrl(workspaceId, definitionId, REDIRECT_URL));
  }

  @Test
  public void testGetSourceConsentUrl() throws IOException, ConfigNotFoundException, JsonValidationException {
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(Map.of("credentials", ImmutableMap.builder()
            .put("client_id", getClientId())
            .build())))));
    final String actualSourceUrl = googleAnalyticsOAuthFlow.getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL);
    final String expectedSourceUrl = String.format(
        "https://accounts.google.com/o/oauth2/v2/auth?client_id=%s&redirect_uri=%s&response_type=code&scope=%s&access_type=offline&state=%s&include_granted_scopes=true&prompt=consent",
        getClientId(),
        EXPECTED_REDIRECT_URL,
        EXPECTED_SCOPE,
        getConstantState());
    LOGGER.info(expectedSourceUrl);
    assertEquals(expectedSourceUrl, actualSourceUrl);
  }

  @Test
  public void testGetDestinationConsentUrl() throws IOException, ConfigNotFoundException, JsonValidationException {
    when(configRepository.listDestinationOAuthParam()).thenReturn(List.of(new DestinationOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withDestinationDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(Map.of("credentials", ImmutableMap.builder()
            .put("client_id", getClientId())
            .build())))));
    // It would be better to make this comparison agnostic of the order of query params but the URI
    // class' equals() method
    // considers URLs with different qparam orders different URIs..
    final String actualDestinationUrl = googleAnalyticsOAuthFlow.getDestinationConsentUrl(workspaceId, definitionId, REDIRECT_URL);
    final String expectedDestinationUrl = String.format(
        "https://accounts.google.com/o/oauth2/v2/auth?client_id=%s&redirect_uri=%s&response_type=code&scope=%s&access_type=offline&state=%s&include_granted_scopes=true&prompt=consent",
        getClientId(),
        EXPECTED_REDIRECT_URL,
        EXPECTED_SCOPE,
        getConstantState());
    LOGGER.info(expectedDestinationUrl);
    assertEquals(expectedDestinationUrl, actualDestinationUrl);
  }

  @Test
  public void testCompleteOAuthMissingCode() throws IOException, ConfigNotFoundException, JsonValidationException {
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(Map.of("credentials", ImmutableMap.builder()
            .put("client_id", getClientId())
            .put("client_secret", "test_client_secret")
            .build())))));
    final Map<String, Object> queryParams = Map.of();
    assertThrows(IOException.class, () -> googleAnalyticsOAuthFlow.completeSourceOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL));
  }

  @Test
  public void testCompleteSourceOAuth() throws IOException, ConfigNotFoundException, JsonValidationException, InterruptedException {
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(Map.of("credentials", ImmutableMap.builder()
            .put("client_id", getClientId())
            .put("client_secret", "test_client_secret")
            .build())))));
    Map<String, String> returnedCredentials = Map.of("refresh_token", "refresh_token_response");
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(Jsons.serialize(returnedCredentials));
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final Map<String, Object> actualQueryParams = googleAnalyticsOAuthFlow.completeSourceOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL);
    assertEquals(Jsons.serialize(Map.of("credentials", returnedCredentials)), Jsons.serialize(actualQueryParams));
  }

  @Test
  public void testCompleteDestinationOAuth() throws IOException, ConfigNotFoundException, JsonValidationException, InterruptedException {
    when(configRepository.listDestinationOAuthParam()).thenReturn(List.of(new DestinationOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withDestinationDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(Map.of("credentials", ImmutableMap.builder()
            .put("client_id", getClientId())
            .put("client_secret", "test_client_secret")
            .build())))));
    Map<String, String> returnedCredentials = Map.of("refresh_token", "refresh_token_response");
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(Jsons.serialize(returnedCredentials));
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final Map<String, Object> actualQueryParams = googleAnalyticsOAuthFlow
        .completeDestinationOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL);
    assertEquals(Jsons.serialize(Map.of("credentials", returnedCredentials)), Jsons.serialize(actualQueryParams));
  }

  private String getClientId() throws IOException {
    if (!Files.exists(CREDENTIALS_PATH)) {
      return "test_client_id";
    } else {
      final String fullConfigAsString = new String(Files.readAllBytes(CREDENTIALS_PATH));
      final JsonNode credentialsJson = Jsons.deserialize(fullConfigAsString);
      return credentialsJson.get("credentials").get("client_id").asText();
    }
  }

}
