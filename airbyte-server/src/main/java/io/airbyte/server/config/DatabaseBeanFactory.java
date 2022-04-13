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
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.micronaut.context.annotation.Factory;
import java.io.IOException;
import javax.inject.Named;
import javax.inject.Singleton;
import org.jooq.DSLContext;

@Factory
public class DatabaseBeanFactory {

  @Singleton
  @Named("configDatabaseInstance")
  public DatabaseInstance configDatabaseInstance(@Named("config") final DSLContext dslContext)
      throws IOException {
    return new ConfigsDatabaseInstance(dslContext);
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
  public DatabaseInstance jobsDatabaseInstance(@Named("jobs") final DSLContext dslContext)
      throws IOException {
    return new JobsDatabaseInstance(dslContext);
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

}
