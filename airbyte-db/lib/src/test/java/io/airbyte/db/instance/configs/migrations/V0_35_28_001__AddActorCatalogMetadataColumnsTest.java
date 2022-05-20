/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import io.airbyte.db.instance.configs.AbstractConfigsDatabaseTest;
import io.airbyte.db.instance.configs.migrations.V0_32_8_001__AirbyteConfigDatabaseDenormalization.ActorType;
import java.io.IOException;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.UUID;
import org.jooq.DSLContext;
import org.jooq.JSONB;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class V0_35_28_001__AddActorCatalogMetadataColumnsTest extends AbstractConfigsDatabaseTest {

  @Test
  public void test() throws SQLException, IOException {
    final DSLContext context = getDslContext();
    V0_32_8_001__AirbyteConfigDatabaseDenormalization.migrate(context);
    V0_35_26_001__PersistDiscoveredCatalog.migrate(context);
    V0_35_28_001__AddActorCatalogMetadataColumns.migrate(context);
    assertCanInsertSchemaDataWithMetadata(context);
  }

  private void assertCanInsertSchemaDataWithMetadata(final DSLContext ctx) {
    Assertions.assertDoesNotThrow(() -> {
      final UUID catalogId = UUID.randomUUID();
      final UUID actorId = UUID.randomUUID();
      final UUID actorDefinitionId = UUID.randomUUID();
      final UUID workspaceId = UUID.randomUUID();

      ctx.insertInto(DSL.table("workspace"))
          .columns(
              DSL.field("id"),
              DSL.field("name"),
              DSL.field("slug"),
              DSL.field("initial_setup_complete"))
          .values(
              workspaceId,
              "base workspace",
              "base_workspace",
              true)
          .execute();
      ctx.insertInto(DSL.table("actor_definition"))
          .columns(
              DSL.field("id"),
              DSL.field("name"),
              DSL.field("docker_repository"),
              DSL.field("docker_image_tag"),
              DSL.field("actor_type"),
              DSL.field("spec"))
          .values(
              actorDefinitionId,
              "Jenkins",
              "farosai/airbyte-jenkins-source",
              "0.1.23",
              ActorType.source,
              JSONB.valueOf("{}"))
          .execute();
      ctx.insertInto(DSL.table("actor"))
          .columns(
              DSL.field("id"),
              DSL.field("workspace_id"),
              DSL.field("actor_definition_id"),
              DSL.field("name"),
              DSL.field("configuration"),
              DSL.field("actor_type"),
              DSL.field("created_at"),
              DSL.field("updated_at"))
          .values(
              actorId,
              workspaceId,
              actorDefinitionId,
              "JenkinsConnection",
              JSONB.valueOf("{}"),
              ActorType.source,
              OffsetDateTime.now(),
              OffsetDateTime.now())
          .execute();
      ctx.insertInto(DSL.table("actor_catalog"))
          .columns(
              DSL.field("id"),
              DSL.field("catalog"),
              DSL.field("catalog_hash"),
              DSL.field("created_at"),
              DSL.field("modified_at"))
          .values(
              catalogId,
              JSONB.valueOf("{}"),
              "",
              OffsetDateTime.now(),
              OffsetDateTime.now())
          .execute();
      ctx.insertInto(DSL.table("actor_catalog_fetch_event"))
          .columns(
              DSL.field("id"),
              DSL.field("actor_catalog_id"),
              DSL.field("actor_id"),
              DSL.field("config_hash"),
              DSL.field("actor_version"),
              DSL.field("created_at"),
              DSL.field("modified_at"))
          .values(
              UUID.randomUUID(),
              catalogId,
              actorId,
              "HASHVALUE",
              "2.0.1",
              OffsetDateTime.now(),
              OffsetDateTime.now())
          .execute();
    });
  }

}
