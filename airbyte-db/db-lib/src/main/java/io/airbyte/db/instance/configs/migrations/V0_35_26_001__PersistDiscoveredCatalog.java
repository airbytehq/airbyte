/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import static org.jooq.impl.DSL.constraint;
import static org.jooq.impl.DSL.foreignKey;
import static org.jooq.impl.DSL.primaryKey;

import com.google.common.annotations.VisibleForTesting;
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

public class V0_35_26_001__PersistDiscoveredCatalog extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_35_26_001__PersistDiscoveredCatalog.class);
  private static final String ACTOR_CATALOG = "actor_catalog";

  @Override
  public void migrate(final Context context) throws Exception {
    LOGGER.info("Running migration: {}", this.getClass().getSimpleName());

    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    final DSLContext ctx = DSL.using(context.getConnection());
    migrate(ctx);
  }

  @VisibleForTesting
  public static void migrate(final DSLContext ctx) {
    createActorCatalog(ctx);
    createCatalogFetchEvent(ctx);
    addConnectionTableForeignKey(ctx);
  }

  private static void createActorCatalog(final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<JSONB> catalog = DSL.field("catalog", SQLDataType.JSONB.nullable(false));
    final Field<String> catalogHash = DSL.field("catalog_hash", SQLDataType.VARCHAR(32).nullable(false));
    final Field<OffsetDateTime> createdAt = DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));
    ctx.createTableIfNotExists(ACTOR_CATALOG)
        .columns(id,
            catalog,
            catalogHash,
            createdAt)
        .constraints(primaryKey(id))
        .execute();
    LOGGER.info("actor_catalog table created");
    ctx.createIndexIfNotExists("actor_catalog_catalog_hash_id_idx").on(ACTOR_CATALOG, "catalog_hash").execute();
  }

  private static void createCatalogFetchEvent(final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<UUID> actorCatalogId = DSL.field("actor_catalog_id", SQLDataType.UUID.nullable(false));
    final Field<UUID> actorId = DSL.field("actor_id", SQLDataType.UUID.nullable(false));
    final Field<String> configHash = DSL.field("config_hash", SQLDataType.VARCHAR(32).nullable(false));
    final Field<String> actorVersion = DSL.field("actor_version", SQLDataType.VARCHAR(256).nullable(false));

    ctx.createTableIfNotExists("actor_catalog_fetch_event")
        .columns(id,
            actorCatalogId,
            actorId,
            configHash,
            actorVersion)
        .constraints(primaryKey(id),
            foreignKey(actorCatalogId).references(ACTOR_CATALOG, "id").onDeleteCascade(),
            foreignKey(actorId).references("actor", "id").onDeleteCascade())
        .execute();
    LOGGER.info("actor_catalog_fetch_event table created");
    ctx.createIndexIfNotExists("actor_catalog_fetch_event_actor_id_idx").on("actor_catalog_fetch_event", "actor_id").execute();
    ctx.createIndexIfNotExists("actor_catalog_fetch_event_actor_catalog_id_idx").on("actor_catalog_fetch_event", "actor_catalog_id").execute();
  }

  private static void addConnectionTableForeignKey(final DSLContext ctx) {
    final Field<UUID> sourceCatalogId = DSL.field("source_catalog_id", SQLDataType.UUID.nullable(true));
    ctx.alterTable("connection")
        .addIfNotExists(sourceCatalogId).execute();
    ctx.alterTable("connection")
        .dropConstraintIfExists("connection_actor_catalog_id_fk");
    ctx.alterTable("connection")
        .add(constraint("connection_actor_catalog_id_fk").foreignKey(sourceCatalogId)
            .references(ACTOR_CATALOG, "id").onDeleteCascade())
        .execute();
  }

}
