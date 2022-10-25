package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.DbMigrationApiController;
import io.airbyte.server.handlers.DbMigrationHandler;
import java.util.Map;
import org.glassfish.hk2.api.Factory;

public class DbMigrationApiFactory implements Factory<DbMigrationApiController> {

  private static DbMigrationHandler dbMigrationHandler;
  private static Map<String, String> mdc;

  public static void setValues(final DbMigrationHandler dbMigrationHandler, final Map<String, String> mdc) {
    DbMigrationApiFactory.dbMigrationHandler = dbMigrationHandler;
    DbMigrationApiFactory.mdc = mdc;
  }

  @Override public DbMigrationApiController provide() {
    return null;
  }

  @Override public void dispose(final DbMigrationApiController instance) {
    /* no op */
  }
}
