/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader.config;

import io.airbyte.bootloader.Bootloader;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.db.Database;
import io.airbyte.db.instance.FlywayConfigurationConstants;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.micronaut.context.annotation.Factory;
import io.micronaut.flyway.FlywayConfigurationProperties;
import java.io.IOException;
import javax.inject.Inject;
import javax.inject.Named;
import javax.inject.Singleton;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;

@Factory
public class DatabaseBeanFactory {

  @Singleton
  @Named("configDatabase")
  public Database configDatabase(@Named("config") final DSLContext dslContext) throws IOException {
    return new ConfigsDatabaseInstance(dslContext).getAndInitialize();
  }

  @Singleton
  public ConfigPersistence configPersistence(@Named("configDatabase") final Database configDatabase,
                                             final JsonSecretsProcessor jsonSecretsProcessor) {
    return DatabaseConfigPersistence.createWithValidation(configDatabase, jsonSecretsProcessor);
  }

  @Singleton
  @Named("jobsDatabase")
  public Database jobsDatabase(@Named("jobs") final DSLContext dslContext) throws IOException {
    return new JobsDatabaseInstance(dslContext).getAndInitialize();
  }

  @Singleton
  public JobPersistence jobPersistence(@Named("jobsDatabase") final Database jobsDatabase) {
    return new DefaultJobPersistence(jobsDatabase);
  }

  @Singleton
  public ConfigRepository configRepository(final ConfigPersistence configPersistence, @Named("configDatabase") final Database configDatabase) {
    return new ConfigRepository(configPersistence, configDatabase);
  }

  @Singleton
  @Named("configFlyway")
  public Flyway configFlyway(@Named("config") final FlywayConfigurationProperties configFlywayConfigurationProperties,
      @Named("config") final DataSource configDataSource) {
    return configFlywayConfigurationProperties.getFluentConfiguration()
        .dataSource(configDataSource)
        .baselineVersion(FlywayConfigurationConstants.BASELINE_VERSION)
        .baselineDescription(FlywayConfigurationConstants.BASELINE_DESCRIPTION)
        .baselineOnMigrate(FlywayConfigurationConstants.BASELINE_ON_MIGRATION)
        .installedBy(Bootloader.class.getSimpleName())
        .table(String.format("airbyte_%s_migrations", "configs"))
        .load();
  }

  @Singleton
  @Named("jobsFlyway")
  public Flyway jobsFlyway(@Named("jobs") final FlywayConfigurationProperties jobsFlywayConfigurationProperties,
      @Named("jobs") final DataSource jobsDataSource) {
    return jobsFlywayConfigurationProperties.getFluentConfiguration()
        .dataSource(jobsDataSource)
        .baselineVersion(FlywayConfigurationConstants.BASELINE_VERSION)
        .baselineDescription(FlywayConfigurationConstants.BASELINE_DESCRIPTION)
        .baselineOnMigrate(FlywayConfigurationConstants.BASELINE_ON_MIGRATION)
        .installedBy(Bootloader.class.getSimpleName())
        .table(String.format("airbyte_%s_migrations", "jobs"))
        .load();
  }
}
