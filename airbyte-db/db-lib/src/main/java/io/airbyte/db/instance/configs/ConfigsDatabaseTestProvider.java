/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs;

import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.table;

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.ConfigSchema;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.db.factory.DatabaseCheckFactory;
import io.airbyte.db.init.DatabaseInitializationException;
import io.airbyte.db.instance.DatabaseConstants;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.test.TestDatabaseProvider;
import java.io.IOException;
import java.time.OffsetDateTime;
import java.util.UUID;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;
import org.jooq.JSONB;

public class ConfigsDatabaseTestProvider implements TestDatabaseProvider {

  private final DSLContext dslContext;
  private final Flyway flyway;

  public ConfigsDatabaseTestProvider(final DSLContext dslContext, final Flyway flyway) {
    this.dslContext = dslContext;
    this.flyway = flyway;
  }

  @Override
  public Database create(final boolean runMigration) throws IOException, DatabaseInitializationException {
    final String initalSchema = MoreResources.readResource(DatabaseConstants.CONFIGS_INITIAL_SCHEMA_PATH);
    DatabaseCheckFactory.createConfigsDatabaseInitializer(dslContext, DatabaseConstants.DEFAULT_CONNECTION_TIMEOUT_MS, initalSchema).initialize();

    final Database database = new Database(dslContext);

    if (runMigration) {
      final DatabaseMigrator migrator = new ConfigsDatabaseMigrator(database, flyway);
      migrator.createBaseline();
      migrator.migrate();
    } else {
      // The configs database is considered ready only if there are some seed records.
      // So we need to create at least one record here.
      final OffsetDateTime timestamp = OffsetDateTime.now();
      new ExceptionWrappingDatabase(database).transaction(ctx -> ctx.insertInto(table("airbyte_configs"))
          .set(field("config_id"), UUID.randomUUID().toString())
          .set(field("config_type"), ConfigSchema.STATE.name())
          .set(field("config_blob"), JSONB.valueOf("{}"))
          .set(field("created_at"), timestamp)
          .set(field("updated_at"), timestamp)
          .execute());
    }

    return database;
  }

}
