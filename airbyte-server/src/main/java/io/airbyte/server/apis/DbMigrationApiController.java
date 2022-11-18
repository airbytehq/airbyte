/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.DbMigrationApi;
import io.airbyte.api.model.generated.DbMigrationExecutionRead;
import io.airbyte.api.model.generated.DbMigrationReadList;
import io.airbyte.api.model.generated.DbMigrationRequestBody;
import io.airbyte.server.handlers.DbMigrationHandler;
import javax.ws.rs.Path;

@Path("/v1/db_migrations")
public class DbMigrationApiController implements DbMigrationApi {

  private final DbMigrationHandler dbMigrationHandler;

  public DbMigrationApiController(final DbMigrationHandler dbMigrationHandler) {
    this.dbMigrationHandler = dbMigrationHandler;
  }

  @Override
  public DbMigrationExecutionRead executeMigrations(final DbMigrationRequestBody dbMigrationRequestBody) {
    return ConfigurationApi.execute(() -> dbMigrationHandler.migrate(dbMigrationRequestBody));
  }

  @Override
  public DbMigrationReadList listMigrations(final DbMigrationRequestBody dbMigrationRequestBody) {
    return ConfigurationApi.execute(() -> dbMigrationHandler.list(dbMigrationRequestBody));
  }

}
