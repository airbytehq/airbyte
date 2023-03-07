/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import java.util.UUID;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.impl.DSL;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// TODO: update migration description in the class name
public class V0_40_18_004__BackfillActorDefinitionWorkspaceGrant extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(
      V0_40_18_004__BackfillActorDefinitionWorkspaceGrant.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    final DSLContext ctx = DSL.using(context.getConnection());

    var customActorDefinitionIds = ctx.fetch("SELECT id FROM actor_definition WHERE public is false and tombstone is false;");
    var existingWorkspaces = ctx.fetch("SELECT id FROM WORKSPACE where tombstone is false;");

    // Update for all custom connectors - set custom field to true;
    ctx.execute("UPDATE actor_definition"
        + " SET custom = true "
        + " WHERE public is false and tombstone is false;");

    for (final var customActorDefinitionIdRecord : customActorDefinitionIds) {
      for (final var existingWorkspaceRecord : existingWorkspaces) {
        // Populate a record for new table;
        var customActorDefinitionIdValue = customActorDefinitionIdRecord.getValue("id", UUID.class);
        var existingWorkspaceIdValue = existingWorkspaceRecord.getValue("id", UUID.class);

        ctx.execute("INSERT INTO actor_definition_workspace_grant(workspace_id, actor_definition_id) VALUES ({0}, {1})",
            existingWorkspaceIdValue, customActorDefinitionIdValue);
      }
    }
  }

}
