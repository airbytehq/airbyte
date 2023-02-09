/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.check.impl;

import io.airbyte.db.check.DatabaseAvailabilityCheck;
import io.airbyte.db.check.DatabaseMigrationCheck;
import java.util.Optional;
import org.flywaydb.core.Flyway;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Implementation of the {@link DatabaseMigrationCheck} for the Configurations database.
 */
public class ConfigsDatabaseMigrationCheck implements DatabaseMigrationCheck {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigsDatabaseMigrationCheck.class);

  // TODO inject via dependency injection framework
  private final ConfigsDatabaseAvailabilityCheck databaseAvailablityCheck;

  // TODO inject via dependency injection framework
  private final Flyway flyway;

  // TODO inject via dependency injection framework
  private final String minimumFlywayVersion;

  // TODO inject via dependency injection framework
  private final long timeoutMs;

  public ConfigsDatabaseMigrationCheck(final ConfigsDatabaseAvailabilityCheck databaseAvailablityCheck,
                                       final Flyway flyway,
                                       final String minimumFlywayVersion,
                                       final long timeoutMs) {
    this.databaseAvailablityCheck = databaseAvailablityCheck;
    this.flyway = flyway;
    this.minimumFlywayVersion = minimumFlywayVersion;
    this.timeoutMs = timeoutMs;
  }

  @Override
  public Optional<DatabaseAvailabilityCheck> getDatabaseAvailabilityCheck() {
    return Optional.ofNullable(databaseAvailablityCheck);
  }

  @Override
  public Optional<Flyway> getFlyway() {
    return Optional.ofNullable(flyway);
  }

  @Override
  public Logger getLogger() {
    return LOGGER;
  }

  @Override
  public String getMinimumFlywayVersion() {
    return minimumFlywayVersion;
  }

  @Override
  public long getTimeoutMs() {
    return timeoutMs;
  }

}
