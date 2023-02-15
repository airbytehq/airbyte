/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.init.impl;

import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.mock;

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.check.DatabaseCheckException;
import io.airbyte.db.check.impl.ConfigsDatabaseAvailabilityCheck;
import io.airbyte.db.init.DatabaseInitializationException;
import io.airbyte.db.instance.DatabaseConstants;
import java.io.IOException;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link ConfigsDatabaseInitializer} class.
 */
class ConfigsDatabaseInitializerTest extends CommonDatabaseInitializerTest {

  @Test
  void testInitializingSchema() throws IOException {
    final var databaseAvailabilityCheck = mock(ConfigsDatabaseAvailabilityCheck.class);
    final var initialSchema = MoreResources.readResource(DatabaseConstants.CONFIGS_INITIAL_SCHEMA_PATH);
    final var initializer = new ConfigsDatabaseInitializer(databaseAvailabilityCheck, dslContext, initialSchema);

    Assertions.assertDoesNotThrow(() -> initializer.initialize());
    assertTrue(initializer.hasTable(dslContext, initializer.getTableNames().get().stream().findFirst().get()));
  }

  @Test
  void testInitializingSchemaAlreadyExists() throws IOException {
    final var databaseAvailabilityCheck = mock(ConfigsDatabaseAvailabilityCheck.class);
    final var initialSchema = MoreResources.readResource(DatabaseConstants.CONFIGS_INITIAL_SCHEMA_PATH);
    dslContext.execute(initialSchema);
    final var initializer = new ConfigsDatabaseInitializer(databaseAvailabilityCheck, dslContext, initialSchema);

    Assertions.assertDoesNotThrow(() -> initializer.initialize());
    assertTrue(initializer.hasTable(dslContext, initializer.getTableNames().get().stream().findFirst().get()));
  }

  @Test
  void testInitializationException() throws IOException, DatabaseCheckException {
    final var databaseAvailabilityCheck = mock(ConfigsDatabaseAvailabilityCheck.class);
    final var initialSchema = MoreResources.readResource(DatabaseConstants.CONFIGS_INITIAL_SCHEMA_PATH);

    doThrow(new DatabaseCheckException("test")).when(databaseAvailabilityCheck).check();

    final var initializer = new ConfigsDatabaseInitializer(databaseAvailabilityCheck, dslContext, initialSchema);
    Assertions.assertThrows(DatabaseInitializationException.class, () -> initializer.initialize());
  }

}
