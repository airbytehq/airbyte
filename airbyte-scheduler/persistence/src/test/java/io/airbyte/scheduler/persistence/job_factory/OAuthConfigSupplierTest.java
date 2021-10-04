/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_factory;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyBoolean;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.JsonNodeType;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.analytics.Deployment;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Configs.TrackingStrategy;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

public class OAuthConfigSupplierTest {

  private ConfigRepository configRepository;
  private OAuthConfigSupplier oAuthConfigSupplier;

  @BeforeEach
  public void setup() throws JsonValidationException, ConfigNotFoundException, IOException {
    configRepository = mock(ConfigRepository.class);
    oAuthConfigSupplier = new OAuthConfigSupplier(configRepository, false);
    when(configRepository.getStandardSourceDefinition(any())).thenReturn(new StandardSourceDefinition()
        .withSourceDefinitionId(UUID.randomUUID())
        .withName("test")
        .withDockerImageTag("dev"));
    when(configRepository.getStandardDestinationDefinition(any())).thenReturn(new StandardDestinationDefinition()
        .withDestinationDefinitionId(UUID.randomUUID())
        .withName("test")
        .withDockerImageTag("dev"));
    when(configRepository.getStandardWorkspace(any(), anyBoolean())).thenReturn(new StandardWorkspace());
    TrackingClientSingleton.initialize(
        TrackingStrategy.LOGGING,
        mock(Deployment.class),
        "test",
        "dev",
        configRepository);
  }

  @Test
  public void testInjectEmptyOAuthParameters() throws JsonValidationException, IOException, ConfigNotFoundException {
    final JsonNode config = generateJsonConfig();
    final UUID sourceDefinitionId = UUID.randomUUID();
    final UUID workspaceId = UUID.randomUUID();
    final JsonNode actualConfig = oAuthConfigSupplier.injectSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    assertEquals(config, actualConfig);
    assertNoTracking();
  }

  @Test
  public void testInjectGlobalOAuthParameters() throws JsonValidationException, IOException, ConfigNotFoundException {
    final JsonNode config = generateJsonConfig();
    final UUID sourceDefinitionId = UUID.randomUUID();
    final UUID workspaceId = UUID.randomUUID();
    final Map<String, String> oauthParameters = generateOAuthParameters();
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
    final JsonNode actualConfig = oAuthConfigSupplier.injectSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    final ObjectNode expectedConfig = ((ObjectNode) Jsons.clone(config));
    for (String key : oauthParameters.keySet()) {
      expectedConfig.set(key, Jsons.jsonNode(oauthParameters.get(key)));
    }
    assertEquals(expectedConfig, actualConfig);
    assertTracking();
  }

  @Test
  public void testInjectWorkspaceOAuthParameters() throws JsonValidationException, IOException, ConfigNotFoundException {
    final JsonNode config = generateJsonConfig();
    final UUID sourceDefinitionId = UUID.randomUUID();
    final UUID workspaceId = UUID.randomUUID();
    when(configRepository.listSourceOAuthParam()).thenReturn(List.of(
        new SourceOAuthParameter()
            .withOauthParameterId(UUID.randomUUID())
            .withSourceDefinitionId(sourceDefinitionId)
            .withWorkspaceId(null)
            .withConfiguration(Jsons.jsonNode(generateOAuthParameters())),
        new SourceOAuthParameter()
            .withOauthParameterId(UUID.randomUUID())
            .withSourceDefinitionId(sourceDefinitionId)
            .withWorkspaceId(workspaceId)
            .withConfiguration(Jsons.jsonNode(ImmutableMap.<String, Object>builder()
                .put("api_secret", "my secret workspace")
                .put("api_client", Map.of("anyOf", List.of(Map.of("id", "id"), Map.of("service", "account"))))
                .build()))));
    final JsonNode actualConfig = oAuthConfigSupplier.injectSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    final ObjectNode expectedConfig = (ObjectNode) Jsons.clone(config);
    expectedConfig.set("api_secret", Jsons.jsonNode("my secret workspace"));
    expectedConfig.set("api_client", Jsons.jsonNode(Map.of("anyOf", List.of(
        Map.of("id", "id"),
        Map.of("service", "account")))));
    assertEquals(expectedConfig, actualConfig);
    assertTracking();
  }

  @Test
  void testInjectMaskedOAuthParameters() throws JsonValidationException, IOException, ConfigNotFoundException {
    final OAuthConfigSupplier maskingSupplier = new OAuthConfigSupplier(configRepository, true);

    final JsonNode config = generateJsonConfig();
    final UUID sourceDefinitionId = UUID.randomUUID();
    final UUID workspaceId = UUID.randomUUID();
    final Map<String, String> oauthParameters = generateOAuthParameters();
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
    final JsonNode actualConfig = maskingSupplier.injectSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    final ObjectNode expectedConfig = ((ObjectNode) Jsons.clone(config));
    for (String key : oauthParameters.keySet()) {
      expectedConfig.set(key, Jsons.jsonNode(OAuthConfigSupplier.SECRET_MASK));
    }
    assertEquals(expectedConfig, actualConfig);
    assertNoTracking();
  }

  private ObjectNode generateJsonConfig() {
    return (ObjectNode) Jsons.jsonNode(ImmutableMap.builder()
        .put("apiSecret", "123")
        .put("client", "testing")
        .build());
  }

  private Map<String, String> generateOAuthParameters() {
    return ImmutableMap.<String, String>builder()
        .put("api_secret", "mysecret")
        .put("api_client", UUID.randomUUID().toString())
        .build();
  }

  private void maskAllValues(ObjectNode node) {
    for (String key : Jsons.keys(node)) {
      if (node.get(key).getNodeType() == JsonNodeType.OBJECT) {
        maskAllValues((ObjectNode) node.get(key));
      } else {
        node.set(key, Jsons.jsonNode(OAuthConfigSupplier.SECRET_MASK));
      }
    }
  }

  @Test
  void testInjectUnnestedNode_Masked() throws JsonValidationException, ConfigNotFoundException, IOException {
    OAuthConfigSupplier supplier = new OAuthConfigSupplier(configRepository, true);
    ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());
    ObjectNode maskedOauthParams = Jsons.clone(oauthParams);
    maskAllValues(maskedOauthParams);
    ObjectNode actual = generateJsonConfig();
    ObjectNode expected = Jsons.clone(actual);
    expected.setAll(maskedOauthParams);

    supplier.injectJsonNode(actual, oauthParams);
    assertEquals(expected, actual);
    assertNoTracking();
  }

  @Test
  void testInjectUnnestedNode_Unmasked() throws JsonValidationException, ConfigNotFoundException, IOException {
    OAuthConfigSupplier supplier = new OAuthConfigSupplier(configRepository, false);
    ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());

    ObjectNode actual = generateJsonConfig();
    ObjectNode expected = Jsons.clone(actual);
    expected.setAll(oauthParams);

    supplier.injectJsonNode(actual, oauthParams);

    assertEquals(expected, actual);
    assertNoTracking();
  }

  @Test
  void testInjectNewNestedNode_Masked() throws JsonValidationException, ConfigNotFoundException, IOException {
    OAuthConfigSupplier supplier = new OAuthConfigSupplier(configRepository, true);
    ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());
    ObjectNode maskedOauthParams = Jsons.clone(oauthParams);
    maskAllValues(maskedOauthParams);
    ObjectNode nestedConfig = (ObjectNode) Jsons.jsonNode(ImmutableMap.builder()
        .put("oauth_credentials", oauthParams)
        .build());

    // nested node does not exist in actual object
    ObjectNode actual = generateJsonConfig();
    ObjectNode expected = Jsons.clone(actual);
    expected.putObject("oauth_credentials").setAll(maskedOauthParams);

    supplier.injectJsonNode(actual, nestedConfig);
    assertEquals(expected, actual);
    assertNoTracking();
  }

  @Test
  @DisplayName("A nested config should be inserted with the same nesting structure")
  void testInjectNewNestedNode_Unmasked() throws JsonValidationException, ConfigNotFoundException, IOException {
    OAuthConfigSupplier supplier = new OAuthConfigSupplier(configRepository, false);
    ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());
    ObjectNode nestedConfig = (ObjectNode) Jsons.jsonNode(ImmutableMap.builder()
        .put("oauth_credentials", oauthParams)
        .build());

    // nested node does not exist in actual object
    ObjectNode actual = generateJsonConfig();
    ObjectNode expected = Jsons.clone(actual);
    expected.putObject("oauth_credentials").setAll(oauthParams);

    supplier.injectJsonNode(actual, nestedConfig);
    assertEquals(expected, actual);
    assertNoTracking();
  }

  @Test
  @DisplayName("A nested node which partially exists in the main config should be merged into the main config, not overwrite the whole nested object")
  void testInjectedPartiallyExistingNestedNode_Unmasked() throws JsonValidationException, ConfigNotFoundException, IOException {
    OAuthConfigSupplier supplier = new OAuthConfigSupplier(configRepository, false);
    ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());
    ObjectNode nestedConfig = (ObjectNode) Jsons.jsonNode(ImmutableMap.builder()
        .put("oauth_credentials", oauthParams)
        .build());

    // nested node partially exists in actual object
    ObjectNode actual = generateJsonConfig();
    actual.putObject("oauth_credentials").put("irrelevant_field", "_");
    ObjectNode expected = Jsons.clone(actual);
    ((ObjectNode) expected.get("oauth_credentials")).setAll(oauthParams);

    supplier.injectJsonNode(actual, nestedConfig);
    assertEquals(expected, actual);
    assertNoTracking();
  }

  private void assertNoTracking() throws JsonValidationException, ConfigNotFoundException, IOException {
    // No tracking should be triggered, so accessing standard workspaces is unnecessary
    verify(configRepository, times(0)).getStandardWorkspace(any(), anyBoolean());
  }

  private void assertTracking() throws JsonValidationException, ConfigNotFoundException, IOException {
    // Tracking should be triggered, so accessing standard workspaces is necessary
    verify(configRepository, times(2)).getStandardWorkspace(any(), anyBoolean());
  }

}
