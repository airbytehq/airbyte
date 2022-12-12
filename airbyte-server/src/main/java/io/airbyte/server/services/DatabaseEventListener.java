/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.services;

import io.airbyte.db.check.DatabaseCheckException;
import io.airbyte.db.check.DatabaseMigrationCheck;
import io.micronaut.context.event.ApplicationEventListener;
import io.micronaut.core.annotation.Order;
import io.micronaut.runtime.server.event.ServerStartupEvent;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.lang.invoke.MethodHandles;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Singleton
@Order(1)
public class DatabaseEventListener implements ApplicationEventListener<ServerStartupEvent> {

  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());

  private final DatabaseMigrationCheck configsMigrationCheck;

  private final DatabaseMigrationCheck jobsMigrationCheck;

  public DatabaseEventListener(
                               @Named("configsDatabaseMigrationCheck") final DatabaseMigrationCheck configsMigrationCheck,
                               @Named("jobsDatabaseMigrationCheck") final DatabaseMigrationCheck jobsMigrationCheck) {
    this.configsMigrationCheck = configsMigrationCheck;
    this.jobsMigrationCheck = jobsMigrationCheck;
  }

  @Override
  public void onApplicationEvent(final ServerStartupEvent event) {
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
