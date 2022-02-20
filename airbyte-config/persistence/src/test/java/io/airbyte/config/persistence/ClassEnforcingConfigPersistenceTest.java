/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ClassEnforcingConfigPersistenceTest {

  public static final UUID UUID1 = UUID.randomUUID();
  public static final Instant INSTANT = Instant.now();
  public static final StandardWorkspace WORKSPACE = new StandardWorkspace();
  public static final StandardSync STANDARD_SYNC = new StandardSync().withConnectionId(UUID1);

  private ClassEnforcingConfigPersistence configPersistence;
  private ConfigPersistence decoratedConfigPersistence;

  @BeforeEach
  void setUp() {
    decoratedConfigPersistence = mock(ConfigPersistence.class);
    configPersistence = new ClassEnforcingConfigPersistence(decoratedConfigPersistence);
  }

  @Test
  void testWriteConfigSuccess() throws IOException, JsonValidationException {
    configPersistence.writeConfig(ConfigSchema.STANDARD_SYNC, UUID1.toString(), STANDARD_SYNC);
    verify(decoratedConfigPersistence).writeConfig(ConfigSchema.STANDARD_SYNC, UUID1.toString(), STANDARD_SYNC);
  }

  @Test
  void testWriteConfigFailure() {
    assertThrows(IllegalArgumentException.class,
        () -> configPersistence.writeConfig(ConfigSchema.STANDARD_SYNC, UUID1.toString(), WORKSPACE));
    verifyNoInteractions(decoratedConfigPersistence);
  }

  @Test
  void testWriteConfigsSuccess() throws IOException, JsonValidationException {
    final Map<String, StandardSync> configs = ImmutableMap.of(UUID1.toString(), STANDARD_SYNC);
    configPersistence.writeConfigs(ConfigSchema.STANDARD_SYNC, configs);
    verify(decoratedConfigPersistence).writeConfigs(ConfigSchema.STANDARD_SYNC, configs);
  }

  @Test
  void testWriteConfigsFailure() {
    final Map<String, StandardWorkspace> configs = ImmutableMap.of(UUID1.toString(), WORKSPACE);
    assertThrows(IllegalArgumentException.class, () -> configPersistence.writeConfigs(ConfigSchema.STANDARD_SYNC, configs));
    verifyNoInteractions(decoratedConfigPersistence);
  }

  @Test
  void testGetConfigSuccess() throws IOException, JsonValidationException, ConfigNotFoundException {
    when(decoratedConfigPersistence.getConfig(ConfigSchema.STANDARD_SYNC, UUID1.toString(), StandardSync.class))
        .thenReturn(STANDARD_SYNC);
    assertEquals(STANDARD_SYNC, configPersistence.getConfig(ConfigSchema.STANDARD_SYNC, UUID1.toString(), StandardSync.class));
  }

  @Test
  void testGetConfigFailure() {
    assertThrows(IllegalArgumentException.class,
        () -> configPersistence.getConfig(ConfigSchema.STANDARD_SYNC, UUID1.toString(), StandardWorkspace.class));
    verifyNoInteractions(decoratedConfigPersistence);
  }

  @Test
  void testListConfigsSuccess() throws IOException, JsonValidationException {
    when(decoratedConfigPersistence.listConfigs(ConfigSchema.STANDARD_SYNC, StandardSync.class)).thenReturn(List.of(STANDARD_SYNC));
    assertEquals(List.of(STANDARD_SYNC), configPersistence.listConfigs(ConfigSchema.STANDARD_SYNC, StandardSync.class));
  }

  @Test
  void testListConfigsFailure() {
    assertThrows(IllegalArgumentException.class,
        () -> configPersistence.listConfigs(ConfigSchema.STANDARD_SYNC, StandardWorkspace.class));
    verifyNoInteractions(decoratedConfigPersistence);
  }

  @Test
  void testGetConfigWithMetadataSuccess() throws IOException, JsonValidationException, ConfigNotFoundException {
    when(decoratedConfigPersistence.getConfigWithMetadata(ConfigSchema.STANDARD_SYNC, UUID1.toString(), StandardSync.class))
        .thenReturn(withMetadata(STANDARD_SYNC));
    assertEquals(withMetadata(STANDARD_SYNC),
        configPersistence.getConfigWithMetadata(ConfigSchema.STANDARD_SYNC, UUID1.toString(), StandardSync.class));
  }

  @Test
  void testGetConfigWithMetadataFailure() {
    assertThrows(IllegalArgumentException.class,
        () -> configPersistence.getConfigWithMetadata(ConfigSchema.STANDARD_SYNC, UUID1.toString(), StandardWorkspace.class));
    verifyNoInteractions(decoratedConfigPersistence);
  }

  @Test
  void testListConfigsWithMetadataSuccess() throws IOException, JsonValidationException {
    when(decoratedConfigPersistence.listConfigsWithMetadata(ConfigSchema.STANDARD_SYNC, StandardSync.class))
        .thenReturn(List.of(withMetadata(STANDARD_SYNC)));
    assertEquals(
        List.of(withMetadata(STANDARD_SYNC)),
        configPersistence.listConfigsWithMetadata(ConfigSchema.STANDARD_SYNC, StandardSync.class));
  }

  @Test
  void testListConfigsWithMetadataFailure() {
    assertThrows(IllegalArgumentException.class,
        () -> configPersistence.listConfigsWithMetadata(ConfigSchema.STANDARD_SYNC, StandardWorkspace.class));
    verifyNoInteractions(decoratedConfigPersistence);
  }

  @SuppressWarnings("SameParameterValue")
  private static ConfigWithMetadata<StandardSync> withMetadata(final StandardSync actorDefinition) {
    return new ConfigWithMetadata<>(actorDefinition.getConnectionId().toString(),
        ConfigSchema.STANDARD_SYNC.name(),
        INSTANT,
        INSTANT,
        actorDefinition);
  }

}
