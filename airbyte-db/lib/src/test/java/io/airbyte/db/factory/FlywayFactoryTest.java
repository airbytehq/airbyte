/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.factory;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.test.utils.DatabaseConnectionHelper;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link FlywayFactory} class.
 */
public class FlywayFactoryTest extends AbstractFactoryTest {

  @Test
  void testCreatingAFlywayInstance() {
    final String installedBy = "test";
    final String dbIdentifier = "test";
    final String baselineVersion = "1.2.3";
    final String baselineDescription = "A test baseline description";
    final boolean baselineOnMigrate = true;
    final String migrationFileLocation = "classpath:io/airbyte/db/instance/toys/migrations";
    final DataSource dataSource = DatabaseConnectionHelper.createDataSource(container);
    final Flyway flyway =
        FlywayFactory.create(dataSource, installedBy, dbIdentifier, baselineVersion, baselineDescription, baselineOnMigrate, migrationFileLocation);
    assertNotNull(flyway);
    assertTrue(flyway.getConfiguration().isBaselineOnMigrate());
    assertEquals(baselineDescription, flyway.getConfiguration().getBaselineDescription());
    assertEquals(baselineVersion, flyway.getConfiguration().getBaselineVersion().getVersion());
    assertEquals(baselineOnMigrate, flyway.getConfiguration().isBaselineOnMigrate());
    assertEquals(installedBy, flyway.getConfiguration().getInstalledBy());
    assertEquals(String.format(FlywayFactory.MIGRATION_TABLE_FORMAT, dbIdentifier), flyway.getConfiguration().getTable());
    assertEquals(migrationFileLocation, flyway.getConfiguration().getLocations()[0].getDescriptor());
  }

  @Test
  void testCreatingAFlywayInstanceWithDefaults() {
    final String installedBy = "test";
    final String dbIdentifier = "test";
    final String migrationFileLocation = "classpath:io/airbyte/db/instance/toys/migrations";
    final DataSource dataSource = DatabaseConnectionHelper.createDataSource(container);
    final Flyway flyway = FlywayFactory.create(dataSource, installedBy, dbIdentifier, migrationFileLocation);
    assertNotNull(flyway);
    assertTrue(flyway.getConfiguration().isBaselineOnMigrate());
    assertEquals(FlywayFactory.BASELINE_DESCRIPTION, flyway.getConfiguration().getBaselineDescription());
    assertEquals(FlywayFactory.BASELINE_VERSION, flyway.getConfiguration().getBaselineVersion().getVersion());
    assertEquals(FlywayFactory.BASELINE_ON_MIGRATION, flyway.getConfiguration().isBaselineOnMigrate());
    assertEquals(installedBy, flyway.getConfiguration().getInstalledBy());
    assertEquals(String.format(FlywayFactory.MIGRATION_TABLE_FORMAT, dbIdentifier), flyway.getConfiguration().getTable());
    assertEquals(migrationFileLocation, flyway.getConfiguration().getLocations()[0].getDescriptor());
  }

}
