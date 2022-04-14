/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.test;

import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.table;

import io.airbyte.config.ConfigSchema;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.development.MigrationDevHelper;
import java.io.IOException;
import java.time.OffsetDateTime;
import java.util.UUID;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.jooq.JSONB;
import org.jooq.SQLDialect;

public class ConfigsDatabaseTestProvider implements TestDatabaseProvider {

  private final DataSource dataSource;

  public ConfigsDatabaseTestProvider(final DataSource dataSource) {
    this.dataSource = dataSource;
  }

  @Override
  public Database create(final boolean runMigration) throws IOException {
    final Database database = new ConfigsDatabaseInstance(Databases.createDslContext(dataSource, SQLDialect.POSTGRES))
        .getAndInitialize();

    if (runMigration) {
      final Flyway migrator = MigrationDevHelper.createMigrator(dataSource, MigrationDevHelper.CONFIGS_DB_IDENTIFIER);
      migrator.baseline();
      migrator.migrate();
    }

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

    return database;
  }

}
