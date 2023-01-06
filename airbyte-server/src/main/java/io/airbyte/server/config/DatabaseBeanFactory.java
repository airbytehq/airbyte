/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.config;

import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.config.persistence.StreamResetPersistence;
import io.airbyte.db.Database;
import io.airbyte.db.check.DatabaseMigrationCheck;
import io.airbyte.db.check.impl.JobsDatabaseAvailabilityCheck;
import io.airbyte.db.factory.DatabaseCheckFactory;
import io.airbyte.db.instance.DatabaseConstants;
import io.airbyte.persistence.job.DefaultJobPersistence;
import io.airbyte.persistence.job.JobPersistence;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Value;
import io.micronaut.flyway.FlywayConfigurationProperties;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.io.IOException;
import javax.sql.DataSource;
import lombok.extern.slf4j.Slf4j;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;

/**
 * Micronaut bean factory for database-related singletons.
 */
@Factory
@Slf4j
@SuppressWarnings("PMD.AvoidDuplicateLiterals")
public class DatabaseBeanFactory {

  private static final String BASELINE_DESCRIPTION = "Baseline from file-based migration v1";
  private static final Boolean BASELINE_ON_MIGRATION = true;
  private static final String INSTALLED_BY = "ServerApp";

  @Singleton
  @Named("configDatabase")
  public Database configDatabase(@Named("config") final DSLContext dslContext) throws IOException {
    return new Database(dslContext);
  }

  @Singleton
  @Named("configFlyway")
  public Flyway configFlyway(@Named("config") final FlywayConfigurationProperties configFlywayConfigurationProperties,
                             @Named("config") final DataSource configDataSource,
                             @Value("${airbyte.flyway.configs.minimum-migration-version}") final String baselineVersion) {
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
  @Named("jobsFlyway")
  public Flyway jobsFlyway(@Named("jobs") final FlywayConfigurationProperties jobsFlywayConfigurationProperties,
                           @Named("config") final DataSource jobsDataSource,
                           @Value("${airbyte.flyway.jobs.minimum-migration-version}") final String baselineVersion) {
    return jobsFlywayConfigurationProperties.getFluentConfiguration()
        .dataSource(jobsDataSource)
        .baselineVersion(baselineVersion)
        .baselineDescription(BASELINE_DESCRIPTION)
        .baselineOnMigrate(BASELINE_ON_MIGRATION)
        .installedBy(INSTALLED_BY)
        .table(String.format("airbyte_%s_migrations", "jobs"))
        .load();
  }

  @Singleton
  public ConfigRepository configRepository(@Named("configDatabase") final Database configDatabase) {
    return new ConfigRepository(configDatabase);
  }

  @Singleton
  public JobPersistence jobPersistence(@Named("configDatabase") final Database jobDatabase) {
    return new DefaultJobPersistence(jobDatabase);
  }

  @Singleton
  public StatePersistence statePersistence(@Named("configDatabase") final Database configDatabase) {
    return new StatePersistence(configDatabase);
  }

  @Singleton
  @Named("configsDatabaseMigrationCheck")
  public DatabaseMigrationCheck configsDatabaseMigrationCheck(@Named("config") final DSLContext dslContext,
                                                              @Named("configFlyway") final Flyway configsFlyway,
                                                              @Value("${airbyte.flyway.configs.minimum-migration-version}") final String configsDatabaseMinimumFlywayMigrationVersion,
                                                              @Value("${airbyte.flyway.configs.initialization-timeout-ms}") final Long configsDatabaseInitializationTimeoutMs) {
    log.info("Configs database configuration: {} {}", configsDatabaseMinimumFlywayMigrationVersion, configsDatabaseInitializationTimeoutMs);
    return DatabaseCheckFactory
        .createConfigsDatabaseMigrationCheck(dslContext, configsFlyway, configsDatabaseMinimumFlywayMigrationVersion,
            configsDatabaseInitializationTimeoutMs);
  }

  @Singleton
  @Named("jobsDatabaseMigrationCheck")
  public DatabaseMigrationCheck jobsDatabaseMigrationCheck(@Named("config") final DSLContext dslContext,
                                                           @Named("jobsFlyway") final Flyway jobsFlyway,
                                                           @Value("${airbyte.flyway.jobs.minimum-migration-version}") final String jobsDatabaseMinimumFlywayMigrationVersion,
                                                           @Value("${airbyte.flyway.jobs.initialization-timeout-ms}") final Long jobsDatabaseInitializationTimeoutMs) {
    return DatabaseCheckFactory
        .createJobsDatabaseMigrationCheck(dslContext, jobsFlyway, jobsDatabaseMinimumFlywayMigrationVersion,
            jobsDatabaseInitializationTimeoutMs);
  }

  @Singleton
  @Named("jobsDatabaseAvailabilityCheck")
  public JobsDatabaseAvailabilityCheck jobsDatabaseAvailabilityCheck(@Named("config") final DSLContext dslContext) {
    return new JobsDatabaseAvailabilityCheck(dslContext, DatabaseConstants.DEFAULT_ASSERT_DATABASE_TIMEOUT_MS);
  }

  @Singleton
  public StreamResetPersistence streamResetPersistence(@Named("configDatabase") final Database configDatabase) {
    return new StreamResetPersistence(configDatabase);
  }

}
