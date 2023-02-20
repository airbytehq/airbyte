/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.LongNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.TextNode;
import io.airbyte.config.ActorDefinitionConfigInjection;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ConfigInjectionTest extends BaseConfigDatabaseTest {

  private ConfigRepository configRepository;
  private ConfigInjector configInjector;

  private StandardSourceDefinition sourceDefinition;

  private JsonNode exampleConfig;

  ConfigInjectionTest() throws JsonProcessingException {}

  @BeforeEach
  void beforeEach() throws Exception {
    truncateAllTables();
    configRepository = new ConfigRepository(database);
    configInjector = new ConfigInjector(configRepository);
    exampleConfig = new ObjectMapper().readTree("{\"my_config_key\": 123}");
  }

  @Test
  void testInject() throws IOException, JsonValidationException {
    createBaseObjects();

    final JsonNode injected = configInjector.injectConfig(exampleConfig, sourceDefinition.getSourceDefinitionId());
    assertEquals(123, injected.get("my_config_key").longValue(), 123);
    assertEquals("a", injected.get("a").get("injected_under").asText());
    assertEquals("b", injected.get("b").get("injected_under").asText());
    assertFalse(injected.has("c"));
  }

  @Test
  void testInjectOverwrite() throws IOException, JsonValidationException {
    createBaseObjects();

    ((ObjectNode) exampleConfig).set("a", new LongNode(123));
    ((ObjectNode) exampleConfig).remove("my_config_key");

    final JsonNode injected = configInjector.injectConfig(exampleConfig, sourceDefinition.getSourceDefinitionId());
    assertEquals("a", injected.get("a").get("injected_under").asText());
    assertEquals("b", injected.get("b").get("injected_under").asText());
    assertFalse(injected.has("c"));
  }

  @Test
  void testUpdate() throws IOException, JsonValidationException {
    createBaseObjects();

    // write an injection object with the same definition id and the same injection path - will update
    // the existing one
    configRepository.writeActorDefinitionConfigInjectionForPath(new ActorDefinitionConfigInjection()
        .withActorDefinitionId(sourceDefinition.getSourceDefinitionId()).withInjectionPath("a").withJsonToInject(new TextNode("abc")));

    final JsonNode injected = configInjector.injectConfig(exampleConfig, sourceDefinition.getSourceDefinitionId());
    assertEquals(123, injected.get("my_config_key").longValue(), 123);
    assertEquals("abc", injected.get("a").asText());
    assertEquals("b", injected.get("b").get("injected_under").asText());
    assertFalse(injected.has("c"));
  }

  @Test
  void testCreate() throws IOException, JsonValidationException {
    createBaseObjects();

    // write an injection object with the same definition id and a new injection path - will create a
    // new one and leave the others in place
    configRepository.writeActorDefinitionConfigInjectionForPath(new ActorDefinitionConfigInjection()
        .withActorDefinitionId(sourceDefinition.getSourceDefinitionId()).withInjectionPath("c").withJsonToInject(new TextNode("thirdInject")));

    final JsonNode injected = configInjector.injectConfig(exampleConfig, sourceDefinition.getSourceDefinitionId());
    assertEquals(123, injected.get("my_config_key").longValue());
    assertEquals("a", injected.get("a").get("injected_under").asText());
    assertEquals("b", injected.get("b").get("injected_under").asText());
    assertEquals("thirdInject", injected.get("c").asText());
  }

  private void createBaseObjects() throws IOException, JsonValidationException {
    sourceDefinition = createBaseSourceDef();
    configRepository.writeStandardSourceDefinition(sourceDefinition);

    createInjection(sourceDefinition, "a");
    createInjection(sourceDefinition, "b");

    // unreachable injection, should not show up
    final StandardSourceDefinition otherSourceDefinition = createBaseSourceDef();
    configRepository.writeStandardSourceDefinition(otherSourceDefinition);
    createInjection(otherSourceDefinition, "c");
  }

  private ActorDefinitionConfigInjection createInjection(final StandardSourceDefinition definition, final String path)
      throws IOException {
    final ActorDefinitionConfigInjection injection = new ActorDefinitionConfigInjection().withActorDefinitionId(definition.getSourceDefinitionId())
        .withInjectionPath(path).withJsonToInject(new ObjectMapper().readTree("{\"injected_under\": \"" + path + "\"}"));

    configRepository.writeActorDefinitionConfigInjectionForPath(injection);
    return injection;
  }

  private static StandardSourceDefinition createBaseSourceDef() {
    final UUID id = UUID.randomUUID();

    return new StandardSourceDefinition()
        .withName("source-def-" + id)
        .withDockerRepository("source-image-" + id)
        .withDockerImageTag("0.0.1")
        .withSourceDefinitionId(id)
        .withProtocolVersion("0.2.0")
        .withTombstone(false);
  }

}
