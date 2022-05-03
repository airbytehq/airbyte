/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import static io.airbyte.db.instance.configs.migrations.SetupForNormalizedTablesTest.destinationOauthParameters;
import static io.airbyte.db.instance.configs.migrations.SetupForNormalizedTablesTest.now;
import static io.airbyte.db.instance.configs.migrations.SetupForNormalizedTablesTest.sourceOauthParameters;
import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.table;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.db.instance.configs.AbstractConfigsDatabaseTest;
import io.airbyte.db.instance.configs.migrations.V0_32_8_001__AirbyteConfigDatabaseDenormalization.ActorType;
import java.io.IOException;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.UUID;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.JSONB;
import org.jooq.Record;
import org.jooq.Result;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class V0_35_1_001__RemoveForeignKeyFromActorOauth_Test extends AbstractConfigsDatabaseTest {

  @Test
  public void testCompleteMigration() throws IOException, SQLException {
    final DSLContext context = getDslContext();
    SetupForNormalizedTablesTest.setup(context);

    V0_32_8_001__AirbyteConfigDatabaseDenormalization.migrate(context);
    V0_35_1_001__RemoveForeignKeyFromActorOauth.migrate(context);
    assertDataForSourceOauthParams(context);
    assertDataForDestinationOauthParams(context);
  }

  private void assertDataForSourceOauthParams(final DSLContext context) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<UUID> actorDefinitionId = DSL.field("actor_definition_id", SQLDataType.UUID.nullable(false));
    final Field<JSONB> configuration = DSL.field("configuration", SQLDataType.JSONB.nullable(false));
    final Field<UUID> workspaceId = DSL.field("workspace_id", SQLDataType.UUID.nullable(true));
    final Field<ActorType> actorType = DSL.field("actor_type", SQLDataType.VARCHAR.asEnumDataType(ActorType.class).nullable(false));
    final Field<OffsetDateTime> createdAt = DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));
    final Field<OffsetDateTime> updatedAt = DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));

    final Result<Record> sourceOauthParams = context.select(asterisk())
        .from(table("actor_oauth_parameter"))
        .where(actorType.eq(ActorType.source))
        .fetch();
    final List<SourceOAuthParameter> expectedDefinitions = sourceOauthParameters();
    Assertions.assertEquals(expectedDefinitions.size(), sourceOauthParams.size());

    for (final Record record : sourceOauthParams) {
      final SourceOAuthParameter sourceOAuthParameter = new SourceOAuthParameter()
          .withOauthParameterId(record.get(id))
          .withConfiguration(Jsons.deserialize(record.get(configuration).data()))
          .withWorkspaceId(record.get(workspaceId))
          .withSourceDefinitionId(record.get(actorDefinitionId));
      Assertions.assertTrue(expectedDefinitions.contains(sourceOAuthParameter));
      Assertions.assertEquals(now(), record.get(createdAt).toInstant());
      Assertions.assertEquals(now(), record.get(updatedAt).toInstant());
    }
  }

  private void assertDataForDestinationOauthParams(final DSLContext context) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<UUID> actorDefinitionId = DSL.field("actor_definition_id", SQLDataType.UUID.nullable(false));
    final Field<JSONB> configuration = DSL.field("configuration", SQLDataType.JSONB.nullable(false));
    final Field<UUID> workspaceId = DSL.field("workspace_id", SQLDataType.UUID.nullable(true));
    final Field<ActorType> actorType = DSL.field("actor_type", SQLDataType.VARCHAR.asEnumDataType(ActorType.class).nullable(false));
    final Field<OffsetDateTime> createdAt = DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));
    final Field<OffsetDateTime> updatedAt = DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));

    final Result<Record> destinationOauthParams = context.select(asterisk())
        .from(table("actor_oauth_parameter"))
        .where(actorType.eq(ActorType.destination))
        .fetch();
    final List<DestinationOAuthParameter> expectedDefinitions = destinationOauthParameters();
    Assertions.assertEquals(expectedDefinitions.size(), destinationOauthParams.size());

    for (final Record record : destinationOauthParams) {
      final DestinationOAuthParameter destinationOAuthParameter = new DestinationOAuthParameter()
          .withOauthParameterId(record.get(id))
          .withConfiguration(Jsons.deserialize(record.get(configuration).data()))
          .withWorkspaceId(record.get(workspaceId))
          .withDestinationDefinitionId(record.get(actorDefinitionId));
      Assertions.assertTrue(expectedDefinitions.contains(destinationOAuthParameter));
      Assertions.assertEquals(now(), record.get(createdAt).toInstant());
      Assertions.assertEquals(now(), record.get(updatedAt).toInstant());
    }
  }

}
