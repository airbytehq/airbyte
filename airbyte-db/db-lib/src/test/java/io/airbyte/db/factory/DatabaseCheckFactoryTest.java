/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.factory;

import static org.mockito.Mockito.mock;

import io.airbyte.db.check.impl.ConfigsDatabaseAvailabilityCheck;
import io.airbyte.db.check.impl.ConfigsDatabaseMigrationCheck;
import io.airbyte.db.check.impl.JobsDatabaseAvailabilityCheck;
import io.airbyte.db.check.impl.JobsDatabaseMigrationCheck;
import io.airbyte.db.init.impl.ConfigsDatabaseInitializer;
import io.airbyte.db.init.impl.JobsDatabaseInitializer;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link DatabaseCheckFactory} class.
 */
class DatabaseCheckFactoryTest {

  @Test
  void testCreateConfigsDatabaseAvailabilityCheck() {
    final var dslContext = mock(DSLContext.class);
    final var timeoutMs = 500L;
    final var check = DatabaseCheckFactory.createConfigsDatabaseAvailabilityCheck(dslContext, timeoutMs);

    Assertions.assertNotNull(check);
    Assertions.assertEquals(ConfigsDatabaseAvailabilityCheck.class, check.getClass());
    Assertions.assertEquals(timeoutMs, check.getTimeoutMs());
    Assertions.assertTrue(check.getDslContext().isPresent());
    Assertions.assertEquals(dslContext, check.getDslContext().get());
  }

  @Test
  void testCreateJobsDatabaseAvailabilityCheck() {
    final var dslContext = mock(DSLContext.class);
    final var timeoutMs = 500L;
    final var check = DatabaseCheckFactory.createJobsDatabaseAvailabilityCheck(dslContext, timeoutMs);

    Assertions.assertNotNull(check);
    Assertions.assertEquals(JobsDatabaseAvailabilityCheck.class, check.getClass());
    Assertions.assertEquals(timeoutMs, check.getTimeoutMs());
    Assertions.assertTrue(check.getDslContext().isPresent());
    Assertions.assertEquals(dslContext, check.getDslContext().get());
  }

  @Test
  void testCreateConfigsDatabaseMigrationCheck() {
    final var dslContext = mock(DSLContext.class);
    final var flyway = mock(Flyway.class);
    final var minimumMigrationVersion = "1.2.3";
    final var timeoutMs = 500L;
    final var check = DatabaseCheckFactory.createConfigsDatabaseMigrationCheck(dslContext, flyway, minimumMigrationVersion, timeoutMs);

    Assertions.assertNotNull(check);
    Assertions.assertEquals(ConfigsDatabaseMigrationCheck.class, check.getClass());
    Assertions.assertTrue(check.getDatabaseAvailabilityCheck().isPresent());
    Assertions.assertEquals(ConfigsDatabaseAvailabilityCheck.class, check.getDatabaseAvailabilityCheck().get().getClass());
    Assertions.assertEquals(minimumMigrationVersion, check.getMinimumFlywayVersion());
    Assertions.assertEquals(timeoutMs, check.getTimeoutMs());
    Assertions.assertTrue(check.getFlyway().isPresent());
    Assertions.assertEquals(flyway, check.getFlyway().get());
  }

  @Test
  void testCreateJobsDatabaseMigrationCheck() {
    final var dslContext = mock(DSLContext.class);
    final var flyway = mock(Flyway.class);
    final var minimumMigrationVersion = "1.2.3";
    final var timeoutMs = 500L;
    final var check = DatabaseCheckFactory.createJobsDatabaseMigrationCheck(dslContext, flyway, minimumMigrationVersion, timeoutMs);

    Assertions.assertNotNull(check);
    Assertions.assertEquals(JobsDatabaseMigrationCheck.class, check.getClass());
    Assertions.assertTrue(check.getDatabaseAvailabilityCheck().isPresent());
    Assertions.assertEquals(JobsDatabaseAvailabilityCheck.class, check.getDatabaseAvailabilityCheck().get().getClass());
    Assertions.assertEquals(minimumMigrationVersion, check.getMinimumFlywayVersion());
    Assertions.assertEquals(timeoutMs, check.getTimeoutMs());
    Assertions.assertTrue(check.getFlyway().isPresent());
    Assertions.assertEquals(flyway, check.getFlyway().get());
  }

  @Test
  void testCreateConfigsDatabaseInitializer() {
    final var dslContext = mock(DSLContext.class);
    final var initialSchema = "SELECT 1;";
    final var timeoutMs = 500L;
    final var initializer = DatabaseCheckFactory.createConfigsDatabaseInitializer(dslContext, timeoutMs, initialSchema);

    Assertions.assertNotNull(initializer);
    Assertions.assertEquals(ConfigsDatabaseInitializer.class, initializer.getClass());
    Assertions.assertTrue(initializer.getDatabaseAvailabilityCheck().isPresent());
    Assertions.assertEquals(ConfigsDatabaseAvailabilityCheck.class, initializer.getDatabaseAvailabilityCheck().get().getClass());
    Assertions.assertEquals(timeoutMs, initializer.getDatabaseAvailabilityCheck().get().getTimeoutMs());
    Assertions.assertTrue(initializer.getDslContext().isPresent());
    Assertions.assertEquals(dslContext, initializer.getDslContext().get());
    Assertions.assertEquals(initialSchema, initializer.getInitialSchema());
  }

  @Test
  void testCreateJobsDatabaseInitializer() {
    final var dslContext = mock(DSLContext.class);
    final var initialSchema = "SELECT 1;";
    final var timeoutMs = 500L;
    final var initializer = DatabaseCheckFactory.createJobsDatabaseInitializer(dslContext, timeoutMs, initialSchema);

    Assertions.assertNotNull(initializer);
    Assertions.assertEquals(JobsDatabaseInitializer.class, initializer.getClass());
    Assertions.assertTrue(initializer.getDatabaseAvailabilityCheck().isPresent());
    Assertions.assertEquals(JobsDatabaseAvailabilityCheck.class, initializer.getDatabaseAvailabilityCheck().get().getClass());
    Assertions.assertEquals(timeoutMs, initializer.getDatabaseAvailabilityCheck().get().getTimeoutMs());
    Assertions.assertTrue(initializer.getDslContext().isPresent());
    Assertions.assertEquals(dslContext, initializer.getDslContext().get());
    Assertions.assertEquals(initialSchema, initializer.getInitialSchema());
  }

}
