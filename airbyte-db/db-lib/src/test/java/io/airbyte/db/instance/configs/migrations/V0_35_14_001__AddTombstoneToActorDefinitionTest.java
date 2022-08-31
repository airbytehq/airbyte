/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import io.airbyte.db.instance.configs.AbstractConfigsDatabaseTest;
import io.airbyte.db.instance.configs.migrations.V0_32_8_001__AirbyteConfigDatabaseDenormalization.ActorType;
import java.io.IOException;
import java.sql.SQLException;
import java.util.UUID;
import org.jooq.DSLContext;
import org.jooq.JSONB;
import org.jooq.Record;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class V0_35_14_001__AddTombstoneToActorDefinitionTest extends AbstractConfigsDatabaseTest {

  @Test
  void test() throws SQLException, IOException {
    final DSLContext context = getDslContext();

    // necessary to add actor_definition table
    V0_32_8_001__AirbyteConfigDatabaseDenormalization.migrate(context);

    final UUID id = UUID.randomUUID();
    context.insertInto(DSL.table("actor_definition"))
        .columns(
            DSL.field("id"),
            DSL.field("name"),
            DSL.field("docker_repository"),
            DSL.field("docker_image_tag"),
            DSL.field("actor_type"),
            DSL.field("spec"))
        .values(
            id,
            "name",
            "repo",
            "1.0.0",
            ActorType.source,
            JSONB.valueOf("{}"))
        .execute();

    Assertions.assertFalse(tombstoneColumnExists(context));

    V0_35_14_001__AddTombstoneToActorDefinition.addTombstoneColumn(context);

    Assertions.assertTrue(tombstoneColumnExists(context));
    Assertions.assertTrue(tombstoneDefaultsToFalse(context, id));
  }

  protected static boolean tombstoneColumnExists(final DSLContext ctx) {
    return ctx.fetchExists(DSL.select()
        .from("information_schema.columns")
        .where(DSL.field("table_name").eq("actor_definition")
            .and(DSL.field("column_name").eq("tombstone"))));
  }

  protected static boolean tombstoneDefaultsToFalse(final DSLContext ctx, final UUID id) {
    final Record record = ctx.fetchOne(DSL.select()
        .from("actor_definition")
        .where(DSL.field("id").eq(id)));

    return record.get("tombstone").equals(false);
  }

}
