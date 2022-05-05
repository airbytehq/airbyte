/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth.flows;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
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
import io.airbyte.oauth.BaseOAuthFlow;
import io.airbyte.oauth.MoreOAuthParameters;
import io.airbyte.protocol.models.OAuthConfigSpecification;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.http.HttpClient;
import java.net.http.HttpResponse;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public abstract class BaseOAuthFlowTest {

  private static final String REDIRECT_URL = "https://airbyte.io";

  private HttpClient httpClient;
  private ConfigRepository configRepository;
  private BaseOAuthFlow oauthFlow;

  private UUID workspaceId;
  private UUID definitionId;

  protected HttpClient getHttpClient() {
    return httpClient;
  }

  protected ConfigRepository getConfigRepository() {
    return configRepository;
  }

  @BeforeEach
  public void setup() throws JsonValidationException, IOException {
    httpClient = mock(HttpClient.class);
    configRepository = mock(ConfigRepository.class);
    oauthFlow = getOAuthFlow();

    workspaceId = UUID.randomUUID();
    definitionId = UUID.randomUUID();
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(new SourceOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withSourceDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(getOAuthParamConfig())));
    when(configRepository.listDestinationOAuthParam()).thenReturn(List.of(new DestinationOAuthParameter()
        .withOauthParameterId(UUID.randomUUID())
        .withDestinationDefinitionId(definitionId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(getOAuthParamConfig())));
  }

  /**
   * This should be implemented for the particular oauth flow implementation
   *
   * @return the oauth flow implementation to test
   */
  protected abstract BaseOAuthFlow getOAuthFlow();

  /**
   * This should be implemented for the particular oauth flow implementation
   *
   * @return the expected consent URL
   */
  protected abstract String getExpectedConsentUrl();

  /**
   * Redefine if the oauth flow implementation does not return `refresh_token`. (maybe for example
   * using `access_token` like in the `GithubOAuthFlowTest` instead?)
   *
   * @return the full output expected to be returned by this oauth flow + all its instance wide
   *         variables
   */
  protected Map<String, String> getExpectedOutput() {
    return Map.of(
        "refresh_token", "refresh_token_response",
        "client_id", MoreOAuthParameters.SECRET_MASK,
        "client_secret", MoreOAuthParameters.SECRET_MASK);
  }

  /**
   * Redefine if the oauth flow implementation does not return `refresh_token`. (maybe for example
   * using `access_token` like in the `GithubOAuthFlowTest` instead?)
   *
   * @return the output specification used to identify what the oauth flow should be returning
   */
  protected JsonNode getCompleteOAuthOutputSpecification() {
    return getJsonSchema(Map.of("refresh_token", Map.of("type", "string")));
  }

  /**
   * Redefine if the oauth flow implementation does not return `refresh_token`. (maybe for example
   * using `access_token` like in the `GithubOAuthFlowTest` instead?)
   *
   * @return the filtered outputs once it is filtered by the output specifications
   */
  protected Map<String, String> getExpectedFilteredOutput() {
    return Map.of(
        "refresh_token", "refresh_token_response",
        "client_id", MoreOAuthParameters.SECRET_MASK);
  }

  /**
   * @return the output specification used to filter what the oauth flow should be returning
   */
  protected JsonNode getCompleteOAuthServerOutputSpecification() {
    return getJsonSchema(Map.of("client_id", Map.of("type", "string")));
  }

  /**
   * Redefine to match the oauth implementation flow getDefaultOAuthOutputPath()
   *
   * @return the backward compatible path that is used in the deprecated oauth flows.
   */
  protected List<String> getExpectedOutputPath() {
    return List.of("credentials");
  }

  /**
   * @return if the OAuth implementation flow has a dependency on input values from connector config.
   */
  protected boolean hasDependencyOnConnectorConfigValues() {
    return !getInputOAuthConfiguration().isEmpty();
  }

  /**
   * If the OAuth implementation flow has a dependency on input values from connector config, this
   * method should be redefined.
   *
   * @return the input configuration sent to oauth flow (values from connector config)
   */
  protected JsonNode getInputOAuthConfiguration() {
    return Jsons.emptyObject();
  }

  /**
   * If the OAuth implementation flow has a dependency on input values from connector config, this
   * method should be redefined.
   *
   * @return the input configuration sent to oauth flow (values from connector config)
   */
  protected JsonNode getUserInputFromConnectorConfigSpecification() {
    return getJsonSchema(Map.of());
  }

  /**
   * @return the instance wide config params for this oauth flow
   */
  protected JsonNode getOAuthParamConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("client_id", "test_client_id")
        .put("client_secret", "test_client_secret")
        .build());
  }

  protected static JsonNode getJsonSchema(final Map<String, Object> properties) {
    return Jsons.jsonNode(Map.of(
        "type", "object",
        "additionalProperties", "false",
        "properties", properties));
  }

  protected OAuthConfigSpecification getoAuthConfigSpecification() {
    return new OAuthConfigSpecification()
        .withOauthUserInputFromConnectorConfigSpecification(getUserInputFromConnectorConfigSpecification())
        .withCompleteOauthOutputSpecification(getCompleteOAuthOutputSpecification())
        .withCompleteOauthServerOutputSpecification(getCompleteOAuthServerOutputSpecification());
  }

  private OAuthConfigSpecification getEmptyOAuthConfigSpecification() {
    return new OAuthConfigSpecification()
        .withCompleteOauthOutputSpecification(Jsons.emptyObject())
        .withCompleteOauthServerOutputSpecification(Jsons.emptyObject());
  }

  protected String getConstantState() {
    return "state";
  }

  protected String getMockedResponse() {
    final Map<String, String> returnedCredentials = getExpectedOutput();
    return Jsons.serialize(returnedCredentials);
  }

  protected OAuthConfigSpecification getOAuthConfigSpecification() {
    return getoAuthConfigSpecification()
        // change property types to induce json validation errors.
        .withCompleteOauthServerOutputSpecification(getJsonSchema(Map.of("client_id", Map.of("type", "integer"))))
        .withCompleteOauthOutputSpecification(getJsonSchema(Map.of("refresh_token", Map.of("type", "integer"))));
  }

  @Test
  public void testGetDefaultOutputPath() {
    assertEquals(getExpectedOutputPath(), oauthFlow.getDefaultOAuthOutputPath());
  }

  @Test
  public void testValidateInputOAuthConfigurationFailure() {
    final JsonNode invalidInputOAuthConfiguration = Jsons.jsonNode(Map.of("UnexpectedRandomField", 42));
    assertThrows(JsonValidationException.class,
        () -> oauthFlow.getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL, invalidInputOAuthConfiguration, getoAuthConfigSpecification()));
    assertThrows(JsonValidationException.class, () -> oauthFlow.getDestinationConsentUrl(workspaceId, definitionId, REDIRECT_URL,
        invalidInputOAuthConfiguration, getoAuthConfigSpecification()));
    assertThrows(JsonValidationException.class, () -> oauthFlow.completeSourceOAuth(workspaceId, definitionId, Map.of(), REDIRECT_URL,
        invalidInputOAuthConfiguration, getoAuthConfigSpecification()));
    assertThrows(JsonValidationException.class, () -> oauthFlow.completeDestinationOAuth(workspaceId, definitionId, Map.of(), REDIRECT_URL,
        invalidInputOAuthConfiguration, getoAuthConfigSpecification()));
  }

  @Test
  public void testGetConsentUrlEmptyOAuthParameters() throws JsonValidationException, IOException {
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of());
    when(configRepository.listDestinationOAuthParam()).thenReturn(List.of());
    assertThrows(ConfigNotFoundException.class,
        () -> oauthFlow.getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL, getInputOAuthConfiguration(), getoAuthConfigSpecification()));
    assertThrows(ConfigNotFoundException.class,
        () -> oauthFlow.getDestinationConsentUrl(workspaceId, definitionId, REDIRECT_URL, getInputOAuthConfiguration(),
            getoAuthConfigSpecification()));
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
    assertThrows(IllegalArgumentException.class,
        () -> oauthFlow.getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL, getInputOAuthConfiguration(), getoAuthConfigSpecification()));
    assertThrows(IllegalArgumentException.class,
        () -> oauthFlow.getDestinationConsentUrl(workspaceId, definitionId, REDIRECT_URL, getInputOAuthConfiguration(),
            getoAuthConfigSpecification()));
  }

  @Test
  public void testGetSourceConsentUrlEmptyOAuthSpec() throws IOException, ConfigNotFoundException, JsonValidationException {
    if (hasDependencyOnConnectorConfigValues()) {
      assertThrows(IOException.class, () -> oauthFlow.getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL, Jsons.emptyObject(), null),
          "OAuth Flow Implementations with dependencies on connector config can't be supported without OAuthConfigSpecifications");
    } else {
      final String consentUrl = oauthFlow.getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL, Jsons.emptyObject(), null);
      assertEquals(getExpectedConsentUrl(), consentUrl);
    }
  }

  @Test
  public void testGetDestinationConsentUrlEmptyOAuthSpec() throws IOException, ConfigNotFoundException, JsonValidationException {
    if (hasDependencyOnConnectorConfigValues()) {
      assertThrows(IOException.class, () -> oauthFlow.getDestinationConsentUrl(workspaceId, definitionId, REDIRECT_URL, Jsons.emptyObject(), null),
          "OAuth Flow Implementations with dependencies on connector config can't be supported without OAuthConfigSpecifications");
    } else {
      final String consentUrl = oauthFlow.getDestinationConsentUrl(workspaceId, definitionId, REDIRECT_URL, Jsons.emptyObject(), null);
      assertEquals(getExpectedConsentUrl(), consentUrl);
    }
  }

  @Test
  public void testGetSourceConsentUrl() throws IOException, ConfigNotFoundException, JsonValidationException {
    final String consentUrl =
        oauthFlow.getSourceConsentUrl(workspaceId, definitionId, REDIRECT_URL, getInputOAuthConfiguration(), getoAuthConfigSpecification());
    assertEquals(getExpectedConsentUrl(), consentUrl);
  }

  @Test
  public void testGetDestinationConsentUrl() throws IOException, ConfigNotFoundException, JsonValidationException {
    final String consentUrl =
        oauthFlow.getDestinationConsentUrl(workspaceId, definitionId, REDIRECT_URL, getInputOAuthConfiguration(), getoAuthConfigSpecification());
    assertEquals(getExpectedConsentUrl(), consentUrl);
  }

  @Test
  public void testCompleteOAuthMissingCode() {
    final Map<String, Object> queryParams = Map.of();
    assertThrows(IOException.class, () -> oauthFlow.completeSourceOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL));
  }

  @Test
  public void testDeprecatedCompleteSourceOAuth() throws IOException, InterruptedException, ConfigNotFoundException {
    final Map<String, String> returnedCredentials = getExpectedOutput();
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(Jsons.serialize(returnedCredentials));
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");

    if (hasDependencyOnConnectorConfigValues()) {
      assertThrows(IOException.class, () -> oauthFlow.completeSourceOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL),
          "OAuth Flow Implementations with dependencies on connector config can't be supported in the deprecated APIs");
    } else {
      Map<String, Object> actualRawQueryParams = oauthFlow.completeSourceOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL);
      for (final String node : getExpectedOutputPath()) {
        assertNotNull(actualRawQueryParams.get(node));
        actualRawQueryParams = (Map<String, Object>) actualRawQueryParams.get(node);
      }
      final Map<String, String> expectedOutput = returnedCredentials;
      final Map<String, Object> actualQueryParams = actualRawQueryParams;
      assertEquals(expectedOutput.size(), actualQueryParams.size(),
          String.format("Expected %s values but got\n\t%s\ninstead of\n\t%s", expectedOutput.size(), actualQueryParams, expectedOutput));
      expectedOutput.forEach((key, value) -> assertEquals(value, actualQueryParams.get(key)));
    }
  }

  @Test
  public void testDeprecatedCompleteDestinationOAuth() throws IOException, ConfigNotFoundException, InterruptedException {
    final Map<String, String> returnedCredentials = getExpectedOutput();
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(Jsons.serialize(returnedCredentials));
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");

    if (hasDependencyOnConnectorConfigValues()) {
      assertThrows(IOException.class, () -> oauthFlow.completeDestinationOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL),
          "OAuth Flow Implementations with dependencies on connector config can't be supported in the deprecated APIs");
    } else {
      Map<String, Object> actualRawQueryParams = oauthFlow.completeDestinationOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL);
      for (final String node : getExpectedOutputPath()) {
        assertNotNull(actualRawQueryParams.get(node));
        actualRawQueryParams = (Map<String, Object>) actualRawQueryParams.get(node);
      }
      final Map<String, String> expectedOutput = returnedCredentials;
      final Map<String, Object> actualQueryParams = actualRawQueryParams;
      assertEquals(expectedOutput.size(), actualQueryParams.size(),
          String.format("Expected %s values but got\n\t%s\ninstead of\n\t%s", expectedOutput.size(), actualQueryParams, expectedOutput));
      expectedOutput.forEach((key, value) -> assertEquals(value, actualQueryParams.get(key)));
    }
  }

  @Test
  public void testEmptyOutputCompleteSourceOAuth() throws IOException, InterruptedException, ConfigNotFoundException, JsonValidationException {
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(getMockedResponse());
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final Map<String, Object> actualQueryParams = oauthFlow.completeSourceOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL,
        getInputOAuthConfiguration(), getEmptyOAuthConfigSpecification());
    assertEquals(0, actualQueryParams.size(),
        String.format("Expected no values but got %s", actualQueryParams));
  }

  @Test
  public void testEmptyOutputCompleteDestinationOAuth() throws IOException, InterruptedException, ConfigNotFoundException, JsonValidationException {
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(getMockedResponse());
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final Map<String, Object> actualQueryParams = oauthFlow.completeDestinationOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL,
        getInputOAuthConfiguration(), getEmptyOAuthConfigSpecification());
    assertEquals(0, actualQueryParams.size(),
        String.format("Expected no values but got %s", actualQueryParams));
  }

  @Test
  public void testEmptyInputCompleteSourceOAuth() throws IOException, InterruptedException, ConfigNotFoundException, JsonValidationException {
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(getMockedResponse());
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final Map<String, Object> actualQueryParams = oauthFlow.completeSourceOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL,
        Jsons.emptyObject(), getoAuthConfigSpecification());
    final Map<String, String> expectedOutput = getExpectedFilteredOutput();
    assertEquals(expectedOutput.size(), actualQueryParams.size(),
        String.format("Expected %s values but got\n\t%s\ninstead of\n\t%s", expectedOutput.size(), actualQueryParams, expectedOutput));
    expectedOutput.forEach((key, value) -> assertEquals(value, actualQueryParams.get(key)));
  }

  @Test
  public void testEmptyInputCompleteDestinationOAuth() throws IOException, InterruptedException, ConfigNotFoundException, JsonValidationException {
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(getMockedResponse());
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final Map<String, Object> actualQueryParams = oauthFlow.completeDestinationOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL,
        Jsons.emptyObject(), getoAuthConfigSpecification());
    final Map<String, String> expectedOutput = getExpectedFilteredOutput();
    assertEquals(expectedOutput.size(), actualQueryParams.size(),
        String.format("Expected %s values but got\n\t%s\ninstead of\n\t%s", expectedOutput.size(), actualQueryParams, expectedOutput));
    expectedOutput.forEach((key, value) -> assertEquals(value, actualQueryParams.get(key)));
  }

  @Test
  public void testCompleteSourceOAuth() throws IOException, InterruptedException, ConfigNotFoundException, JsonValidationException {
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(getMockedResponse());
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final Map<String, Object> actualQueryParams = oauthFlow.completeSourceOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL,
        getInputOAuthConfiguration(), getoAuthConfigSpecification());
    final Map<String, String> expectedOutput = getExpectedFilteredOutput();
    assertEquals(expectedOutput.size(), actualQueryParams.size(),
        String.format("Expected %s values but got\n\t%s\ninstead of\n\t%s", expectedOutput.size(), actualQueryParams, expectedOutput));
    expectedOutput.forEach((key, value) -> assertEquals(value, actualQueryParams.get(key)));
  }

  @Test
  public void testCompleteDestinationOAuth() throws IOException, InterruptedException, ConfigNotFoundException, JsonValidationException {
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(getMockedResponse());
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final Map<String, Object> actualQueryParams = oauthFlow.completeDestinationOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL,
        getInputOAuthConfiguration(), getoAuthConfigSpecification());
    final Map<String, String> expectedOutput = getExpectedFilteredOutput();
    assertEquals(expectedOutput.size(), actualQueryParams.size(),
        String.format("Expected %s values but got\n\t%s\ninstead of\n\t%s", expectedOutput.size(), actualQueryParams, expectedOutput));
    expectedOutput.forEach((key, value) -> assertEquals(value, actualQueryParams.get(key)));
  }

  @Test
  public void testValidateOAuthOutputFailure() throws IOException, InterruptedException, ConfigNotFoundException, JsonValidationException {
    final HttpResponse response = mock(HttpResponse.class);
    when(response.body()).thenReturn(getMockedResponse());
    when(httpClient.send(any(), any())).thenReturn(response);
    final Map<String, Object> queryParams = Map.of("code", "test_code");
    final OAuthConfigSpecification oAuthConfigSpecification = getOAuthConfigSpecification();
    assertThrows(JsonValidationException.class, () -> oauthFlow.completeSourceOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL,
        getInputOAuthConfiguration(), oAuthConfigSpecification));
    assertThrows(JsonValidationException.class, () -> oauthFlow.completeDestinationOAuth(workspaceId, definitionId, queryParams, REDIRECT_URL,
        getInputOAuthConfiguration(), oAuthConfigSpecification));
  }

}
