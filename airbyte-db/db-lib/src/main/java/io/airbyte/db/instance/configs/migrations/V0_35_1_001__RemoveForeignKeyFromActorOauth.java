/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import static io.airbyte.db.instance.configs.migrations.V0_32_8_001__AirbyteConfigDatabaseDenormalization.actorDefinitionDoesNotExist;
import static io.airbyte.db.instance.configs.migrations.V0_32_8_001__AirbyteConfigDatabaseDenormalization.listConfigsWithMetadata;
import static org.jooq.impl.DSL.currentOffsetDateTime;
import static org.jooq.impl.DSL.select;
import static org.jooq.impl.DSL.table;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.db.instance.configs.migrations.V0_32_8_001__AirbyteConfigDatabaseDenormalization.ActorType;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.List;
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

@SuppressWarnings("PMD.AvoidDuplicateLiterals")
public class V0_35_1_001__RemoveForeignKeyFromActorOauth extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_35_1_001__RemoveForeignKeyFromActorOauth.class);

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
    dropForeignKeyConstraintFromActorOauthTable(ctx);
    populateActorOauthParameter(ctx);
  }

  private static void dropForeignKeyConstraintFromActorOauthTable(final DSLContext ctx) {
    ctx.alterTable("actor_oauth_parameter").dropForeignKey("actor_oauth_parameter_workspace_id_fkey").execute();
    LOGGER.info("actor_oauth_parameter_workspace_id_fkey constraint dropped");
  }

  private static void populateActorOauthParameter(final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<UUID> actorDefinitionId = DSL.field("actor_definition_id", SQLDataType.UUID.nullable(false));
    final Field<JSONB> configuration = DSL.field("configuration", SQLDataType.JSONB.nullable(false));
    final Field<UUID> workspaceId = DSL.field("workspace_id", SQLDataType.UUID.nullable(true));
    final Field<ActorType> actorType = DSL.field("actor_type", SQLDataType.VARCHAR.asEnumDataType(ActorType.class).nullable(false));
    final Field<OffsetDateTime> createdAt =
        DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> updatedAt =
        DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));

    final List<ConfigWithMetadata<SourceOAuthParameter>> sourceOauthParamsWithMetadata = listConfigsWithMetadata(
        ConfigSchema.SOURCE_OAUTH_PARAM,
        SourceOAuthParameter.class,
        ctx);
    long sourceOauthParamRecords = 0L;
    for (final ConfigWithMetadata<SourceOAuthParameter> configWithMetadata : sourceOauthParamsWithMetadata) {
      final SourceOAuthParameter sourceOAuthParameter = configWithMetadata.getConfig();
      if (actorDefinitionDoesNotExist(sourceOAuthParameter.getSourceDefinitionId(), ctx)) {
        LOGGER.warn(
            "Skipping source oauth parameter " + sourceOAuthParameter.getSourceDefinitionId() + " because the specified source definition "
                + sourceOAuthParameter.getSourceDefinitionId()
                + " doesn't exist and violates foreign key constraint.");
        continue;
      } else if (actorOAuthParamExists(sourceOAuthParameter.getOauthParameterId(), ctx)) {
        LOGGER.warn(
            "Skipping source oauth parameter " + sourceOAuthParameter.getOauthParameterId()
                + " because the specified parameter already exists in the table.");
        continue;
      }
      ctx.insertInto(DSL.table("actor_oauth_parameter"))
          .set(id, sourceOAuthParameter.getOauthParameterId())
          .set(workspaceId, sourceOAuthParameter.getWorkspaceId())
          .set(actorDefinitionId, sourceOAuthParameter.getSourceDefinitionId())
          .set(configuration, JSONB.valueOf(Jsons.serialize(sourceOAuthParameter.getConfiguration())))
          .set(actorType, ActorType.source)
          .set(createdAt, OffsetDateTime.ofInstant(configWithMetadata.getCreatedAt(), ZoneOffset.UTC))
          .set(updatedAt, OffsetDateTime.ofInstant(configWithMetadata.getUpdatedAt(), ZoneOffset.UTC))
          .execute();
      sourceOauthParamRecords++;
    }

    LOGGER.info("actor_oauth_parameter table populated with " + sourceOauthParamRecords + " source oauth params records");

    final List<ConfigWithMetadata<DestinationOAuthParameter>> destinationOauthParamsWithMetadata = listConfigsWithMetadata(
        ConfigSchema.DESTINATION_OAUTH_PARAM,
        DestinationOAuthParameter.class,
        ctx);
    long destinationOauthParamRecords = 0L;
    for (final ConfigWithMetadata<DestinationOAuthParameter> configWithMetadata : destinationOauthParamsWithMetadata) {
      final DestinationOAuthParameter destinationOAuthParameter = configWithMetadata.getConfig();
      if (actorDefinitionDoesNotExist(destinationOAuthParameter.getDestinationDefinitionId(), ctx)) {
        LOGGER.warn(
            "Skipping destination oauth parameter " + destinationOAuthParameter.getOauthParameterId()
                + " because the specified destination definition "
                + destinationOAuthParameter.getDestinationDefinitionId()
                + " doesn't exist and violates foreign key constraint.");
        continue;
      } else if (actorOAuthParamExists(destinationOAuthParameter.getOauthParameterId(), ctx)) {
        LOGGER.warn(
            "Skipping destination oauth parameter " + destinationOAuthParameter.getOauthParameterId()
                + " because the specified parameter already exists in the table.");
        continue;
      }
      ctx.insertInto(DSL.table("actor_oauth_parameter"))
          .set(id, destinationOAuthParameter.getOauthParameterId())
          .set(workspaceId, destinationOAuthParameter.getWorkspaceId())
          .set(actorDefinitionId, destinationOAuthParameter.getDestinationDefinitionId())
          .set(configuration, JSONB.valueOf(Jsons.serialize(destinationOAuthParameter.getConfiguration())))
          .set(actorType, ActorType.destination)
          .set(createdAt, OffsetDateTime.ofInstant(configWithMetadata.getCreatedAt(), ZoneOffset.UTC))
          .set(updatedAt, OffsetDateTime.ofInstant(configWithMetadata.getUpdatedAt(), ZoneOffset.UTC))
          .execute();
      destinationOauthParamRecords++;
    }

    LOGGER.info("actor_oauth_parameter table populated with " + destinationOauthParamRecords + " destination oauth params records");
  }

  static boolean actorOAuthParamExists(final UUID oauthParamId, final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    return ctx.fetchExists(select()
        .from(table("actor_oauth_parameter"))
        .where(id.eq(oauthParamId)));
  }

}
