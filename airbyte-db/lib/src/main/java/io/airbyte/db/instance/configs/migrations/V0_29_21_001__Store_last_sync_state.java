package io.airbyte.db.instance.configs.migrations;

import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Create a new table to store the latest job state for each standard sync.
 * Ideally the latest state should be copied to the new table in the migration.
 * However,
 */
public class V0_29_21_001__Store_last_sync_state extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_29_21_001__Store_last_sync_state.class);

  private static final String TABLE_NAME = "latest_sync_state";
  private static final String COLUMN_SYNC_ID = "sync_id";
  private static final String COLUMN_STATE = "state";
  private static final String COLUMN_CREATED_AT = "created_at";
  private static final String COLUMN_UPDATED_AT = "updated_at";

  @Override
  public void migrate(Context context) throws Exception {
    DSLContext ctx = DSL.using(context.getConnection());
    ctx.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";");
    ctx.createTable(TABLE_NAME)
        .column(COLUMN_SYNC_ID, SQLDataType.UUID.nullable(false))
        .column(COLUMN_STATE, SQLDataType.JSONB.nullable(false))
        .column(COLUMN_CREATED_AT, SQLDataType.OFFSETDATETIME.nullable(false).defaultValue(DSL.currentOffsetDateTime()))
        .column(COLUMN_UPDATED_AT, SQLDataType.OFFSETDATETIME.nullable(false).defaultValue(DSL.currentOffsetDateTime()))
        .execute();
    ctx.createUniqueIndexIfNotExists(String.format("%s_sync_id_idx", TABLE_NAME))
        .on(TABLE_NAME, COLUMN_SYNC_ID)
        .execute();
  }

}
