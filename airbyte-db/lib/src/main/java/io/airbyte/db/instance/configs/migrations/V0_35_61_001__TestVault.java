/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import java.time.OffsetDateTime;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.impl.DSL;
import org.jooq.util.postgres.PostgresDataType;

public class V0_35_61_001__TestVault extends BaseJavaMigration {

  @Override
  public void migrate(final Context context) throws Exception {
    final DSLContext ctx = DSL.using(context.getConnection());
    final Field<String> encryption_type = DSL.field("encryption_type", PostgresDataType.TEXT.nullable(true));
    final Field<String> encryption_version = DSL.field("encryption_version", PostgresDataType.TEXT.nullable(true));
    final Field<String> root_token = DSL.field("root_token", PostgresDataType.TEXT.nullable(true));
    final Field<String[]> unseal_keys = DSL.field("unseal_keys", PostgresDataType.TEXT.getArrayDataType().nullable(true));
    final Field<OffsetDateTime> created_at = DSL.field("created_at", PostgresDataType.TIMESTAMPTZ.nullable(true));

    ctx.createTableIfNotExists("vault_init_data")
        .columns(encryption_type, encryption_version, root_token, unseal_keys, created_at)
        .execute();
  }

}
