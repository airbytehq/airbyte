/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
