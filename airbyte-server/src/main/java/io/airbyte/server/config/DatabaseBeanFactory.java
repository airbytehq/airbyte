/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.config;

import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.db.Database;
import io.airbyte.db.instance.DatabaseInstance;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import io.airbyte.db.instance.jobs.JobsDatabaseMigrator;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Value;
import java.io.IOException;
import javax.inject.Named;
import javax.inject.Singleton;

@Factory
public class DatabaseBeanFactory {

  @Singleton
  @Named("configDatabaseInstance")
  public DatabaseInstance configDatabaseInstance(
                                                 @Value("${airbyte.database.config.user}") final String configDatabaseUser,
                                                 @Value("${airbyte.database.config.password}") final String configDatabasePassword,
                                                 @Value("${airbyte.database.config.url}") final String configDatabaseUrl)
      throws IOException {
    return new ConfigsDatabaseInstance(
        configDatabaseUser,
        configDatabasePassword,
        configDatabaseUrl);
  }

  @Singleton
  @Named("configDatabase")
  public Database configDatabase(@Named("configDatabaseInstance") final DatabaseInstance configDatabaseInstance) {
    return configDatabaseInstance.getInitialized();
  }

  @Singleton
  @Named("configPersistence")
  public ConfigPersistence configPersistence(@Named("configDatabase") final Database configDatabase,
                                             final JsonSecretsProcessor jsonSecretsProcessor) {
    return DatabaseConfigPersistence.createWithValidation(configDatabase, jsonSecretsProcessor);
  }

  @Singleton
  public ConfigRepository configRepository(final ConfigPersistence configPersistence, @Named("configDatabase") final Database configDatabase) {
    return new ConfigRepository(configPersistence, configDatabase);
  }

  @Singleton
  @Named("jobsDatabaseInstance")
  public DatabaseInstance jobsDatabaseInstance(
                                               @Value("${airbyte.database.jobs.user}") final String jobDatabaseUser,
                                               @Value("${airbyte.database.jobs.password}") final String jobDatabasePassword,
                                               @Value("${airbyte.database.jobs.url}") final String jobDatabaseUrl)
      throws IOException {
    return new JobsDatabaseInstance(
        jobDatabaseUser,
        jobDatabasePassword,
        jobDatabaseUrl);
  }

  @Singleton
  @Named("jobDatabase")
  public Database jobDatabase(@Named("jobsDatabaseInstance") final DatabaseInstance jobsDatabaseInstance) {
    return jobsDatabaseInstance.getInitialized();
  }

  @Singleton
  public JobPersistence jobPersistence(@Named("jobDatabase") final Database jobDatabase) {
    return new DefaultJobPersistence(jobDatabase);
  }

  @Singleton
  @Named("configDbMigrator")
  public DatabaseMigrator configDbMirator(@Named("configDatabase") final Database configDatabase) {
    return new ConfigsDatabaseMigrator(configDatabase, DatabaseBeanFactory.class.getSimpleName());
  }

  @Singleton
  @Named("jobDbMigrator")
  public DatabaseMigrator jobDatabseMigrator(@Named("jobDatabase") final Database jobDatabase) {
    return new JobsDatabaseMigrator(jobDatabase, DatabaseBeanFactory.class.getSimpleName());
  }

}
