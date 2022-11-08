/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import com.google.common.collect.Sets;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ValidatingConfigPersistenceTest {

  public static final UUID UUID_1 = new UUID(0, 1);
  public static final Instant INSTANT = Instant.now();
  public static final StandardSourceDefinition SOURCE_1 = new StandardSourceDefinition();

  static {
    SOURCE_1.withSourceDefinitionId(UUID_1).withName("apache storm");
  }

  public static final UUID UUID_2 = new UUID(0, 2);
  public static final StandardSourceDefinition SOURCE_2 = new StandardSourceDefinition();

  static {
    SOURCE_2.withSourceDefinitionId(UUID_2).withName("apache storm");
  }

  private JsonSchemaValidator schemaValidator;

  private ValidatingConfigPersistence configPersistence;
  private ConfigPersistence decoratedConfigPersistence;
  private static final String ERROR_MESSAGE = "error";

  @BeforeEach
  void setUp() {
    schemaValidator = mock(JsonSchemaValidator.class);

    decoratedConfigPersistence = mock(ConfigPersistence.class);
    configPersistence = new ValidatingConfigPersistence(decoratedConfigPersistence, schemaValidator);
  }

  @Test
  void testWriteConfigSuccess() throws IOException, JsonValidationException {
    configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), SOURCE_1);
    final Map<String, StandardSourceDefinition> aggregatedSource = new HashMap<>();
    aggregatedSource.put(UUID_1.toString(), SOURCE_1);
    verify(decoratedConfigPersistence).writeConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, aggregatedSource);
  }

  @Test
  void testWriteConfigsSuccess() throws IOException, JsonValidationException {
    final Map<String, StandardSourceDefinition> sourceDefinitionById = new HashMap<>();
    sourceDefinitionById.put(UUID_1.toString(), SOURCE_1);
    sourceDefinitionById.put(UUID_2.toString(), SOURCE_2);

    configPersistence.writeConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, sourceDefinitionById);
    verify(decoratedConfigPersistence).writeConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, sourceDefinitionById);
  }

  @Test
  void testWriteConfigFailure() throws JsonValidationException {
    doThrow(new JsonValidationException(ERROR_MESSAGE)).when(schemaValidator).ensure(any(), any());
    assertThrows(JsonValidationException.class,
        () -> configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), SOURCE_1));

    verifyNoInteractions(decoratedConfigPersistence);
  }

  @Test
  void testWriteConfigsFailure() throws JsonValidationException {
    doThrow(new JsonValidationException(ERROR_MESSAGE)).when(schemaValidator).ensure(any(), any());

    final Map<String, StandardSourceDefinition> sourceDefinitionById = new HashMap<>();
    sourceDefinitionById.put(UUID_1.toString(), SOURCE_1);
    sourceDefinitionById.put(UUID_2.toString(), SOURCE_2);

    assertThrows(JsonValidationException.class,
        () -> configPersistence.writeConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, sourceDefinitionById));

    verifyNoInteractions(decoratedConfigPersistence);
  }

  @Test
  void testGetConfigSuccess() throws IOException, JsonValidationException, ConfigNotFoundException {
    when(decoratedConfigPersistence.getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), StandardSourceDefinition.class))
        .thenReturn(SOURCE_1);
    final StandardSourceDefinition actualConfig = configPersistence
        .getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), StandardSourceDefinition.class);

    assertEquals(SOURCE_1, actualConfig);
  }

  @Test
  void testGetConfigFailure() throws IOException, JsonValidationException, ConfigNotFoundException {
    doThrow(new JsonValidationException(ERROR_MESSAGE)).when(schemaValidator).ensure(any(), any());
    when(decoratedConfigPersistence.getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), StandardSourceDefinition.class))
        .thenReturn(SOURCE_1);

    assertThrows(
        JsonValidationException.class,
        () -> configPersistence.getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), StandardSourceDefinition.class));
  }

  @Test
  void testListConfigsSuccess() throws JsonValidationException, IOException {
    when(decoratedConfigPersistence.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class))
        .thenReturn(List.of(SOURCE_1, SOURCE_2));

    final List<StandardSourceDefinition> actualConfigs = configPersistence
        .listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class);

    assertEquals(
        Sets.newHashSet(SOURCE_1, SOURCE_2),
        Sets.newHashSet(actualConfigs));
  }

  @Test
  void testListConfigsFailure() throws JsonValidationException, IOException {
    doThrow(new JsonValidationException(ERROR_MESSAGE)).when(schemaValidator).ensure(any(), any());
    when(decoratedConfigPersistence.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class))
        .thenReturn(List.of(SOURCE_1, SOURCE_2));

    assertThrows(JsonValidationException.class, () -> configPersistence
        .listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class));
  }

  @Test
  void testGetConfigWithMetadataSuccess() throws IOException, JsonValidationException, ConfigNotFoundException {
    when(decoratedConfigPersistence.getConfigWithMetadata(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), StandardSourceDefinition.class))
        .thenReturn(withMetadata(SOURCE_1));
    final ConfigWithMetadata<StandardSourceDefinition> actualConfig = configPersistence
        .getConfigWithMetadata(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), StandardSourceDefinition.class);

    assertEquals(withMetadata(SOURCE_1), actualConfig);
  }

  @Test
  void testGetConfigWithMetadataFailure() throws IOException, JsonValidationException, ConfigNotFoundException {
    doThrow(new JsonValidationException(ERROR_MESSAGE)).when(schemaValidator).ensure(any(), any());
    when(decoratedConfigPersistence.getConfigWithMetadata(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), StandardSourceDefinition.class))
        .thenReturn(withMetadata(SOURCE_1));

    assertThrows(
        JsonValidationException.class,
        () -> configPersistence.getConfigWithMetadata(ConfigSchema.STANDARD_SOURCE_DEFINITION, UUID_1.toString(), StandardSourceDefinition.class));
  }

  @Test
  void testListConfigsWithMetadataSuccess() throws JsonValidationException, IOException {
    when(decoratedConfigPersistence.listConfigsWithMetadata(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class))
        .thenReturn(List.of(withMetadata(SOURCE_1), withMetadata(SOURCE_2)));

    final List<ConfigWithMetadata<StandardSourceDefinition>> actualConfigs = configPersistence
        .listConfigsWithMetadata(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class);

    // noinspection unchecked
    assertEquals(
        Sets.newHashSet(withMetadata(SOURCE_1), withMetadata(SOURCE_2)),
        Sets.newHashSet(actualConfigs));
  }

  @Test
  void testListConfigsWithMetadataFailure() throws JsonValidationException, IOException {
    doThrow(new JsonValidationException(ERROR_MESSAGE)).when(schemaValidator).ensure(any(), any());
    when(decoratedConfigPersistence.listConfigsWithMetadata(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class))
        .thenReturn(List.of(withMetadata(SOURCE_1), withMetadata(SOURCE_2)));

    assertThrows(JsonValidationException.class, () -> configPersistence
        .listConfigsWithMetadata(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class));
  }

  private static ConfigWithMetadata<StandardSourceDefinition> withMetadata(final StandardSourceDefinition sourceDef) {
    return new ConfigWithMetadata<>(sourceDef.getSourceDefinitionId().toString(),
        ConfigSchema.STANDARD_SOURCE_DEFINITION.name(),
        INSTANT,
        INSTANT,
        sourceDef);
  }

}
