/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.connectorbuilder.config;

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.temporal.config.WorkerMode;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DatabaseCheckFactory;
import io.airbyte.db.init.DatabaseInitializer;
import io.airbyte.db.instance.DatabaseConstants;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.persistence.job.DefaultJobPersistence;
import io.airbyte.persistence.job.JobPersistence;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import io.micronaut.flyway.FlywayConfigurationProperties;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.io.IOException;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;

/**
 * Micronaut bean factory for database-related singletons.
 */
@Factory
@SuppressWarnings("PMD.AvoidDuplicateLiterals")
public class DatabaseBeanFactory {

  private static final String BASELINE_DESCRIPTION = "Baseline from file-based migration v1";
  private static final Boolean BASELINE_ON_MIGRATION = true;
  private static final String INSTALLED_BY = "BootloaderApp";

  @Singleton
  @Named("configDatabase")
  public Database configDatabase(@Named("config") final DSLContext dslContext) throws IOException {
    return new Database(dslContext);
  }

  @Singleton
  @Named("configFlyway")
  public Flyway configFlyway(@Named("config") final FlywayConfigurationProperties configFlywayConfigurationProperties,
                             @Named("config") final DataSource configDataSource,
                             @Value("${airbyte.bootloader.migration-baseline-version}") final String baselineVersion) {
    return configFlywayConfigurationProperties.getFluentConfiguration()
        .dataSource(configDataSource)
        .baselineVersion(baselineVersion)
        .baselineDescription(BASELINE_DESCRIPTION)
        .baselineOnMigrate(BASELINE_ON_MIGRATION)
        .installedBy(INSTALLED_BY)
        .table(String.format("airbyte_%s_migrations", "configs"))
        .load();
  }

  @Singleton
  public ConfigRepository configRepository(@Named("configDatabase") final Database configDatabase) {
    return new ConfigRepository(configDatabase);
  }

  @Singleton
  @Named("configsDatabaseInitializer")
  public DatabaseInitializer configsDatabaseInitializer(@Named("config") final DSLContext configsDslContext,
                                                        @Value("${airbyte.flyway.configs.initialization-timeout-ms}") final Long configsDatabaseInitializationTimeoutMs)
      throws IOException {
    return DatabaseCheckFactory.createConfigsDatabaseInitializer(configsDslContext,
        configsDatabaseInitializationTimeoutMs, MoreResources.readResource(DatabaseConstants.CONFIGS_INITIAL_SCHEMA_PATH));
  }

  @Singleton
  @Named("configsDatabaseMigrator")
  public DatabaseMigrator configsDatabaseMigrator(@Named("configDatabase") final Database configDatabase,
                                                  @Named("configFlyway") final Flyway configFlyway) {
    return new ConfigsDatabaseMigrator(configDatabase, configFlyway);
  }

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  @Named("jobsDatabase")
  public Database jobsDatabase(@Named("jobs") final DSLContext dslContext) throws IOException {
    return new Database(dslContext);
  }

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  public JobPersistence jobPersistence(@Named("jobsDatabase") final Database jobDatabase) {
    return new DefaultJobPersistence(jobDatabase);
  }

}
