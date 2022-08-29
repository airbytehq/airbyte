/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.currentOffsetDateTime;
import static org.jooq.impl.DSL.foreignKey;
import static org.jooq.impl.DSL.primaryKey;
import static org.jooq.impl.DSL.select;
import static org.jooq.impl.DSL.table;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncState;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.db.jdbc.JdbcUtils;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;
import org.flywaydb.core.api.migration.BaseJavaMigration;
import org.flywaydb.core.api.migration.Context;
import org.jooq.Catalog;
import org.jooq.DSLContext;
import org.jooq.EnumType;
import org.jooq.Field;
import org.jooq.JSONB;
import org.jooq.Record;
import org.jooq.Result;
import org.jooq.Schema;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.jooq.impl.SchemaImpl;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings("PMD.AvoidDuplicateLiterals")
public class V0_32_8_001__AirbyteConfigDatabaseDenormalization extends BaseJavaMigration {

  private static final Logger LOGGER = LoggerFactory.getLogger(V0_32_8_001__AirbyteConfigDatabaseDenormalization.class);

  @Override
  public void migrate(final Context context) throws Exception {

    // Warning: please do not use any jOOQ generated code to write a migration.
    // As database schema changes, the generated jOOQ code can be deprecated. So
    // old migration may not compile if there is any generated code.
    final DSLContext ctx = DSL.using(context.getConnection());
    migrate(ctx);
  }

  @VisibleForTesting
  public static void migrate(final DSLContext ctx) {
    createEnums(ctx);
    createAndPopulateWorkspace(ctx);
    createAndPopulateActorDefinition(ctx);
    createAndPopulateActor(ctx);
    crateAndPopulateActorOauthParameter(ctx);
    createAndPopulateOperation(ctx);
    createAndPopulateConnection(ctx);
    createAndPopulateState(ctx);
  }

  private static void createEnums(final DSLContext ctx) {
    ctx.createType("source_type").asEnum("api", "file", JdbcUtils.DATABASE_KEY, "custom").execute();
    LOGGER.info("source_type enum created");
    ctx.createType("actor_type").asEnum("source", "destination").execute();
    LOGGER.info("actor_type enum created");
    ctx.createType("operator_type").asEnum("normalization", "dbt").execute();
    LOGGER.info("operator_type enum created");
    ctx.createType("namespace_definition_type").asEnum("source", "destination", "customformat").execute();
    LOGGER.info("namespace_definition_type enum created");
    ctx.createType("status_type").asEnum("active", "inactive", "deprecated").execute();
    LOGGER.info("status_type enum created");
  }

  private static void createAndPopulateWorkspace(final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<String> name = DSL.field("name", SQLDataType.VARCHAR(256).nullable(false));
    final Field<String> slug = DSL.field("slug", SQLDataType.VARCHAR(256).nullable(false));
    final Field<Boolean> initialSetupComplete = DSL.field("initial_setup_complete", SQLDataType.BOOLEAN.nullable(false));
    final Field<UUID> customerId = DSL.field("customer_id", SQLDataType.UUID.nullable(true));
    final Field<String> email = DSL.field("email", SQLDataType.VARCHAR(256).nullable(true));
    final Field<Boolean> anonymousDataCollection = DSL.field("anonymous_data_collection", SQLDataType.BOOLEAN.nullable(true));
    final Field<Boolean> sendNewsletter = DSL.field("send_newsletter", SQLDataType.BOOLEAN.nullable(true));
    final Field<Boolean> sendSecurityUpdates = DSL.field("send_security_updates", SQLDataType.BOOLEAN.nullable(true));
    final Field<Boolean> displaySetupWizard = DSL.field("display_setup_wizard", SQLDataType.BOOLEAN.nullable(true));
    final Field<Boolean> tombstone = DSL.field("tombstone", SQLDataType.BOOLEAN.nullable(false).defaultValue(false));
    final Field<JSONB> notifications = DSL.field("notifications", SQLDataType.JSONB.nullable(true));
    final Field<Boolean> firstSyncComplete = DSL.field("first_sync_complete", SQLDataType.BOOLEAN.nullable(true));
    final Field<Boolean> feedbackComplete = DSL.field("feedback_complete", SQLDataType.BOOLEAN.nullable(true));
    final Field<OffsetDateTime> createdAt =
        DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> updatedAt =
        DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));

    ctx.createTableIfNotExists("workspace")
        .columns(id,
            customerId,
            name,
            slug,
            email,
            initialSetupComplete,
            anonymousDataCollection,
            sendNewsletter,
            sendSecurityUpdates,
            displaySetupWizard,
            tombstone,
            notifications,
            firstSyncComplete,
            feedbackComplete,
            createdAt,
            updatedAt)
        .constraints(primaryKey(id))
        .execute();
    LOGGER.info("workspace table created");
    final List<ConfigWithMetadata<StandardWorkspace>> configsWithMetadata = listConfigsWithMetadata(ConfigSchema.STANDARD_WORKSPACE,
        StandardWorkspace.class,
        ctx);

    for (final ConfigWithMetadata<StandardWorkspace> configWithMetadata : configsWithMetadata) {
      final StandardWorkspace standardWorkspace = configWithMetadata.getConfig();
      ctx.insertInto(DSL.table("workspace"))
          .set(id, standardWorkspace.getWorkspaceId())
          .set(customerId, standardWorkspace.getCustomerId())
          .set(name, standardWorkspace.getName())
          .set(slug, standardWorkspace.getSlug())
          .set(email, standardWorkspace.getEmail())
          .set(initialSetupComplete, standardWorkspace.getInitialSetupComplete())
          .set(anonymousDataCollection, standardWorkspace.getAnonymousDataCollection())
          .set(sendNewsletter, standardWorkspace.getNews())
          .set(sendSecurityUpdates, standardWorkspace.getSecurityUpdates())
          .set(displaySetupWizard, standardWorkspace.getDisplaySetupWizard())
          .set(tombstone, standardWorkspace.getTombstone() != null && standardWorkspace.getTombstone())
          .set(notifications, JSONB.valueOf(Jsons.serialize(standardWorkspace.getNotifications())))
          .set(firstSyncComplete, standardWorkspace.getFirstCompletedSync())
          .set(feedbackComplete, standardWorkspace.getFeedbackDone())
          .set(createdAt, OffsetDateTime.ofInstant(configWithMetadata.getCreatedAt(), ZoneOffset.UTC))
          .set(updatedAt, OffsetDateTime.ofInstant(configWithMetadata.getUpdatedAt(), ZoneOffset.UTC))
          .execute();
    }
    LOGGER.info("workspace table populated with " + configsWithMetadata.size() + " records");
  }

  private static void createAndPopulateActorDefinition(final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<String> name = DSL.field("name", SQLDataType.VARCHAR(256).nullable(false));
    final Field<String> dockerRepository = DSL.field("docker_repository", SQLDataType.VARCHAR(256).nullable(false));
    final Field<String> dockerImageTag = DSL.field("docker_image_tag", SQLDataType.VARCHAR(256).nullable(false));
    final Field<String> documentationUrl = DSL.field("documentation_url", SQLDataType.VARCHAR(256).nullable(true));
    final Field<JSONB> spec = DSL.field("spec", SQLDataType.JSONB.nullable(false));
    final Field<String> icon = DSL.field("icon", SQLDataType.VARCHAR(256).nullable(true));
    final Field<ActorType> actorType = DSL.field("actor_type", SQLDataType.VARCHAR.asEnumDataType(ActorType.class).nullable(false));
    final Field<SourceType> sourceType = DSL.field("source_type", SQLDataType.VARCHAR.asEnumDataType(SourceType.class).nullable(true));
    final Field<OffsetDateTime> createdAt =
        DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> updatedAt =
        DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));

    ctx.createTableIfNotExists("actor_definition")
        .columns(id,
            name,
            dockerRepository,
            dockerImageTag,
            documentationUrl,
            icon,
            actorType,
            sourceType,
            spec,
            createdAt,
            updatedAt)
        .constraints(primaryKey(id))
        .execute();

    LOGGER.info("actor_definition table created");

    final List<ConfigWithMetadata<StandardSourceDefinition>> sourceDefinitionsWithMetadata = listConfigsWithMetadata(
        ConfigSchema.STANDARD_SOURCE_DEFINITION,
        StandardSourceDefinition.class,
        ctx);

    for (final ConfigWithMetadata<StandardSourceDefinition> configWithMetadata : sourceDefinitionsWithMetadata) {
      final StandardSourceDefinition standardSourceDefinition = configWithMetadata.getConfig();
      ctx.insertInto(DSL.table("actor_definition"))
          .set(id, standardSourceDefinition.getSourceDefinitionId())
          .set(name, standardSourceDefinition.getName())
          .set(dockerRepository, standardSourceDefinition.getDockerRepository())
          .set(dockerImageTag, standardSourceDefinition.getDockerImageTag())
          .set(documentationUrl, standardSourceDefinition.getDocumentationUrl())
          .set(icon, standardSourceDefinition.getIcon())
          .set(actorType, ActorType.source)
          .set(sourceType, standardSourceDefinition.getSourceType() == null ? null
              : Enums.toEnum(standardSourceDefinition.getSourceType().value(), SourceType.class).orElseThrow())
          .set(spec, JSONB.valueOf(Jsons.serialize(standardSourceDefinition.getSpec())))
          .set(createdAt, OffsetDateTime.ofInstant(configWithMetadata.getCreatedAt(), ZoneOffset.UTC))
          .set(updatedAt, OffsetDateTime.ofInstant(configWithMetadata.getUpdatedAt(), ZoneOffset.UTC))
          .execute();
    }
    LOGGER.info("actor_definition table populated with " + sourceDefinitionsWithMetadata.size() + " source definition records");

    final List<ConfigWithMetadata<StandardDestinationDefinition>> destinationDefinitionsWithMetadata = listConfigsWithMetadata(
        ConfigSchema.STANDARD_DESTINATION_DEFINITION,
        StandardDestinationDefinition.class,
        ctx);

    for (final ConfigWithMetadata<StandardDestinationDefinition> configWithMetadata : destinationDefinitionsWithMetadata) {
      final StandardDestinationDefinition standardDestinationDefinition = configWithMetadata.getConfig();
      ctx.insertInto(DSL.table("actor_definition"))
          .set(id, standardDestinationDefinition.getDestinationDefinitionId())
          .set(name, standardDestinationDefinition.getName())
          .set(dockerRepository, standardDestinationDefinition.getDockerRepository())
          .set(dockerImageTag, standardDestinationDefinition.getDockerImageTag())
          .set(documentationUrl, standardDestinationDefinition.getDocumentationUrl())
          .set(icon, standardDestinationDefinition.getIcon())
          .set(actorType, ActorType.destination)
          .set(spec, JSONB.valueOf(Jsons.serialize(standardDestinationDefinition.getSpec())))
          .set(createdAt, OffsetDateTime.ofInstant(configWithMetadata.getCreatedAt(), ZoneOffset.UTC))
          .set(updatedAt, OffsetDateTime.ofInstant(configWithMetadata.getUpdatedAt(), ZoneOffset.UTC))
          .execute();
    }
    LOGGER.info("actor_definition table populated with " + destinationDefinitionsWithMetadata.size() + " destination definition records");
  }

  private static void createAndPopulateActor(final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<String> name = DSL.field("name", SQLDataType.VARCHAR(256).nullable(false));
    final Field<UUID> actorDefinitionId = DSL.field("actor_definition_id", SQLDataType.UUID.nullable(false));
    final Field<UUID> workspaceId = DSL.field("workspace_id", SQLDataType.UUID.nullable(false));
    final Field<JSONB> configuration = DSL.field("configuration", SQLDataType.JSONB.nullable(false));
    final Field<ActorType> actorType = DSL.field("actor_type", SQLDataType.VARCHAR.asEnumDataType(ActorType.class).nullable(false));
    final Field<Boolean> tombstone = DSL.field("tombstone", SQLDataType.BOOLEAN.nullable(false).defaultValue(false));
    final Field<OffsetDateTime> createdAt =
        DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> updatedAt =
        DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));

    ctx.createTableIfNotExists("actor")
        .columns(id,
            workspaceId,
            actorDefinitionId,
            name,
            configuration,
            actorType,
            tombstone,
            createdAt,
            updatedAt)
        .constraints(primaryKey(id),
            foreignKey(workspaceId).references("workspace", "id").onDeleteCascade(),
            foreignKey(actorDefinitionId).references("actor_definition", "id").onDeleteCascade())
        .execute();
    ctx.createIndex("actor_actor_definition_id_idx").on("actor", "actor_definition_id").execute();

    LOGGER.info("actor table created");

    final List<ConfigWithMetadata<SourceConnection>> sourcesWithMetadata = listConfigsWithMetadata(
        ConfigSchema.SOURCE_CONNECTION,
        SourceConnection.class,
        ctx);
    long sourceRecords = 0L;
    for (final ConfigWithMetadata<SourceConnection> configWithMetadata : sourcesWithMetadata) {
      final SourceConnection sourceConnection = configWithMetadata.getConfig();
      if (workspaceDoesNotExist(sourceConnection.getWorkspaceId(), ctx)) {
        LOGGER.warn(
            "Skipping source connection " + sourceConnection.getSourceId() + " because the specified workspace " + sourceConnection.getWorkspaceId()
                + " doesn't exist and violates foreign key constraint.");
        continue;
      } else if (actorDefinitionDoesNotExist(sourceConnection.getSourceDefinitionId(), ctx)) {
        LOGGER.warn(
            "Skipping source connection " + sourceConnection.getSourceId() + " because the specified source definition "
                + sourceConnection.getSourceDefinitionId()
                + " doesn't exist and violates foreign key constraint.");
        continue;
      }

      ctx.insertInto(DSL.table("actor"))
          .set(id, sourceConnection.getSourceId())
          .set(workspaceId, sourceConnection.getWorkspaceId())
          .set(actorDefinitionId, sourceConnection.getSourceDefinitionId())
          .set(name, sourceConnection.getName())
          .set(configuration, JSONB.valueOf(Jsons.serialize(sourceConnection.getConfiguration())))
          .set(actorType, ActorType.source)
          .set(tombstone, sourceConnection.getTombstone() != null && sourceConnection.getTombstone())
          .set(createdAt, OffsetDateTime.ofInstant(configWithMetadata.getCreatedAt(), ZoneOffset.UTC))
          .set(updatedAt, OffsetDateTime.ofInstant(configWithMetadata.getUpdatedAt(), ZoneOffset.UTC))
          .execute();
      sourceRecords++;
    }
    LOGGER.info("actor table populated with " + sourceRecords + " source records");

    final List<ConfigWithMetadata<DestinationConnection>> destinationsWithMetadata = listConfigsWithMetadata(
        ConfigSchema.DESTINATION_CONNECTION,
        DestinationConnection.class,
        ctx);
    long destinationRecords = 0L;
    for (final ConfigWithMetadata<DestinationConnection> configWithMetadata : destinationsWithMetadata) {
      final DestinationConnection destinationConnection = configWithMetadata.getConfig();
      if (workspaceDoesNotExist(destinationConnection.getWorkspaceId(), ctx)) {
        LOGGER.warn(
            "Skipping destination connection " + destinationConnection.getDestinationId() + " because the specified workspace "
                + destinationConnection.getWorkspaceId()
                + " doesn't exist and violates foreign key constraint.");
        continue;
      } else if (actorDefinitionDoesNotExist(destinationConnection.getDestinationDefinitionId(), ctx)) {
        LOGGER.warn(
            "Skipping destination connection " + destinationConnection.getDestinationId() + " because the specified source definition "
                + destinationConnection.getDestinationDefinitionId()
                + " doesn't exist and violates foreign key constraint.");
        continue;
      }

      ctx.insertInto(DSL.table("actor"))
          .set(id, destinationConnection.getDestinationId())
          .set(workspaceId, destinationConnection.getWorkspaceId())
          .set(actorDefinitionId, destinationConnection.getDestinationDefinitionId())
          .set(name, destinationConnection.getName())
          .set(configuration, JSONB.valueOf(Jsons.serialize(destinationConnection.getConfiguration())))
          .set(actorType, ActorType.destination)
          .set(tombstone, destinationConnection.getTombstone() != null && destinationConnection.getTombstone())
          .set(createdAt, OffsetDateTime.ofInstant(configWithMetadata.getCreatedAt(), ZoneOffset.UTC))
          .set(updatedAt, OffsetDateTime.ofInstant(configWithMetadata.getUpdatedAt(), ZoneOffset.UTC))
          .execute();
      destinationRecords++;
    }
    LOGGER.info("actor table populated with " + destinationRecords + " destination records");
  }

  @VisibleForTesting
  static boolean workspaceDoesNotExist(final UUID workspaceId, final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    return !ctx.fetchExists(select()
        .from(table("workspace"))
        .where(id.eq(workspaceId)));
  }

  @VisibleForTesting
  static boolean actorDefinitionDoesNotExist(final UUID definitionId, final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    return !ctx.fetchExists(select()
        .from(table("actor_definition"))
        .where(id.eq(definitionId)));
  }

  @VisibleForTesting
  static boolean actorDoesNotExist(final UUID actorId, final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    return !ctx.fetchExists(select()
        .from(table("actor"))
        .where(id.eq(actorId)));
  }

  @VisibleForTesting
  static boolean connectionDoesNotExist(final UUID connectionId, final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    return !ctx.fetchExists(select()
        .from(table("connection"))
        .where(id.eq(connectionId)));
  }

  @VisibleForTesting
  static boolean operationDoesNotExist(final UUID operationId, final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    return !ctx.fetchExists(select()
        .from(table("operation"))
        .where(id.eq(operationId)));
  }

  private static void crateAndPopulateActorOauthParameter(final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<UUID> actorDefinitionId = DSL.field("actor_definition_id", SQLDataType.UUID.nullable(false));
    final Field<JSONB> configuration = DSL.field("configuration", SQLDataType.JSONB.nullable(false));
    final Field<UUID> workspaceId = DSL.field("workspace_id", SQLDataType.UUID.nullable(true));
    final Field<ActorType> actorType = DSL.field("actor_type", SQLDataType.VARCHAR.asEnumDataType(ActorType.class).nullable(false));
    final Field<OffsetDateTime> createdAt =
        DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> updatedAt =
        DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));

    ctx.createTableIfNotExists("actor_oauth_parameter")
        .columns(id,
            workspaceId,
            actorDefinitionId,
            configuration,
            actorType,
            createdAt,
            updatedAt)
        .constraints(primaryKey(id),
            foreignKey(workspaceId).references("workspace", "id").onDeleteCascade(),
            foreignKey(actorDefinitionId).references("actor_definition", "id").onDeleteCascade())
        .execute();

    LOGGER.info("actor_oauth_parameter table created");

    final List<ConfigWithMetadata<SourceOAuthParameter>> sourceOauthParamsWithMetadata = listConfigsWithMetadata(
        ConfigSchema.SOURCE_OAUTH_PARAM,
        SourceOAuthParameter.class,
        ctx);
    long sourceOauthParamRecords = 0L;
    for (final ConfigWithMetadata<SourceOAuthParameter> configWithMetadata : sourceOauthParamsWithMetadata) {
      final SourceOAuthParameter sourceOAuthParameter = configWithMetadata.getConfig();
      if (workspaceDoesNotExist(sourceOAuthParameter.getWorkspaceId(), ctx)) {
        LOGGER.warn(
            "Skipping source oauth parameter " + sourceOAuthParameter.getOauthParameterId() + " because the specified workspace "
                + sourceOAuthParameter.getWorkspaceId()
                + " doesn't exist and violates foreign key constraint.");
        continue;
      } else if (actorDefinitionDoesNotExist(sourceOAuthParameter.getSourceDefinitionId(), ctx)) {
        LOGGER.warn(
            "Skipping source oauth parameter " + sourceOAuthParameter.getSourceDefinitionId() + " because the specified source definition "
                + sourceOAuthParameter.getSourceDefinitionId()
                + " doesn't exist and violates foreign key constraint.");
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
      if (workspaceDoesNotExist(destinationOAuthParameter.getWorkspaceId(), ctx)) {
        LOGGER.warn(
            "Skipping destination oauth parameter " + destinationOAuthParameter.getOauthParameterId() + " because the specified workspace "
                + destinationOAuthParameter.getWorkspaceId()
                + " doesn't exist and violates foreign key constraint.");
        continue;
      } else if (actorDefinitionDoesNotExist(destinationOAuthParameter.getDestinationDefinitionId(), ctx)) {
        LOGGER.warn(
            "Skipping destination oauth parameter " + destinationOAuthParameter.getOauthParameterId()
                + " because the specified destination definition "
                + destinationOAuthParameter.getDestinationDefinitionId()
                + " doesn't exist and violates foreign key constraint.");
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

  private static void createAndPopulateOperation(final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<UUID> workspaceId = DSL.field("workspace_id", SQLDataType.UUID.nullable(false));
    final Field<String> name = DSL.field("name", SQLDataType.VARCHAR(256).nullable(false));
    final Field<OperatorType> operatorType = DSL.field("operator_type", SQLDataType.VARCHAR.asEnumDataType(OperatorType.class).nullable(false));
    final Field<JSONB> operatorNormalization = DSL.field("operator_normalization", SQLDataType.JSONB.nullable(true));
    final Field<JSONB> operatorDbt = DSL.field("operator_dbt", SQLDataType.JSONB.nullable(true));
    final Field<Boolean> tombstone = DSL.field("tombstone", SQLDataType.BOOLEAN.nullable(false).defaultValue(false));
    final Field<OffsetDateTime> createdAt =
        DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> updatedAt =
        DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));

    ctx.createTableIfNotExists("operation")
        .columns(id,
            workspaceId,
            name,
            operatorType,
            operatorNormalization,
            operatorDbt,
            tombstone,
            createdAt,
            updatedAt)
        .constraints(primaryKey(id),
            foreignKey(workspaceId).references("workspace", "id").onDeleteCascade())
        .execute();

    LOGGER.info("operation table created");

    final List<ConfigWithMetadata<StandardSyncOperation>> configsWithMetadata = listConfigsWithMetadata(
        ConfigSchema.STANDARD_SYNC_OPERATION,
        StandardSyncOperation.class,
        ctx);
    long standardSyncOperationRecords = 0L;
    for (final ConfigWithMetadata<StandardSyncOperation> configWithMetadata : configsWithMetadata) {
      final StandardSyncOperation standardSyncOperation = configWithMetadata.getConfig();
      if (workspaceDoesNotExist(standardSyncOperation.getWorkspaceId(), ctx)) {
        LOGGER.warn(
            "Skipping standard sync operation " + standardSyncOperation.getOperationId() + " because the specified workspace "
                + standardSyncOperation.getWorkspaceId()
                + " doesn't exist and violates foreign key constraint.");
        continue;
      }
      ctx.insertInto(DSL.table("operation"))
          .set(id, standardSyncOperation.getOperationId())
          .set(workspaceId, standardSyncOperation.getWorkspaceId())
          .set(name, standardSyncOperation.getName())
          .set(operatorType, standardSyncOperation.getOperatorType() == null ? null
              : Enums.toEnum(standardSyncOperation.getOperatorType().value(), OperatorType.class).orElseThrow())
          .set(operatorNormalization, JSONB.valueOf(Jsons.serialize(standardSyncOperation.getOperatorNormalization())))
          .set(operatorDbt, JSONB.valueOf(Jsons.serialize(standardSyncOperation.getOperatorDbt())))
          .set(tombstone, standardSyncOperation.getTombstone() != null && standardSyncOperation.getTombstone())
          .set(createdAt, OffsetDateTime.ofInstant(configWithMetadata.getCreatedAt(), ZoneOffset.UTC))
          .set(updatedAt, OffsetDateTime.ofInstant(configWithMetadata.getUpdatedAt(), ZoneOffset.UTC))
          .execute();
      standardSyncOperationRecords++;
    }

    LOGGER.info("operation table populated with " + standardSyncOperationRecords + " records");
  }

  private static void createConnectionOperation(final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<UUID> connectionId = DSL.field("connection_id", SQLDataType.UUID.nullable(false));
    final Field<UUID> operationId = DSL.field("operation_id", SQLDataType.UUID.nullable(false));
    final Field<OffsetDateTime> createdAt =
        DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> updatedAt =
        DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));

    ctx.createTableIfNotExists("connection_operation")
        .columns(id,
            connectionId,
            operationId,
            createdAt,
            updatedAt)
        .constraints(primaryKey(id, connectionId, operationId),
            foreignKey(connectionId).references("connection", "id").onDeleteCascade(),
            foreignKey(operationId).references("operation", "id").onDeleteCascade())
        .execute();
    LOGGER.info("connection_operation table created");
  }

  private static void createAndPopulateConnection(final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<NamespaceDefinitionType> namespaceDefinition = DSL
        .field("namespace_definition", SQLDataType.VARCHAR.asEnumDataType(NamespaceDefinitionType.class).nullable(false));
    final Field<String> namespaceFormat = DSL.field("namespace_format", SQLDataType.VARCHAR(256).nullable(true));
    final Field<String> prefix = DSL.field("prefix", SQLDataType.VARCHAR(256).nullable(true));
    final Field<UUID> sourceId = DSL.field("source_id", SQLDataType.UUID.nullable(false));
    final Field<UUID> destinationId = DSL.field("destination_id", SQLDataType.UUID.nullable(false));
    final Field<String> name = DSL.field("name", SQLDataType.VARCHAR(256).nullable(false));
    final Field<JSONB> catalog = DSL.field("catalog", SQLDataType.JSONB.nullable(false));
    final Field<StatusType> status = DSL.field("status", SQLDataType.VARCHAR.asEnumDataType(StatusType.class).nullable(true));
    final Field<JSONB> schedule = DSL.field("schedule", SQLDataType.JSONB.nullable(true));
    final Field<Boolean> manual = DSL.field("manual", SQLDataType.BOOLEAN.nullable(false));
    final Field<JSONB> resourceRequirements = DSL.field("resource_requirements", SQLDataType.JSONB.nullable(true));
    final Field<OffsetDateTime> createdAt =
        DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> updatedAt =
        DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));

    ctx.createTableIfNotExists("connection")
        .columns(id,
            namespaceDefinition,
            namespaceFormat,
            prefix,
            sourceId,
            destinationId,
            name,
            catalog,
            status,
            schedule,
            manual,
            resourceRequirements,
            createdAt,
            updatedAt)
        .constraints(primaryKey(id),
            foreignKey(sourceId).references("actor", "id").onDeleteCascade(),
            foreignKey(destinationId).references("actor", "id").onDeleteCascade())
        .execute();
    ctx.createIndex("connection_source_id_idx").on("connection", "source_id").execute();
    ctx.createIndex("connection_destination_id_idx").on("connection", "destination_id").execute();

    LOGGER.info("connection table created");
    createConnectionOperation(ctx);

    final List<ConfigWithMetadata<StandardSync>> configsWithMetadata = listConfigsWithMetadata(
        ConfigSchema.STANDARD_SYNC,
        StandardSync.class,
        ctx);
    long standardSyncRecords = 0L;
    for (final ConfigWithMetadata<StandardSync> configWithMetadata : configsWithMetadata) {
      final StandardSync standardSync = configWithMetadata.getConfig();
      if (actorDoesNotExist(standardSync.getSourceId(), ctx)) {
        LOGGER.warn(
            "Skipping standard sync " + standardSync.getConnectionId() + " because the specified source " + standardSync.getSourceId()
                + " doesn't exist and violates foreign key constraint.");
        continue;
      } else if (actorDoesNotExist(standardSync.getDestinationId(), ctx)) {
        LOGGER.warn(
            "Skipping standard sync " + standardSync.getConnectionId() + " because the specified destination " + standardSync.getDestinationId()
                + " doesn't exist and violates foreign key constraint.");
        continue;
      }
      ctx.insertInto(DSL.table("connection"))
          .set(id, standardSync.getConnectionId())
          .set(namespaceDefinition, standardSync.getNamespaceDefinition() == null ? null
              : Enums.toEnum(standardSync.getNamespaceDefinition().value(), NamespaceDefinitionType.class).orElseThrow())
          .set(namespaceFormat, standardSync.getNamespaceFormat())
          .set(prefix, standardSync.getPrefix())
          .set(sourceId, standardSync.getSourceId())
          .set(destinationId, standardSync.getDestinationId())
          .set(name, standardSync.getName())
          .set(catalog, JSONB.valueOf(Jsons.serialize(standardSync.getCatalog())))
          .set(status, standardSync.getStatus() == null ? null : Enums.toEnum(standardSync.getStatus().value(), StatusType.class).orElseThrow())
          .set(schedule, JSONB.valueOf(Jsons.serialize(standardSync.getSchedule())))
          .set(manual, standardSync.getManual())
          .set(resourceRequirements, JSONB.valueOf(Jsons.serialize(standardSync.getResourceRequirements())))
          .set(createdAt, OffsetDateTime.ofInstant(configWithMetadata.getCreatedAt(), ZoneOffset.UTC))
          .set(updatedAt, OffsetDateTime.ofInstant(configWithMetadata.getUpdatedAt(), ZoneOffset.UTC))
          .execute();
      standardSyncRecords++;
      populateConnectionOperation(ctx, configWithMetadata);
    }

    LOGGER.info("connection table populated with " + standardSyncRecords + " records");
  }

  private static void createAndPopulateState(final DSLContext ctx) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<UUID> connectionId = DSL.field("connection_id", SQLDataType.UUID.nullable(false));
    final Field<JSONB> state = DSL.field("state", SQLDataType.JSONB.nullable(true));
    final Field<OffsetDateTime> createdAt =
        DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> updatedAt =
        DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));

    ctx.createTableIfNotExists("state")
        .columns(id,
            connectionId,
            state,
            createdAt,
            updatedAt)
        .constraints(primaryKey(id, connectionId),
            foreignKey(connectionId).references("connection", "id").onDeleteCascade())
        .execute();

    LOGGER.info("state table created");

    final List<ConfigWithMetadata<StandardSyncState>> configsWithMetadata = listConfigsWithMetadata(
        ConfigSchema.STANDARD_SYNC_STATE,
        StandardSyncState.class,
        ctx);
    long standardSyncStateRecords = 0L;
    for (final ConfigWithMetadata<StandardSyncState> configWithMetadata : configsWithMetadata) {
      final StandardSyncState standardSyncState = configWithMetadata.getConfig();
      if (connectionDoesNotExist(standardSyncState.getConnectionId(), ctx)) {
        LOGGER.warn(
            "Skipping standard sync state because the specified standard sync " + standardSyncState.getConnectionId()
                + " doesn't exist and violates foreign key constraint.");
        continue;
      }
      ctx.insertInto(DSL.table("state"))
          .set(id, UUID.randomUUID())
          .set(connectionId, standardSyncState.getConnectionId())
          .set(state, JSONB.valueOf(Jsons.serialize(standardSyncState.getState())))
          .set(createdAt, OffsetDateTime.ofInstant(configWithMetadata.getCreatedAt(), ZoneOffset.UTC))
          .set(updatedAt, OffsetDateTime.ofInstant(configWithMetadata.getUpdatedAt(), ZoneOffset.UTC))
          .execute();
      standardSyncStateRecords++;
    }

    LOGGER.info("state table populated with " + standardSyncStateRecords + " records");
  }

  private static void populateConnectionOperation(final DSLContext ctx,
                                                  final ConfigWithMetadata<StandardSync> standardSyncWithMetadata) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<UUID> connectionId = DSL.field("connection_id", SQLDataType.UUID.nullable(false));
    final Field<UUID> operationId = DSL.field("operation_id", SQLDataType.UUID.nullable(false));
    final Field<OffsetDateTime> createdAt =
        DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> updatedAt =
        DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));

    final StandardSync standardSync = standardSyncWithMetadata.getConfig();

    if (connectionDoesNotExist(standardSync.getConnectionId(), ctx)) {
      LOGGER.warn(
          "Skipping connection_operations because the specified standard sync " + standardSync.getConnectionId()
              + " doesn't exist and violates foreign key constraint.");
      return;
    }
    long connectionOperationRecords = 0L;
    for (final UUID operationIdFromStandardSync : standardSync.getOperationIds()) {
      if (operationDoesNotExist(operationIdFromStandardSync, ctx)) {
        LOGGER.warn(
            "Skipping connection_operations because the specified standard sync operation " + operationIdFromStandardSync
                + " doesn't exist and violates foreign key constraint.");
        continue;
      }
      ctx.insertInto(DSL.table("connection_operation"))
          .set(id, UUID.randomUUID())
          .set(connectionId, standardSync.getConnectionId())
          .set(operationId, operationIdFromStandardSync)
          .set(createdAt, OffsetDateTime.ofInstant(standardSyncWithMetadata.getCreatedAt(), ZoneOffset.UTC))
          .set(updatedAt, OffsetDateTime.ofInstant(standardSyncWithMetadata.getUpdatedAt(), ZoneOffset.UTC))
          .execute();
      connectionOperationRecords++;
    }
    LOGGER.info("connection_operation table populated with " + connectionOperationRecords + " records");
  }

  static <T> List<ConfigWithMetadata<T>> listConfigsWithMetadata(final AirbyteConfig airbyteConfigType,
                                                                 final Class<T> clazz,
                                                                 final DSLContext ctx) {
    final Field<String> configId = DSL.field("config_id", SQLDataType.VARCHAR(36).nullable(false));
    final Field<String> configType = DSL.field("config_type", SQLDataType.VARCHAR(60).nullable(false));
    final Field<OffsetDateTime> createdAt =
        DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<OffsetDateTime> updatedAt =
        DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false).defaultValue(currentOffsetDateTime()));
    final Field<JSONB> configBlob = DSL.field("config_blob", SQLDataType.JSONB.nullable(false));
    final Result<Record> results = ctx.select(asterisk()).from(DSL.table("airbyte_configs")).where(configType.eq(airbyteConfigType.name())).fetch();

    return results.stream().map(record -> new ConfigWithMetadata<>(
        record.get(configId),
        record.get(configType),
        record.get(createdAt).toInstant(),
        record.get(updatedAt).toInstant(),
        Jsons.deserialize(record.get(configBlob).data(), clazz)))
        .collect(Collectors.toList());
  }

  public enum SourceType implements EnumType {

    api("api"),
    file("file"),
    database(JdbcUtils.DATABASE_KEY),
    custom("custom");

    private final String literal;

    SourceType(final String literal) {
      this.literal = literal;
    }

    @Override
    public Catalog getCatalog() {
      return getSchema() == null ? null : getSchema().getCatalog();
    }

    @Override
    public Schema getSchema() {
      return new SchemaImpl(DSL.name("public"), null);

    }

    @Override
    public String getName() {
      return "source_type";
    }

    @Override
    public String getLiteral() {
      return literal;
    }

  }

  public enum NamespaceDefinitionType implements EnumType {

    source("source"),
    destination("destination"),
    customformat("customformat");

    private final String literal;

    NamespaceDefinitionType(final String literal) {
      this.literal = literal;
    }

    @Override
    public Catalog getCatalog() {
      return getSchema() == null ? null : getSchema().getCatalog();
    }

    @Override
    public Schema getSchema() {
      return new SchemaImpl(DSL.name("public"), null);
    }

    @Override
    public String getName() {
      return "namespace_definition_type";
    }

    @Override
    public String getLiteral() {
      return literal;
    }

  }

  public enum StatusType implements EnumType {

    active("active"),
    inactive("inactive"),
    deprecated("deprecated");

    private final String literal;

    StatusType(final String literal) {
      this.literal = literal;
    }

    @Override
    public Catalog getCatalog() {
      return getSchema() == null ? null : getSchema().getCatalog();
    }

    @Override
    public Schema getSchema() {
      return new SchemaImpl(DSL.name("public"), null);
    }

    @Override
    public String getName() {
      return "status_type";
    }

    @Override
    public String getLiteral() {
      return literal;
    }

  }

  public enum OperatorType implements EnumType {

    normalization("normalization"),
    dbt("dbt");

    private final String literal;

    OperatorType(final String literal) {
      this.literal = literal;
    }

    @Override
    public Catalog getCatalog() {
      return getSchema() == null ? null : getSchema().getCatalog();
    }

    @Override
    public Schema getSchema() {
      return new SchemaImpl(DSL.name("public"), null);
    }

    @Override
    public String getName() {
      return "operator_type";
    }

    @Override
    public String getLiteral() {
      return literal;
    }

  }

  public enum ActorType implements EnumType {

    source("source"),
    destination("destination");

    private final String literal;

    ActorType(final String literal) {
      this.literal = literal;
    }

    @Override
    public Catalog getCatalog() {
      return getSchema() == null ? null : getSchema().getCatalog();
    }

    @Override
    public Schema getSchema() {
      return new SchemaImpl(DSL.name("public"), null);
    }

    @Override
    public String getName() {
      return "actor_type";
    }

    @Override
    public String getLiteral() {
      return literal;
    }

  }

}
