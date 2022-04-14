/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter.config;

import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
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

}
