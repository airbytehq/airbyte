/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.config;

import io.airbyte.db.check.DatabaseMigrationCheck;
import io.airbyte.db.check.impl.JobsDatabaseAvailabilityCheck;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Replaces;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import org.jooq.DSLContext;
import org.mockito.Mockito;

/**
 * In order to be able to mock the Beans that are defined in a factory, we need to create a Factory
 * dedicated to the test. This could be removed and change to @MockBean annotation once those Beans
 * are moved to @Singleton.
 *
 * If some Beans are added in a factory of the main source folder, we will need to mock it here as
 * well.
 */
@Factory
public class DatabaseBeanFactory {

  @Singleton
  @Named("configsDatabaseMigrationCheck")
  @Replaces(value = DatabaseMigrationCheck.class,
            named = "configsDatabaseMigrationCheck")
  public DatabaseMigrationCheck configsDatabaseMigrationCheck() {
    return Mockito.mock(DatabaseMigrationCheck.class);
  }

  @Singleton
  @Named("jobsDatabaseMigrationCheck")
  @Replaces(value = DatabaseMigrationCheck.class,
            named = "jobsDatabaseMigrationCheck")
  public DatabaseMigrationCheck jobsDatabaseMigrationCheck() {
    return Mockito.mock(DatabaseMigrationCheck.class);
  }

  @Singleton
  @Named("jobsDatabaseAvailabilityCheck")
  @Replaces(value = JobsDatabaseAvailabilityCheck.class,
            named = "jobsDatabaseAvailabilityCheck")
  public JobsDatabaseAvailabilityCheck jobsDatabaseAvailabilityCheck(@Named("config") final DSLContext dslContext) {
    return Mockito.mock(JobsDatabaseAvailabilityCheck.class);
  }

}
