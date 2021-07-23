package io.airbyte.db.database;

import static org.jooq.impl.DSL.select;

import io.airbyte.db.Database;
import java.io.IOException;
import org.jooq.DSLContext;

public interface DatabaseInstance {

  /**
   * Get a database that is ready to be used.
   */
  Database get();

  /**
   * Get an empty database and initialize it.
   */
  Database getAndInitialize() throws IOException;

  static boolean hasTable(DSLContext ctx, String tableName) {
    return ctx.fetchExists(select()
        .from("information_schema.tables")
        .where(String.format("table_name = '%s'", tableName)));
  }

}
