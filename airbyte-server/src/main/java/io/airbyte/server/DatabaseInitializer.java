/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.airbyte.db.instance.DatabaseInstance;
import io.airbyte.db.instance.MinimumFlywayMigrationVersionCheck;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.jobs.JobsDatabaseMigrator;
import io.micronaut.context.annotation.Value;
import io.micronaut.context.event.StartupEvent;
import io.micronaut.runtime.event.annotation.EventListener;
import javax.inject.Inject;
import javax.inject.Named;
import javax.inject.Singleton;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Performs database initialization logic on application context start.
 */
@Singleton
public class DatabaseInitializer {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabaseInitializer.class);

  @Value("${airbyte.database.config.flyway_minimum_migration_version}")
  private String configDatabaseMinimumFlywayVersion;

  @Value("${airbyte.database.config.initialization_timeout_ms}")
  private Long configDatabaseInitializationTimeoutMs;

  @Inject
  @Named("configDatabaseInstance")
  private DatabaseInstance configDatabaseInstance;

  @Value("${airbyte.database.jobs.flyway_minimum_migration_version}")
  private String jobsDatabaseMinimumFlywayVersion;

  @Value("${airbyte.database.jobs.initialization_timeout_ms}")
  private Long jobsDatabaseInitializationTimeoutMs;

  @Inject
  @Named("jobsDatabaseInstance")
  private DatabaseInstance jobsDatabaseInstance;

  @EventListener
  public void onStartup(final StartupEvent startupEvent) throws InterruptedException {
    initializeConfigDatabase();
    initializeJobsDatabase();
  }

  public void initializeConfigDatabase() throws InterruptedException {
    LOGGER.info("Checking configs database flyway migration version...");
    MinimumFlywayMigrationVersionCheck.assertDatabase(configDatabaseInstance, MinimumFlywayMigrationVersionCheck.DEFAULT_ASSERT_DATABASE_TIMEOUT_MS);
    LOGGER.info("Checking configs database flyway migrations...");
    final ConfigsDatabaseMigrator configsMigrator =
        new ConfigsDatabaseMigrator(configDatabaseInstance.getInitialized(), DatabaseInitializer.class.getName());
    MinimumFlywayMigrationVersionCheck.assertMigrations(configsMigrator, configDatabaseMinimumFlywayVersion, configDatabaseInitializationTimeoutMs);
  }

  private void initializeJobsDatabase() throws InterruptedException {
    LOGGER.info("Checking jobs database flyway migration version..");
    MinimumFlywayMigrationVersionCheck.assertDatabase(jobsDatabaseInstance, MinimumFlywayMigrationVersionCheck.DEFAULT_ASSERT_DATABASE_TIMEOUT_MS);
    LOGGER.info("Checking jobs database flyway migrations...");
    final JobsDatabaseMigrator jobsMigrator = new JobsDatabaseMigrator(jobsDatabaseInstance.getInitialized(), DatabaseInitializer.class.getName());
    MinimumFlywayMigrationVersionCheck.assertMigrations(jobsMigrator, jobsDatabaseMinimumFlywayVersion, jobsDatabaseInitializationTimeoutMs);
  }

}
