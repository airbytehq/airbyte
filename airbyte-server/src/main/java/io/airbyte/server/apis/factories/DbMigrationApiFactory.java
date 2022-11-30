/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.DbMigrationApiController;
import io.airbyte.server.handlers.DbMigrationHandler;
import java.util.Map;
import org.glassfish.hk2.api.Factory;
import org.slf4j.MDC;

public class DbMigrationApiFactory implements Factory<DbMigrationApiController> {

  private static DbMigrationHandler dbMigrationHandler;
  private static Map<String, String> mdc;

  public static void setValues(final DbMigrationHandler dbMigrationHandler, final Map<String, String> mdc) {
    DbMigrationApiFactory.dbMigrationHandler = dbMigrationHandler;
    DbMigrationApiFactory.mdc = mdc;
  }

  @Override
  public DbMigrationApiController provide() {
    MDC.setContextMap(DbMigrationApiFactory.mdc);

    return new DbMigrationApiController(dbMigrationHandler);
  }

  @Override
  public void dispose(final DbMigrationApiController instance) {
    /* no op */
  }

}
