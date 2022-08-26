/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import io.airbyte.db.instance.configs.AbstractConfigsDatabaseTest;
import io.airbyte.db.instance.configs.migrations.V0_32_8_001__AirbyteConfigDatabaseDenormalization.ActorType;
import io.airbyte.db.instance.configs.migrations.V0_35_15_001__AddReleaseStageAndReleaseDateToActorDefinition.ReleaseStage;
import java.io.IOException;
import java.sql.SQLException;
import java.util.UUID;
import org.jooq.DSLContext;
import org.jooq.JSONB;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class V0_35_15_001__AddReleaseStageAndReleaseDateToActorDefinition_Test extends AbstractConfigsDatabaseTest {

  @Test
  void test() throws SQLException, IOException {
    final DSLContext context = getDslContext();

    // necessary to add actor_definition table
    V0_32_8_001__AirbyteConfigDatabaseDenormalization.migrate(context);

    Assertions.assertFalse(releaseStageColumnExists(context));
    Assertions.assertFalse(releaseDateColumnExists(context));

    V0_35_15_001__AddReleaseStageAndReleaseDateToActorDefinition.createReleaseStageEnum(context);
    V0_35_15_001__AddReleaseStageAndReleaseDateToActorDefinition.addReleaseStageColumn(context);
    V0_35_15_001__AddReleaseStageAndReleaseDateToActorDefinition.addReleaseDateColumn(context);

    Assertions.assertTrue(releaseStageColumnExists(context));
    Assertions.assertTrue(releaseDateColumnExists(context));

    assertReleaseStageEnumWorks(context);
  }

  private static boolean releaseStageColumnExists(final DSLContext ctx) {
    return ctx.fetchExists(DSL.select()
        .from("information_schema.columns")
        .where(DSL.field("table_name").eq("actor_definition")
            .and(DSL.field("column_name").eq("release_stage"))));
  }

  private static boolean releaseDateColumnExists(final DSLContext ctx) {
    return ctx.fetchExists(DSL.select()
        .from("information_schema.columns")
        .where(DSL.field("table_name").eq("actor_definition")
            .and(DSL.field("column_name").eq("release_date"))));
  }

  private static void assertReleaseStageEnumWorks(final DSLContext ctx) {
    Assertions.assertDoesNotThrow(() -> {
      insertWithReleaseStage(ctx, ReleaseStage.alpha);
      insertWithReleaseStage(ctx, ReleaseStage.beta);
      insertWithReleaseStage(ctx, ReleaseStage.generally_available);
      insertWithReleaseStage(ctx, ReleaseStage.custom);
    });
  }

  private static void insertWithReleaseStage(final DSLContext ctx, final ReleaseStage releaseStage) {
    ctx.insertInto(DSL.table("actor_definition"))
        .columns(
            DSL.field("id"),
            DSL.field("name"),
            DSL.field("docker_repository"),
            DSL.field("docker_image_tag"),
            DSL.field("actor_type"),
            DSL.field("spec"),
            DSL.field("release_stage"))
        .values(
            UUID.randomUUID(),
            "name",
            "repo",
            "1.0.0",
            ActorType.source,
            JSONB.valueOf("{}"),
            releaseStage)
        .execute();
  }

}
