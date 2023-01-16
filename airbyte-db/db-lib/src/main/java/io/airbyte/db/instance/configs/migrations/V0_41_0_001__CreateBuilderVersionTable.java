
package io.airbyte.db.instance.configs.migrations;

import static org.jooq.impl.DSL.currentOffsetDateTime;
import static org.jooq.impl.DSL.foreignKey;
import static org.jooq.impl.DSL.primaryKey;

import java.time.OffsetDateTime;
import java.util.UUID;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.JSONB;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class V0_41_0_001__CreateBuilderVersionTable extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_41_0_001__CreateBuilderVersionTable.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    final DSLContext ctx = DSL.using(context.getConnection());
    extendSourceType(ctx);
    createAndPopulateWorkspace(ctx);
  }

  private static void extendSourceType(final DSLContext ctx) {
    ctx.alterType("source_type").addValue("builder");
  }

  private static void createAndPopulateWorkspace(final DSLContext ctx) {
    final Field<UUID> builderVersionId = DSL.field("builder_version_id", SQLDataType.UUID.nullable(false));
    final Field<UUID> actorDefinitionId = DSL.field("actor_definition_id", SQLDataType.UUID.nullable(false));
    final Field<String> description = DSL.field("description", SQLDataType.CLOB.nullable(false));
    final Field<JSONB> manifest = DSL.field("manifest", SQLDataType.JSONB.nullable(false));
    final Field<JSONB> spec = DSL.field("spec", SQLDataType.JSONB.nullable(false));
    final Field<Integer> version = DSL.field("version", SQLDataType.INTEGER.nullable(false));
    final Field<OffsetDateTime> createdAt =
        DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> updatedAt =
        DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));

    ctx.createTableIfNotExists("builder_version")
        .columns(builderVersionId,
            actorDefinitionId,
            description,
            manifest,
            spec,
            version,
            createdAt,
            updatedAt)
        .constraints(primaryKey(builderVersionId),
            foreignKey(actorDefinitionId).references("actor_definition", "id").onDeleteCascade())
        .execute();
    LOGGER.info("workspace_service_account table created");
  }

}
