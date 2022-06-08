/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import static org.jooq.impl.DSL.currentOffsetDateTime;

import com.google.common.annotations.VisibleForTesting;
import java.time.OffsetDateTime;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class V0_35_28_001__AddActorCatalogMetadataColumns extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(
      V0_35_28_001__AddActorCatalogMetadataColumns.class);

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    final DSLContext ctx = DSL.using(context.getConnection());
    migrate(ctx);
  }

  @VisibleForTesting
  public static void migrate(final DSLContext ctx) {
    final Field<OffsetDateTime> createdAt =
        DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> modifiedAt =
        DSL.field("modified_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    ctx.alterTable("actor_catalog")
        .addIfNotExists(modifiedAt).execute();
    ctx.alterTable("actor_catalog_fetch_event")
        .addIfNotExists(createdAt).execute();
    ctx.alterTable("actor_catalog_fetch_event")
        .addIfNotExists(modifiedAt).execute();
  }

}
