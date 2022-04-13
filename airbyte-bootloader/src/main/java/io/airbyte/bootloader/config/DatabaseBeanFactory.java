/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.bootloader.config;

import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.db.Database;
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

  // @Singleton
  // @Named("configsDbMigrator")
  // public DatabaseMigrator configsDbMigrator(@Named("configDatabase") final Database configDatabase)
  // {
  // return new ConfigsDatabaseMigrator(configDatabase, Bootloader.class.getSimpleName());
  // }
  //
  // @Singleton
  // @Named("jobsDbMigrator")
  // public DatabaseMigrator jobsDbMigrator(@Named("jobsDatabase") final Database jobsDatabase) {
  // return new JobsDatabaseMigrator(jobsDatabase, Bootloader.class.getSimpleName());
  // }

  @Singleton
  public ConfigRepository configRepository(final ConfigPersistence configPersistence, @Named("configDatabase") final Database configDatabase) {
    return new ConfigRepository(configPersistence, configDatabase);
  }

}
