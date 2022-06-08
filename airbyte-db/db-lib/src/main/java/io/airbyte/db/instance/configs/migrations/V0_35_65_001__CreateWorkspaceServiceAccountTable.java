/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

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

public class V0_35_65_001__CreateWorkspaceServiceAccountTable extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_35_65_001__CreateWorkspaceServiceAccountTable.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    final DSLContext ctx = DSL.using(context.getConnection());
    createAndPopulateWorkspace(ctx);
  }

  private static void createAndPopulateWorkspace(final DSLContext ctx) {
    final Field<UUID> workspaceId = DSL.field("workspace_id", SQLDataType.UUID.nullable(false));
    final Field<String> serviceAccountId = DSL.field("service_account_id", SQLDataType.VARCHAR(31).nullable(false));
    final Field<String> serviceAccountEmail = DSL.field("service_account_email", SQLDataType.VARCHAR(256).nullable(false));
    final Field<JSONB> jsonCredential = DSL.field("json_credential", SQLDataType.JSONB.nullable(false));
    final Field<JSONB> hmacKey = DSL.field("hmac_key", SQLDataType.JSONB.nullable(false));
    final Field<OffsetDateTime> createdAt =
        DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> updatedAt =
        DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));

    ctx.createTableIfNotExists("workspace_service_account")
        .columns(workspaceId,
            serviceAccountId,
            serviceAccountEmail,
            jsonCredential,
            hmacKey,
            createdAt,
            updatedAt)
        .constraints(primaryKey(workspaceId, serviceAccountId),
            foreignKey(workspaceId).references("workspace", "id").onDeleteCascade())
        .execute();
    LOGGER.info("workspace_service_account table created");
  }

}
