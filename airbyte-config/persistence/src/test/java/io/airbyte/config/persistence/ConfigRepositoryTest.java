/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.split_secrets.MemorySecretPersistence;
import io.airbyte.config.persistence.split_secrets.NoOpSecretsHydrator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ConfigRepositoryTest {

  private static final UUID WORKSPACE_ID = UUID.randomUUID();

  private ConfigPersistence configPersistence;
  private ConfigRepository configRepository;

  @BeforeEach
  void setup() {
    configPersistence = mock(ConfigPersistence.class);
    final var secretPersistence = new MemorySecretPersistence();
    configRepository =
        new ConfigRepository(configPersistence, new NoOpSecretsHydrator(), Optional.of(secretPersistence), Optional.of(secretPersistence));
  }

  @Test
  void testWorkspaceWithNullTombstone() throws ConfigNotFoundException, IOException, JsonValidationException {
    assertReturnsWorkspace(new StandardWorkspace().withWorkspaceId(WORKSPACE_ID));
  }

  @Test
  void testWorkspaceWithFalseTombstone() throws ConfigNotFoundException, IOException, JsonValidationException {
    assertReturnsWorkspace(new StandardWorkspace().withWorkspaceId(WORKSPACE_ID).withTombstone(false));
  }

  @Test
  void testWorkspaceWithTrueTombstone() throws ConfigNotFoundException, IOException, JsonValidationException {
    assertReturnsWorkspace(new StandardWorkspace().withWorkspaceId(WORKSPACE_ID).withTombstone(true));
  }

  void assertReturnsWorkspace(StandardWorkspace workspace) throws ConfigNotFoundException, IOException, JsonValidationException {
    when(configPersistence.getConfig(ConfigSchema.STANDARD_WORKSPACE, WORKSPACE_ID.toString(), StandardWorkspace.class)).thenReturn(workspace);

    assertEquals(workspace, configRepository.getStandardWorkspace(WORKSPACE_ID, true));
  }

}
