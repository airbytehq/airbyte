/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import io.airbyte.db.instance.configs.AbstractConfigsDatabaseTest;
import io.airbyte.db.instance.configs.migrations.V0_32_8_001__AirbyteConfigDatabaseDenormalization.ActorType;
import java.io.IOException;
import java.sql.SQLException;
import java.util.UUID;
import org.jooq.DSLContext;
import org.jooq.JSONB;
import org.jooq.exception.DataAccessException;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class V0_35_59_002__AddActorDefinitionWorkspaceGrantTableTest extends AbstractConfigsDatabaseTest {

  @Test
  public void test() throws SQLException, IOException {
    final DSLContext context = getDslContext();
    V0_32_8_001__AirbyteConfigDatabaseDenormalization.migrate(context);

    final UUID actorDefinitionId = new UUID(0L, 1L);
    context.insertInto(DSL.table("actor_definition"))
        .columns(
            DSL.field("id"),
            DSL.field("name"),
            DSL.field("docker_repository"),
            DSL.field("docker_image_tag"),
            DSL.field("actor_type"),
            DSL.field("spec"))
        .values(
            actorDefinitionId,
            "name",
            "repo",
            "1.0.0",
            ActorType.source,
            JSONB.valueOf("{}"))
        .execute();

    final UUID workspaceId = new UUID(0L, 2L);
    context.insertInto(DSL.table("workspace"))
        .columns(
            DSL.field("id"),
            DSL.field("name"),
            DSL.field("slug"),
            DSL.field("initial_setup_complete"))
        .values(
            workspaceId,
            "default",
            "default",
            true)
        .execute();

    V0_35_59_002__AddActorDefinitionWorkspaceGrantTable.createActorDefinitionWorkspaceGrant(context);
    assertCanInsertActorDefinitionWorkspaceGrant(context, actorDefinitionId, workspaceId);
    assertActorDefinitionWorkspaceGrantConstraints(context);
  }

  private void assertCanInsertActorDefinitionWorkspaceGrant(
                                                            final DSLContext context,
                                                            final UUID actorDefinitionId,
                                                            final UUID workspaceId) {
    Assertions.assertDoesNotThrow(() -> {
      context.insertInto(DSL.table("actor_definition_workspace_grant"))
          .columns(
              DSL.field("actor_definition_id"),
              DSL.field("workspace_id"))
          .values(
              actorDefinitionId,
              workspaceId)
          .execute();
    });
  }

  private void assertActorDefinitionWorkspaceGrantConstraints(final DSLContext context) {
    final Exception e = Assertions.assertThrows(DataAccessException.class, () -> {
      context.insertInto(DSL.table("actor_definition_workspace_grant"))
          .columns(
              DSL.field("actor_definition_id"),
              DSL.field("workspace_id"))
          .values(
              new UUID(0L, 3L),
              new UUID(0L, 4L))
          .execute();
    });
    Assertions.assertTrue(e.getMessage().contains("violates foreign key constraint"));
  }

}
