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

package io.airbyte.scheduler.persistence.job_factory;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.JsonNodeType;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.SourceOAuthParameter;
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
  public void setup() {
    configRepository = mock(ConfigRepository.class);
    oAuthConfigSupplier = new OAuthConfigSupplier(configRepository, false);
  }

  @Test
  public void testInjectEmptyOAuthParameters() throws JsonValidationException, IOException {
    final JsonNode config = generateJsonConfig();
    final UUID sourceDefinitionId = UUID.randomUUID();
    final UUID workspaceId = UUID.randomUUID();
    final JsonNode actualConfig = oAuthConfigSupplier.injectSourceOAuthParameters(sourceDefinitionId, workspaceId, Jsons.clone(config));
    assertEquals(config, actualConfig);
  }

  @Test
  public void testInjectGlobalOAuthParameters() throws JsonValidationException, IOException {
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
  }

  @Test
  public void testInjectWorkspaceOAuthParameters() throws JsonValidationException, IOException {
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
  }

  @Test
  void testInjectMaskedOAuthParameters() throws JsonValidationException, IOException {
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
  void testInjectUnnestedNode_Masked() {
    OAuthConfigSupplier supplier = new OAuthConfigSupplier(configRepository, true);
    ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());
    ObjectNode maskedOauthParams = Jsons.clone(oauthParams);
    maskAllValues(maskedOauthParams);
    ObjectNode actual = generateJsonConfig();
    ObjectNode expected = Jsons.clone(actual);
    expected.setAll(maskedOauthParams);

    supplier.injectJsonNode(actual, oauthParams);
    assertEquals(expected, actual);
  }

  @Test
  void testInjectUnnestedNode_Unmasked() {
    OAuthConfigSupplier supplier = new OAuthConfigSupplier(configRepository, false);
    ObjectNode oauthParams = (ObjectNode) Jsons.jsonNode(generateOAuthParameters());

    ObjectNode actual = generateJsonConfig();
    ObjectNode expected = Jsons.clone(actual);
    expected.setAll(oauthParams);

    supplier.injectJsonNode(actual, oauthParams);

    assertEquals(expected, actual);
  }

  @Test
  void testInjectNewNestedNode_Masked() {
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
  }

  @Test
  @DisplayName("A nested config should be inserted with the same nesting structure")
  void testInjectNewNestedNode_Unmasked() {
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
  }

  @Test
  @DisplayName("A nested node which partially exists in the main config should be merged into the main config, not overwrite the whole nested object")
  void testInjectedPartiallyExistingNestedNode_Unmasked() {
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
  }

}
