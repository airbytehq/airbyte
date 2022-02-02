/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import static org.jooq.impl.DSL.currentOffsetDateTime;
import static org.jooq.impl.DSL.primaryKey;

import com.google.common.annotations.VisibleForTesting;
import java.time.OffsetDateTime;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;

@Slf4j
public class V0_35_16_001__CreateFeatureFlagTable extends BaseJavaMigration {

  @Override
  public void migrate(Context context) throws Exception {
    final DSLContext ctx = DSL.using(context.getConnection());

    log.info("Running migration: {}", this.getClass().getSimpleName());

    createTable(ctx);
  }

  @VisibleForTesting
  void createTable(DSLContext context) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<String> name = DSL.field("name", SQLDataType.VARCHAR(256).nullable(false));
    final Field<String> value = DSL.field("value", SQLDataType.LONGNVARCHAR.nullable(true));
    final Field<OffsetDateTime> createdAt =
        DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> updatedAt =
        DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));

    context.createTableIfNotExists("feature_flag")
        .columns(
            id,
            name,
            value,
            createdAt,
            updatedAt)
        .constraints(primaryKey(id))
        .execute();

    log.info("Feature flag table created");
    context.createIndex("feature_flag_name_idx").on("feature_flag", "name").execute();
    log.info("Feature flag table indexes created");
  }

}
