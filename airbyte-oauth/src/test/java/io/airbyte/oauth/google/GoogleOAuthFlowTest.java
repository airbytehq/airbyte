/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.oauth.google;

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
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GoogleOAuthFlowTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(GoogleOAuthFlowTest.class);
  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");
  private static final String REDIRECT_URL = "https://airbyte.io";
  private static final String SCOPE = "https://www.googleapis.com/auth/analytics.readonly";

  private HttpClient httpClient;
  private ConfigRepository configRepository;
  private GoogleOAuthFlow googleOAuthFlow;

  private UUID workspaceId;
  private UUID definitionId;

  @BeforeEach
  public void setup() {
    httpClient = mock(HttpClient.class);
    configRepository = mock(ConfigRepository.class);
    googleOAuthFlow = new GoogleOAuthFlow(configRepository, SCOPE, httpClient);

    workspaceId = UUID.randomUUID();
    definitionId = UUID.randomUUID();
  }

  @Test
  public void testGetConsentUrlEmptyOAuthParameters() {
    assertThrows(ConfigNotFoundException.class, () -> googleOAuthFlow.getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL));
    assertThrows(ConfigNotFoundException.class, () -> googleOAuthFlow.getDestinationConsentUrl(workspaceId, definitionId, REDIRECT_URL));
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
    assertThrows(IllegalArgumentException.class, () -> googleOAuthFlow.getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL));
    assertThrows(IllegalArgumentException.class, () -> googleOAuthFlow.getDestinationConsentUrl(workspaceId, definitionId, REDIRECT_URL));
  }

  @Test
  public void testGetSourceConsentUrl() throws IOException, ConfigNotFoundException, JsonValidationException {
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(ImmutableMap.builder()
            .put("client_id", getClientId())
            .build()))));
    final String actualSourceUrl = googleOAuthFlow.getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL);
    final String expectedSourceUrl = String.format(
        "https://accounts.google.com/o/oauth2/v2/auth?state=%s&client_id=%s&redirect_uri=%s&scope=%s&access_type=offline&include_granted_scopes=true&response_type=code&prompt=consent",
        definitionId,
        getClientId(),
        urlEncode(REDIRECT_URL),
        urlEncode(SCOPE));
    LOGGER.info(expectedSourceUrl);
    assertEquals(expectedSourceUrl, actualSourceUrl);
  }

  @Test
  public void testGetDestinationConsentUrl() throws IOException, ConfigNotFoundException, JsonValidationException {
    when(configRepository.listDestinationOAuthParam()).thenReturn(List.of(new DestinationOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withDestinationDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(ImmutableMap.builder()
            .put("client_id", getClientId())
            .build()))));
    // It would be better to make this comparison agnostic of the order of query params but the URI
    // class' equals() method
    // considers URLs with different qparam orders different URIs..
    final String actualDestinationUrl = googleOAuthFlow.getDestinationConsentUrl(workspaceId, definitionId, REDIRECT_URL);
    final String expectedDestinationUrl = String.format(
        "https://accounts.google.com/o/oauth2/v2/auth?state=%s&client_id=%s&redirect_uri=%s&scope=%s&access_type=offline&include_granted_scopes=true&response_type=code&prompt=consent",
        definitionId,
        getClientId(),
        urlEncode(REDIRECT_URL),
        urlEncode(SCOPE));
    LOGGER.info(expectedDestinationUrl);
    assertEquals(expectedDestinationUrl, actualDestinationUrl);
  }

  @Test
  public void testCompleteOAuthMissingCode() throws IOException, ConfigNotFoundException, JsonValidationException {
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(ImmutableMap.builder()
            .put("client_id", getClientId())
            .put("client_secret", "test_client_secret")
            .build()))));
    final Map<String, Object> queryParams = Map.of();
    assertThrows(IOException.class, () -> googleOAuthFlow.completeSourceOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL));
  }

  @Test
  public void testCompleteSourceOAuth() throws IOException, ConfigNotFoundException, JsonValidationException, InterruptedException {
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(ImmutableMap.builder()
            .put("client_id", getClientId())
            .put("client_secret", "test_client_secret")
            .build()))));
    final String expectedQueryParams = Jsons.serialize(Map.of(
        "refresh_token", "refresh_token_response"));
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(expectedQueryParams);
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final Map<String, Object> actualQueryParams = googleOAuthFlow.completeSourceOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL);
    assertEquals(expectedQueryParams, Jsons.serialize(actualQueryParams));
  }

  @Test
  public void testCompleteDestinationOAuth() throws IOException, ConfigNotFoundException, JsonValidationException, InterruptedException {
    when(configRepository.listDestinationOAuthParam()).thenReturn(List.of(new DestinationOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withDestinationDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(ImmutableMap.builder()
            .put("client_id", getClientId())
            .put("client_secret", "test_client_secret")
            .build()))));
    final String expectedQueryParams = Jsons.serialize(Map.of(
        "refresh_token", "refresh_token_response"));
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(expectedQueryParams);
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final Map<String, Object> actualQueryParams = googleOAuthFlow.completeDestinationOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL);
    assertEquals(expectedQueryParams, Jsons.serialize(actualQueryParams));
  }

  private String getClientId() throws IOException {
    if (!Files.exists(CREDENTIALS_PATH)) {
      return "test_client_id";
    } else {
      final String fullConfigAsString = new String(Files.readAllBytes(CREDENTIALS_PATH));
      final JsonNode credentialsJson = Jsons.deserialize(fullConfigAsString);
      return credentialsJson.get("client_id").asText();
    }
  }

  private String urlEncode(String s) {
    return URLEncoder.encode(s, StandardCharsets.UTF_8);
  }

}
