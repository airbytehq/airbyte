/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import java.util.List;
import java.util.UUID;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.config.StandardWorkspace;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class V0_35_50_001__AddNotificationTable extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_35_50_001__AddNotificationTable.class);

  @Override
  public void migrate(final Context context) throws Exception {
    final DSLContext ctx = DSL.using(context.getConnection());
    migrate(ctx);
  }

  @VisibleForTesting
  public static void migrate(final DSLContext ctx) {
    createNotificationConfigTable(ctx);
    createNotificationConnectionTable(ctx);
  }

  public static void createNotificationConfigTable(final DSLContext ctx) {


    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<String> name = DSL.field("name", SQLDataType.VARCHAR(256).nullable(false));
    final Field<String> webhook = DSL.field("webhook", SQLDataType.VARCHAR(516).nullable(false));

    ctx.createTableIfNotExists("notification_config")
        .columns(id, name, webhook)
        .execute();
    LOGGER.info("workspace table created");
  }

  public static void createNotificationConnectionTable(final DSLContext ctx) {

    final Field<UUID> connectionId = DSL.field("connection_id", SQLDataType.UUID.nullable(true));
    final Field<UUID> notificationId = DSL.field("notification_id", SQLDataType.UUID.nullable(true));
    final Field<Boolean> onSuccess = DSL.field("on_success", SQLDataType.BOOLEAN.nullable(false));
    final Field<Boolean> onFailure = DSL.field("on_failure", SQLDataType.BOOLEAN.nullable(false));


    ctx.createTableIfNotExists("notification_connection")
            .columns(connectionId, notificationId, onSuccess, onFailure)
            .execute();
  }

}
