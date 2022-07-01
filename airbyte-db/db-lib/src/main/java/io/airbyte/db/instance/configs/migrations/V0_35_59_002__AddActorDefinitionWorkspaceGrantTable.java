/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import static org.jooq.impl.DSL.foreignKey;
import static org.jooq.impl.DSL.unique;

import java.util.UUID;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class V0_35_59_002__AddActorDefinitionWorkspaceGrantTable extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_35_59_002__AddActorDefinitionWorkspaceGrantTable.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    final DSLContext ctx = DSL.using(context.getConnection());
    createActorDefinitionWorkspaceGrant(ctx);
  }

  public static void createActorDefinitionWorkspaceGrant(final DSLContext ctx) {
    final Field<UUID> actorDefinitionId = DSL.field("actor_definition_id", SQLDataType.UUID.nullable(false));
    final Field<UUID> workspaceId = DSL.field("workspace_id", SQLDataType.UUID.nullable(false));
    ctx.createTableIfNotExists("actor_definition_workspace_grant")
        .columns(
            actorDefinitionId,
            workspaceId)
        .constraints(
            unique(workspaceId, actorDefinitionId),
            foreignKey(actorDefinitionId).references("actor_definition", "id").onDeleteCascade(),
            foreignKey(workspaceId).references("workspace", "id").onDeleteCascade())
        .execute();
    LOGGER.info("actor_definition_workspace_grant table created");
  }

}
