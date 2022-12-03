package io.airbyte.config.persistence;

import io.airbyte.db.ExceptionWrappingDatabase;
import java.io.IOException;
import java.util.UUID;
import org.jooq.Table;
import org.jooq.impl.DSL;

/**
 * Commonly used jooq queries that we want to share.
 */
public class JooqQueryHelpers {

  private static final String PRIMARY_KEY = "id";

  /**
   * Deletes all records with given id. If it deletes anything, returns true. Otherwise, false.
   *
   * @param table - table from which to delete the record
   * @param id - id of the record to delete
   * @return true if anything was deleted, otherwise false.
   * @throws IOException - you never know when you io
   */
  @SuppressWarnings("SameParameterValue")
  public static boolean deleteById(final ExceptionWrappingDatabase database, final Table<?> table, final UUID id) throws IOException {
    return database.transaction(ctx -> ctx.deleteFrom(table)).where(DSL.field(DSL.name(PRIMARY_KEY)).eq(id)).execute() > 0;
  }
}
