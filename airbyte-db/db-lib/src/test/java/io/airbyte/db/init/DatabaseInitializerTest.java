/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.init;

import static org.mockito.Mockito.mock;

import io.airbyte.db.check.DatabaseAvailabilityCheck;
import java.util.Collection;
import java.util.Optional;
import org.jooq.DSLContext;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class DatabaseInitializerTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabaseInitializerTest.class);

  @Test
  void testExceptionHandling() {
    final var initializer = new DatabaseInitializer() {

      @Override
      public void initialize() throws DatabaseInitializationException {
        throw new DatabaseInitializationException("test");
      }

      @Override
      public Optional<DatabaseAvailabilityCheck> getDatabaseAvailabilityCheck() {
        return Optional.empty();
      }

      @Override
      public String getDatabaseName() {
        return null;
      }

      @Override
      public Optional<DSLContext> getDslContext() {
        return Optional.empty();
      }

      @Override
      public String getInitialSchema() {
        return null;
      }

      @Override
      public Logger getLogger() {
        return LOGGER;
      }

      @Override
      public Optional<Collection<String>> getTableNames() {
        return Optional.empty();
      }

    };

    Assertions.assertThrows(DatabaseInitializationException.class, () -> initializer.initialize());
  }

  @Test
  void testEmptyTableNames() {
    final var dslContext = mock(DSLContext.class);
    final var initializer = new DatabaseInitializer() {

      @Override
      public Optional<DatabaseAvailabilityCheck> getDatabaseAvailabilityCheck() {
        return Optional.of(mock(DatabaseAvailabilityCheck.class));
      }

      @Override
      public String getDatabaseName() {
        return null;
      }

      @Override
      public Optional<DSLContext> getDslContext() {
        return Optional.of(dslContext);
      }

      @Override
      public String getInitialSchema() {
        return null;
      }

      @Override
      public Logger getLogger() {
        return LOGGER;
      }

      @Override
      public Optional<Collection<String>> getTableNames() {
        return Optional.empty();
      }

    };

    Assertions.assertEquals(false, initializer.initializeSchema(dslContext));
    Assertions.assertNotNull(initializer.getTableNames());
    Assertions.assertEquals(false, initializer.getTableNames().isPresent());
  }

}
