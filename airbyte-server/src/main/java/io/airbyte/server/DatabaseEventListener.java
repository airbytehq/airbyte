/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.airbyte.db.check.DatabaseCheckException;
import io.airbyte.db.check.DatabaseMigrationCheck;
import io.micronaut.context.event.StartupEvent;
import io.micronaut.core.annotation.Order;
import io.micronaut.runtime.event.annotation.EventListener;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.lang.invoke.MethodHandles;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Singleton
public class DatabaseEventListener {

  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());

  private final DatabaseMigrationCheck configsMigrationCheck;

  private final DatabaseMigrationCheck jobsMigrationCheck;

  public DatabaseEventListener(
                               @Named("configsDatabaseMigrationCheck") final DatabaseMigrationCheck configsMigrationCheck,
                               @Named("jobsDatabaseMigrationCheck") final DatabaseMigrationCheck jobsMigrationCheck) {
    this.configsMigrationCheck = configsMigrationCheck;
    this.jobsMigrationCheck = jobsMigrationCheck;
  }

  @EventListener
  @Order(1)
  public void onStartup(final StartupEvent event) {
    log.info("Checking configs database flyway migration version...");
    try {
      configsMigrationCheck.check();
    } catch (final DatabaseCheckException e) {
      throw new RuntimeException(e);
    }

    log.info("Checking jobs database flyway migration version...");
    try {
      jobsMigrationCheck.check();
    } catch (final DatabaseCheckException e) {
      throw new RuntimeException(e);
    }
  }

}
