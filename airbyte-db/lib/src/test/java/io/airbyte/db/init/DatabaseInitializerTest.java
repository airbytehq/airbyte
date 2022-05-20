/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.init;

import io.airbyte.db.check.DatabaseAvailabilityCheck;
import java.util.Collection;
import java.util.Optional;
import org.jooq.DSLContext;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;

public class DatabaseInitializerTest {

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
        return null;
      }

      @Override
      public Collection<String> getTableNames() {
        return null;
      }

    };

    Assertions.assertThrows(DatabaseInitializationException.class, () -> initializer.init());
  }

  @Test
  void testDefaultTableNamesMethod() {
    final var initializer = new DatabaseInitializer() {

      @Override
      public void initialize() throws DatabaseInitializationException {}

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
        return null;
      }

    };

    Assertions.assertNotNull(initializer.getTableNames());
    Assertions.assertEquals(0, initializer.getTableNames().size());
  }

}
