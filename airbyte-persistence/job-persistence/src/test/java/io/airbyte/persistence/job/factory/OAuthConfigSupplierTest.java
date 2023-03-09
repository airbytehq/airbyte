/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job.factory;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyMap;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.MoreOAuthParameters;
import io.airbyte.protocol.models.AdvancedAuth;
import io.airbyte.protocol.models.AdvancedAuth.AuthFlowType;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.OAuthConfigSpecification;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class OAuthConfigSupplierTest {

  static final String API_CLIENT = "api_client";
  static final String CREDENTIALS = "credentials";
  static final String PROPERTIES = "properties";

  private static final String AUTH_TYPE = "auth_type";
  private static final String OAUTH = "oauth";
  private static final String API_SECRET = "api_secret";

  private ConfigRepository configRepository;
  private TrackingClient trackingClient;
  private OAuthConfigSupplier oAuthConfigSupplier;
  private UUID sourceDefinitionId;
  private StandardSourceDefinition testSourceDefinition;

  @BeforeEach
  void setup() throws JsonValidationException, ConfigNotFoundException, IOException {
    configRepository = mock(ConfigRepository.class);
    trackingClient = mock(TrackingClient.class);
    oAuthConfigSupplier = new OAuthConfigSupplier(configRepository, trackingClient);
    sourceDefinitionId = UUID.randomUUID();
    testSourceDefinition = new StandardSourceDefinition()
        .withSourceDefinitionId(sourceDefinitionId)
        .withName("test")
        .withDockerRepository("test/test")
        .withDockerImageTag("dev")
        .withSpec(null);

    setupStandardDefinitionMock(createAdvancedAuth()
        .withPredicateKey(List.of(CREDENTIALS, AUTH_TYPE))
        .withPredicateValue(OAUTH));
  }

  @Test
  void testNoOAuthInjectionBecauseEmptyParams() throws IOException {
    final JsonNode config = generateJsonConfig();
    final UUID workspaceId = UUID.randomUUID();
    final JsonNode actualConfig = oAuthConfigSupplier.injectSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    assertEquals(config, actualConfig);
    assertNoTracking();
  }

  @Test
  void testNoAuthMaskingBecauseEmptyParams() throws IOException {
    final JsonNode config = generateJsonConfig();
    final UUID workspaceId = UUID.randomUUID();
    final JsonNode actualConfig = oAuthConfigSupplier.maskSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    assertEquals(config, actualConfig);
  }

  @Test
  void testNoOAuthInjectionBecauseMissingPredicateKey() throws IOException, JsonValidationException, ConfigNotFoundException {
    setupStandardDefinitionMock(createAdvancedAuth()
        .withPredicateKey(List.of("some_random_fields", AUTH_TYPE))
        .withPredicateValue(OAUTH));
    final JsonNode config = generateJsonConfig();
    final UUID workspaceId = UUID.randomUUID();
    setupOAuthParamMocks(generateOAuthParameters());
    final JsonNode actualConfig = oAuthConfigSupplier.injectSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    assertEquals(config, actualConfig);
    assertNoTracking();
  }

  @Test
  void testNoOAuthInjectionBecauseWrongPredicateValue() throws IOException, JsonValidationException, ConfigNotFoundException {
    setupStandardDefinitionMock(createAdvancedAuth()
        .withPredicateKey(List.of(CREDENTIALS, AUTH_TYPE))
        .withPredicateValue("wrong_auth_type"));
    final JsonNode config = generateJsonConfig();
    final UUID workspaceId = UUID.randomUUID();
    setupOAuthParamMocks(generateOAuthParameters());
    final JsonNode actualConfig = oAuthConfigSupplier.injectSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    assertEquals(config, actualConfig);
    assertNoTracking();
  }

  @Test
  void testNoOAuthMaskingBecauseWrongPredicateValue() throws IOException, JsonValidationException, ConfigNotFoundException {
    setupStandardDefinitionMock(createAdvancedAuth()
        .withPredicateKey(List.of(CREDENTIALS, AUTH_TYPE))
        .withPredicateValue("wrong_auth_type"));
    final JsonNode config = generateJsonConfig();
    final UUID workspaceId = UUID.randomUUID();
    setupOAuthParamMocks(generateOAuthParameters());
    final JsonNode actualConfig = oAuthConfigSupplier.maskSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    assertEquals(config, actualConfig);
  }

  @Test
  void testOAuthInjection() throws JsonValidationException, IOException {
    final JsonNode config = generateJsonConfig();
    final UUID workspaceId = UUID.randomUUID();
    final Map<String, Object> oauthParameters = generateOAuthParameters();
    setupOAuthParamMocks(oauthParameters);
    final JsonNode actualConfig = oAuthConfigSupplier.injectSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    final JsonNode expectedConfig = getExpectedNode((String) oauthParameters.get(API_CLIENT));
    assertEquals(expectedConfig, actualConfig);
    assertTracking(workspaceId);
  }

  @Test
  void testOAuthMasking() throws JsonValidationException, IOException {
    final JsonNode config = generateJsonConfig();
    final UUID workspaceId = UUID.randomUUID();
    final Map<String, Object> oauthParameters = generateOAuthParameters();
    setupOAuthParamMocks(oauthParameters);
    final JsonNode actualConfig = oAuthConfigSupplier.maskSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    final JsonNode expectedConfig = getExpectedNode(MoreOAuthParameters.SECRET_MASK);
    assertEquals(expectedConfig, actualConfig);
  }

  @Test
  void testOAuthInjectionWithoutPredicate() throws JsonValidationException, IOException, ConfigNotFoundException {
    setupStandardDefinitionMock(createAdvancedAuth()
        .withPredicateKey(null)
        .withPredicateValue(null));
    final JsonNode config = generateJsonConfig();
    final UUID workspaceId = UUID.randomUUID();
    final Map<String, Object> oauthParameters = generateOAuthParameters();
    setupOAuthParamMocks(oauthParameters);
    final JsonNode actualConfig = oAuthConfigSupplier.injectSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    final JsonNode expectedConfig = getExpectedNode((String) oauthParameters.get(API_CLIENT));
    assertEquals(expectedConfig, actualConfig);
    assertTracking(workspaceId);
  }

  @Test
  void testOAuthMaskingWithoutPredicate() throws JsonValidationException, IOException, ConfigNotFoundException {
    setupStandardDefinitionMock(createAdvancedAuth()
        .withPredicateKey(null)
        .withPredicateValue(null));
    final JsonNode config = generateJsonConfig();
    final UUID workspaceId = UUID.randomUUID();
    final Map<String, Object> oauthParameters = generateOAuthParameters();
    setupOAuthParamMocks(oauthParameters);
    final JsonNode actualConfig = oAuthConfigSupplier.maskSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    final JsonNode expectedConfig = getExpectedNode(MoreOAuthParameters.SECRET_MASK);
    assertEquals(expectedConfig, actualConfig);
  }

  @Test
  void testOAuthInjectionWithoutPredicateValue() throws JsonValidationException, IOException, ConfigNotFoundException {
    setupStandardDefinitionMock(createAdvancedAuth()
        .withPredicateKey(List.of(CREDENTIALS, AUTH_TYPE))
        .withPredicateValue(""));
    final JsonNode config = generateJsonConfig();
    final UUID workspaceId = UUID.randomUUID();
    final Map<String, Object> oauthParameters = generateOAuthParameters();
    setupOAuthParamMocks(oauthParameters);
    final JsonNode actualConfig = oAuthConfigSupplier.injectSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    final JsonNode expectedConfig = getExpectedNode((String) oauthParameters.get(API_CLIENT));
    assertEquals(expectedConfig, actualConfig);
    assertTracking(workspaceId);
  }

  @Test
  void testOAuthMaskingWithoutPredicateValue() throws JsonValidationException, IOException, ConfigNotFoundException {
    setupStandardDefinitionMock(createAdvancedAuth()
        .withPredicateKey(List.of(CREDENTIALS, AUTH_TYPE))
        .withPredicateValue(""));
    final JsonNode config = generateJsonConfig();
    final UUID workspaceId = UUID.randomUUID();
    final Map<String, Object> oauthParameters = generateOAuthParameters();
    setupOAuthParamMocks(oauthParameters);
    final JsonNode actualConfig = oAuthConfigSupplier.maskSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    final JsonNode expectedConfig = getExpectedNode(MoreOAuthParameters.SECRET_MASK);
    assertEquals(expectedConfig, actualConfig);
  }

  @Test
  void testOAuthFullInjectionBecauseNoOAuthSpec() throws JsonValidationException, IOException, ConfigNotFoundException {
    final JsonNode config = generateJsonConfig();
    final UUID workspaceId = UUID.randomUUID();
    final Map<String, Object> oauthParameters = generateOAuthParameters();
    when(configRepository.getStandardSourceDefinition(any()))
        .thenReturn(testSourceDefinition.withSpec(null));
    setupOAuthParamMocks(oauthParameters);
    final JsonNode actualConfig = oAuthConfigSupplier.injectSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    final ObjectNode expectedConfig = ((ObjectNode) Jsons.clone(config));
    for (final String key : oauthParameters.keySet()) {
      expectedConfig.set(key, Jsons.jsonNode(oauthParameters.get(key)));
    }
    assertEquals(expectedConfig, actualConfig);
    assertTracking(workspaceId);
  }

  @Test
  void testOAuthNoMaskingBecauseNoOAuthSpec() throws JsonValidationException, IOException, ConfigNotFoundException {
    final JsonNode config = generateJsonConfig();
    final UUID workspaceId = UUID.randomUUID();
    final Map<String, Object> oauthParameters = generateOAuthParameters();
    when(configRepository.getStandardSourceDefinition(any()))
        .thenReturn(testSourceDefinition.withSpec(null));
    setupOAuthParamMocks(oauthParameters);
    final JsonNode actualConfig = oAuthConfigSupplier.maskSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    assertEquals(config, actualConfig);
  }

  @Test
  void testOAuthInjectionScopedToWorkspace() throws JsonValidationException, IOException {
    final JsonNode config = generateJsonConfig();
    final UUID workspaceId = UUID.randomUUID();
    final Map<String, Object> oauthParameters = generateOAuthParameters();
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(
        new SourceOAuthParameter()
            .withOauthParameterId(UUID.randomUUID())
            .withSourceDefinitionId(UUID.randomUUID())
            .withWorkspaceId(null)
            .withConfiguration(Jsons.jsonNode(generateOAuthParameters())),
        new SourceOAuthParameter()
            .withOauthParameterId(UUID.randomUUID())
            .withSourceDefinitionId(sourceDefinitionId)
            .withWorkspaceId(workspaceId)
            .withConfiguration(Jsons.jsonNode(oauthParameters))));
    final JsonNode actualConfig = oAuthConfigSupplier.injectSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    final JsonNode expectedConfig = getExpectedNode((String) oauthParameters.get(API_CLIENT));
    assertEquals(expectedConfig, actualConfig);
    assertTracking(workspaceId);
  }

  @Test
  void testOAuthFullInjectionBecauseNoOAuthSpecNestedParameters() throws JsonValidationException, IOException, ConfigNotFoundException {
    // Until https://github.com/airbytehq/airbyte/issues/7624 is solved, we need to handle nested oauth
    // parameters
    final JsonNode config = generateJsonConfig();
    final UUID workspaceId = UUID.randomUUID();
    final Map<String, Object> oauthParameters = generateNestedOAuthParameters();
    setupOAuthParamMocks(oauthParameters);
    final JsonNode actualConfig = oAuthConfigSupplier.injectSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    final JsonNode expectedConfig = Jsons.jsonNode(Map.of(
        "fieldName", "fieldValue",
        CREDENTIALS, Map.of(
            API_SECRET, "123",
            AUTH_TYPE, OAUTH,
            API_CLIENT, ((Map<String, String>) oauthParameters.get(CREDENTIALS)).get(API_CLIENT))));
    assertEquals(expectedConfig, actualConfig);
    assertTracking(workspaceId);
  }

  @Test
  void testOAuthInjectionNestedParameters() throws JsonValidationException, IOException {
    // Until https://github.com/airbytehq/airbyte/issues/7624 is solved, we need to handle nested oauth
    // parameters
    final JsonNode config = generateJsonConfig();
    final UUID workspaceId = UUID.randomUUID();
    final Map<String, Object> oauthParameters = generateNestedOAuthParameters();
    setupOAuthParamMocks(oauthParameters);
    final JsonNode actualConfig = oAuthConfigSupplier.injectSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    final JsonNode expectedConfig = getExpectedNode((String) ((Map<String, Object>) oauthParameters.get(CREDENTIALS)).get(API_CLIENT));
    assertEquals(expectedConfig, actualConfig);
    assertTracking(workspaceId);
  }

  @Test
  void testOAuthMaskingNestedParameters() throws JsonValidationException, IOException {
    // Until https://github.com/airbytehq/airbyte/issues/7624 is solved, we need to handle nested oauth
    // parameters
    final JsonNode config = generateJsonConfig();
    final UUID workspaceId = UUID.randomUUID();
    final Map<String, Object> oauthParameters = generateNestedOAuthParameters();
    setupOAuthParamMocks(oauthParameters);
    final JsonNode actualConfig = oAuthConfigSupplier.maskSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    final JsonNode expectedConfig = getExpectedNode(MoreOAuthParameters.SECRET_MASK);
    assertEquals(expectedConfig, actualConfig);
  }

  private static AdvancedAuth createAdvancedAuth() {
    return new AdvancedAuth()
        .withAuthFlowType(AuthFlowType.OAUTH_2_0)
        .withOauthConfigSpecification(new OAuthConfigSpecification()
            .withCompleteOauthServerOutputSpecification(Jsons.jsonNode(Map.of(PROPERTIES,
                Map.of(API_CLIENT, Map.of(
                    "type", "string",
                    OAuthConfigSupplier.PATH_IN_CONNECTOR_CONFIG, List.of(CREDENTIALS, API_CLIENT)))))));
  }

  private void setupStandardDefinitionMock(final AdvancedAuth advancedAuth) throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.getStandardSourceDefinition(any())).thenReturn(testSourceDefinition
        .withSpec(new ConnectorSpecification().withAdvancedAuth(advancedAuth)));
  }

  private void setupOAuthParamMocks(final Map<String, Object> oauthParameters) throws JsonValidationException, IOException {
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(
        new SourceOAuthParameter()
            .withOauthParameterId(UUID.randomUUID())
            .withSourceDefinitionId(sourceDefinitionId)
            .withWorkspaceId(null)
            .withConfiguration(Jsons.jsonNode(oauthParameters)),
        new SourceOAuthParameter()
            .withOauthParameterId(UUID.randomUUID())
            .withSourceDefinitionId(UUID.randomUUID())
            .withWorkspaceId(null)
            .withConfiguration(Jsons.jsonNode(generateOAuthParameters()))));
  }

  private static ObjectNode generateJsonConfig() {
    return (ObjectNode) Jsons.jsonNode(
        Map.of(
            "fieldName", "fieldValue",
            CREDENTIALS, Map.of(
                API_SECRET, "123",
                AUTH_TYPE, OAUTH)));
  }

  private static Map<String, Object> generateOAuthParameters() {
    return Map.of(
        API_SECRET, "mysecret",
        API_CLIENT, UUID.randomUUID().toString());
  }

  private static Map<String, Object> generateNestedOAuthParameters() {
    return Map.of(CREDENTIALS, generateOAuthParameters());
  }

  private static JsonNode getExpectedNode(final String apiClient) {
    return Jsons.jsonNode(
        Map.of(
            "fieldName", "fieldValue",
            CREDENTIALS, Map.of(
                API_SECRET, "123",
                AUTH_TYPE, OAUTH,
                API_CLIENT, apiClient)));
  }

  private void assertNoTracking() {
    verify(trackingClient, times(0)).track(any(), anyString(), anyMap());
  }

  private void assertTracking(final UUID workspaceId) {
    verify(trackingClient, times(1)).track(workspaceId, "OAuth Injection - Backend", Map.of(
        "connector_source", "test",
        "connector_source_definition_id", sourceDefinitionId,
        "connector_source_docker_repository", "test/test",
        "connector_source_version", "dev"));
  }

}
