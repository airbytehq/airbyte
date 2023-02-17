package io.airbyte.db.instance.configs.migrations;

import static org.jooq.impl.DSL.currentOffsetDateTime;
import static org.jooq.impl.DSL.foreignKey;
import static org.jooq.impl.DSL.primaryKey;
import static org.jooq.impl.DSL.unique;

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

// TODO: update migration description in the class name
public class V0_41_00_002__AddActorDefinitionConfigInjection extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_41_00_002__AddActorDefinitionConfigInjection.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    try (final DSLContext ctx = DSL.using(context.getConnection())) {
      addConfigInjectionTable(ctx);
    }
  }
  private static void addConfigInjectionTable(final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<JSONB> jsonToInject = DSL.field("json_to_inject", SQLDataType.JSONB.nullable(true));
    final Field<String> injectionPath = DSL.field("injection_path", SQLDataType.VARCHAR(256).nullable(false));
    final Field<UUID> actorDefinitionId = DSL.field("actor_definition_id", SQLDataType.UUID.nullable(true));
    final Field<OffsetDateTime> createdAt =
        DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> updatedAt =
        DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));

    ctx.createTableIfNotExists("actor_definition_config_injection").columns(id, jsonToInject, injectionPath, actorDefinitionId, createdAt, updatedAt)
        .constraints(primaryKey(id),
            foreignKey(actorDefinitionId).references("actor_definition", "id").onDeleteCascade(),
            unique(actorDefinitionId, injectionPath)
            ).execute();
    ctx.createIndexIfNotExists("actor_definition_config_injection_injection_path_idx").on("actor_definition_config_injection", "actor_definition_id", "injection_path").execute();
  }

}
