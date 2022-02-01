package io.airbyte.db.instance.configs.migrations;

import static org.jooq.impl.DSL.currentOffsetDateTime;

import java.time.OffsetDateTime;
import java.util.UUID;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;

public class V0_35_16_001__CreateFeatureFlagTable extends BaseJavaMigration {

  @Override public void migrate(Context context) throws Exception {
    final DSLContext ctx = DSL.using(context.getConnection());

    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<String> name = DSL.field("name", SQLDataType.VARCHAR(256).nullable(false));
    final Field<String> value = DSL.field("value", SQLDataType.LONGNVARCHAR.nullable(true));
    final Field<OffsetDateTime> createdAt =
        DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> updatedAt =
        DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));


    ctx.createTableIfNotExists("feature_flag")
        .column(
            id,
            name,
            value,
            createdAt,
            updatedAt
        )
  }
}
