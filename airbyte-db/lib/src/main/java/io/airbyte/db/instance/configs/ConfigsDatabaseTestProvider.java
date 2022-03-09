/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs;

import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.table;

import io.airbyte.config.ConfigSchema;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.test.TestDatabaseProvider;
import java.io.IOException;
import java.time.OffsetDateTime;
import java.util.UUID;
import org.jooq.JSONB;

public class ConfigsDatabaseTestProvider implements TestDatabaseProvider {

  private final String user;
  private final String password;
  private final String jdbcUrl;

  public ConfigsDatabaseTestProvider(final String user, final String password, final String jdbcUrl) {
    this.user = user;
    this.password = password;
    this.jdbcUrl = jdbcUrl;
  }

  @Override
  public Database create(final boolean runMigration) throws IOException {
    final Database database = new ConfigsDatabaseInstance(user, password, jdbcUrl)
        .getAndInitialize();

    if (runMigration) {
      final DatabaseMigrator migrator = new ConfigsDatabaseMigrator(
          database,
          ConfigsDatabaseTestProvider.class.getSimpleName());
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
