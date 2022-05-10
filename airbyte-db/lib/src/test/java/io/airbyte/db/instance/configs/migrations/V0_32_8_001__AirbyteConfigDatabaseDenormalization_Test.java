/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import static io.airbyte.db.instance.configs.migrations.SetupForNormalizedTablesTest.destinationConnections;
import static io.airbyte.db.instance.configs.migrations.SetupForNormalizedTablesTest.destinationOauthParameters;
import static io.airbyte.db.instance.configs.migrations.SetupForNormalizedTablesTest.now;
import static io.airbyte.db.instance.configs.migrations.SetupForNormalizedTablesTest.sourceConnections;
import static io.airbyte.db.instance.configs.migrations.SetupForNormalizedTablesTest.sourceOauthParameters;
import static io.airbyte.db.instance.configs.migrations.SetupForNormalizedTablesTest.standardDestinationDefinitions;
import static io.airbyte.db.instance.configs.migrations.SetupForNormalizedTablesTest.standardSourceDefinitions;
import static io.airbyte.db.instance.configs.migrations.SetupForNormalizedTablesTest.standardSyncOperations;
import static io.airbyte.db.instance.configs.migrations.SetupForNormalizedTablesTest.standardSyncStates;
import static io.airbyte.db.instance.configs.migrations.SetupForNormalizedTablesTest.standardSyncs;
import static io.airbyte.db.instance.configs.migrations.SetupForNormalizedTablesTest.standardWorkspace;
import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.table;

import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.Notification;
import io.airbyte.config.OperatorDbt;
import io.airbyte.config.OperatorNormalization;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.Schedule;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncState;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.State;
import io.airbyte.db.instance.configs.AbstractConfigsDatabaseTest;
import io.airbyte.db.instance.configs.migrations.V0_32_8_001__AirbyteConfigDatabaseDenormalization.ActorType;
import io.airbyte.db.instance.configs.migrations.V0_32_8_001__AirbyteConfigDatabaseDenormalization.NamespaceDefinitionType;
import io.airbyte.db.instance.configs.migrations.V0_32_8_001__AirbyteConfigDatabaseDenormalization.OperatorType;
import io.airbyte.db.instance.configs.migrations.V0_32_8_001__AirbyteConfigDatabaseDenormalization.SourceType;
import io.airbyte.db.instance.configs.migrations.V0_32_8_001__AirbyteConfigDatabaseDenormalization.StatusType;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.ArrayList;
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

public class V0_32_8_001__AirbyteConfigDatabaseDenormalization_Test extends AbstractConfigsDatabaseTest {

  @Test
  public void testCompleteMigration() throws IOException, SQLException {
    final DSLContext context = getDslContext();
    SetupForNormalizedTablesTest.setup(context);

    V0_32_8_001__AirbyteConfigDatabaseDenormalization.migrate(context);

    assertDataForWorkspace(context);
    assertDataForSourceDefinition(context);
    assertDataForDestinationDefinition(context);
    assertDataForSourceConnection(context);
    assertDataForDestinationConnection(context);
    assertDataForSourceOauthParams(context);
    assertDataForDestinationOauthParams(context);
    assertDataForOperations(context);
    assertDataForConnections(context);
    assertDataForStandardSyncStates(context);
  }

  private void assertDataForWorkspace(final DSLContext context) {
    final Result<Record> workspaces = context.select(asterisk())
        .from(table("workspace"))
        .fetch();
    Assertions.assertEquals(1, workspaces.size());

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
    final Field<Boolean> tombstone = DSL.field("tombstone", SQLDataType.BOOLEAN.nullable(true));
    final Field<JSONB> notifications = DSL.field("notifications", SQLDataType.JSONB.nullable(true));
    final Field<Boolean> firstSyncComplete = DSL.field("first_sync_complete", SQLDataType.BOOLEAN.nullable(true));
    final Field<Boolean> feedbackComplete = DSL.field("feedback_complete", SQLDataType.BOOLEAN.nullable(true));
    final Field<OffsetDateTime> createdAt = DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));
    final Field<OffsetDateTime> updatedAt = DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));

    final Record workspace = workspaces.get(0);

    final List<Notification> notificationList = new ArrayList<>();
    final List fetchedNotifications = Jsons.deserialize(workspace.get(notifications).data(), List.class);
    for (final Object notification : fetchedNotifications) {
      notificationList.add(Jsons.convertValue(notification, Notification.class));
    }
    final StandardWorkspace workspaceFromNewTable = new StandardWorkspace()
        .withWorkspaceId(workspace.get(id))
        .withName(workspace.get(name))
        .withSlug(workspace.get(slug))
        .withInitialSetupComplete(workspace.get(initialSetupComplete))
        .withCustomerId(workspace.get(customerId))
        .withEmail(workspace.get(email))
        .withAnonymousDataCollection(workspace.get(anonymousDataCollection))
        .withNews(workspace.get(sendNewsletter))
        .withSecurityUpdates(workspace.get(sendSecurityUpdates))
        .withDisplaySetupWizard(workspace.get(displaySetupWizard))
        .withTombstone(workspace.get(tombstone))
        .withNotifications(notificationList)
        .withFirstCompletedSync(workspace.get(firstSyncComplete))
        .withFeedbackDone(workspace.get(feedbackComplete));
    Assertions.assertEquals(standardWorkspace(), workspaceFromNewTable);
    Assertions.assertEquals(now(), workspace.get(createdAt).toInstant());
    Assertions.assertEquals(now(), workspace.get(updatedAt).toInstant());
    Assertions.assertFalse(V0_32_8_001__AirbyteConfigDatabaseDenormalization.workspaceDoesNotExist(standardWorkspace().getWorkspaceId(), context));
    Assertions.assertTrue(V0_32_8_001__AirbyteConfigDatabaseDenormalization.workspaceDoesNotExist(UUID.randomUUID(), context));
  }

  private void assertDataForSourceDefinition(final DSLContext context) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<String> name = DSL.field("name", SQLDataType.VARCHAR(256).nullable(false));
    final Field<String> dockerRepository = DSL.field("docker_repository", SQLDataType.VARCHAR(256).nullable(false));
    final Field<String> dockerImageTag = DSL.field("docker_image_tag", SQLDataType.VARCHAR(256).nullable(false));
    final Field<String> documentationUrl = DSL.field("documentation_url", SQLDataType.VARCHAR(256).nullable(false));
    final Field<JSONB> spec = DSL.field("spec", SQLDataType.JSONB.nullable(false));
    final Field<String> icon = DSL.field("icon", SQLDataType.VARCHAR(256).nullable(true));
    final Field<ActorType> actorType = DSL.field("actor_type", SQLDataType.VARCHAR.asEnumDataType(ActorType.class).nullable(false));
    final Field<SourceType> sourceType = DSL.field("source_type", SQLDataType.VARCHAR.asEnumDataType(SourceType.class).nullable(true));
    final Field<OffsetDateTime> createdAt = DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));
    final Field<OffsetDateTime> updatedAt = DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));

    final Result<Record> sourceDefinitions = context.select(asterisk())
        .from(table("actor_definition"))
        .where(actorType.eq(ActorType.source))
        .fetch();
    final List<StandardSourceDefinition> expectedDefinitions = standardSourceDefinitions();
    Assertions.assertEquals(expectedDefinitions.size(), sourceDefinitions.size());
    Assertions.assertTrue(V0_32_8_001__AirbyteConfigDatabaseDenormalization.actorDefinitionDoesNotExist(UUID.randomUUID(), context));
    for (final Record sourceDefinition : sourceDefinitions) {
      final StandardSourceDefinition standardSourceDefinition = new StandardSourceDefinition()
          .withSourceDefinitionId(sourceDefinition.get(id))
          .withDockerImageTag(sourceDefinition.get(dockerImageTag))
          .withIcon(sourceDefinition.get(icon))
          .withDockerRepository(sourceDefinition.get(dockerRepository))
          .withDocumentationUrl(sourceDefinition.get(documentationUrl))
          .withName(sourceDefinition.get(name))
          .withSourceType(Enums.toEnum(sourceDefinition.get(sourceType, String.class), StandardSourceDefinition.SourceType.class).orElseThrow())
          .withSpec(Jsons.deserialize(sourceDefinition.get(spec).data(), ConnectorSpecification.class));
      Assertions.assertTrue(expectedDefinitions.contains(standardSourceDefinition));
      Assertions.assertEquals(now(), sourceDefinition.get(createdAt).toInstant());
      Assertions.assertEquals(now(), sourceDefinition.get(updatedAt).toInstant());
      Assertions.assertFalse(
          V0_32_8_001__AirbyteConfigDatabaseDenormalization.actorDefinitionDoesNotExist(standardSourceDefinition.getSourceDefinitionId(), context));
    }
  }

  private void assertDataForDestinationDefinition(final DSLContext context) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<String> name = DSL.field("name", SQLDataType.VARCHAR(256).nullable(false));
    final Field<String> dockerRepository = DSL.field("docker_repository", SQLDataType.VARCHAR(256).nullable(false));
    final Field<String> dockerImageTag = DSL.field("docker_image_tag", SQLDataType.VARCHAR(256).nullable(false));
    final Field<String> documentationUrl = DSL.field("documentation_url", SQLDataType.VARCHAR(256).nullable(false));
    final Field<JSONB> spec = DSL.field("spec", SQLDataType.JSONB.nullable(false));
    final Field<String> icon = DSL.field("icon", SQLDataType.VARCHAR(256).nullable(true));
    final Field<ActorType> actorType = DSL.field("actor_type", SQLDataType.VARCHAR.asEnumDataType(ActorType.class).nullable(false));
    final Field<SourceType> sourceType = DSL.field("source_type", SQLDataType.VARCHAR.asEnumDataType(SourceType.class).nullable(true));
    final Field<OffsetDateTime> createdAt = DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));
    final Field<OffsetDateTime> updatedAt = DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));

    final Result<Record> destinationDefinitions = context.select(asterisk())
        .from(table("actor_definition"))
        .where(actorType.eq(ActorType.destination))
        .fetch();
    final List<StandardDestinationDefinition> expectedDefinitions = standardDestinationDefinitions();
    Assertions.assertEquals(expectedDefinitions.size(), destinationDefinitions.size());
    Assertions.assertTrue(V0_32_8_001__AirbyteConfigDatabaseDenormalization.actorDefinitionDoesNotExist(UUID.randomUUID(), context));
    for (final Record record : destinationDefinitions) {
      final StandardDestinationDefinition standardDestinationDefinition = new StandardDestinationDefinition()
          .withDestinationDefinitionId(record.get(id))
          .withDockerImageTag(record.get(dockerImageTag))
          .withIcon(record.get(icon))
          .withDockerRepository(record.get(dockerRepository))
          .withDocumentationUrl(record.get(documentationUrl))
          .withName(record.get(name))
          .withSpec(Jsons.deserialize(record.get(spec).data(), ConnectorSpecification.class));
      Assertions.assertTrue(expectedDefinitions.contains(standardDestinationDefinition));
      Assertions.assertNull(record.get(sourceType));
      Assertions.assertEquals(now(), record.get(createdAt).toInstant());
      Assertions.assertEquals(now(), record.get(updatedAt).toInstant());
      Assertions.assertFalse(V0_32_8_001__AirbyteConfigDatabaseDenormalization
          .actorDefinitionDoesNotExist(standardDestinationDefinition.getDestinationDefinitionId(), context));
    }
  }

  private void assertDataForSourceConnection(final DSLContext context) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<String> name = DSL.field("name", SQLDataType.VARCHAR(256).nullable(false));
    final Field<UUID> actorDefinitionId = DSL.field("actor_definition_id", SQLDataType.UUID.nullable(false));
    final Field<UUID> workspaceId = DSL.field("workspace_id", SQLDataType.UUID.nullable(false));
    final Field<JSONB> configuration = DSL.field("configuration", SQLDataType.JSONB.nullable(false));
    final Field<ActorType> actorType = DSL.field("actor_type", SQLDataType.VARCHAR.asEnumDataType(ActorType.class).nullable(false));
    final Field<Boolean> tombstone = DSL.field("tombstone", SQLDataType.BOOLEAN.nullable(false));
    final Field<OffsetDateTime> createdAt = DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));
    final Field<OffsetDateTime> updatedAt = DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));

    final Result<Record> sourceConnections = context.select(asterisk())
        .from(table("actor"))
        .where(actorType.eq(ActorType.source))
        .fetch();
    final List<SourceConnection> expectedDefinitions = sourceConnections();
    Assertions.assertEquals(expectedDefinitions.size(), sourceConnections.size());
    Assertions.assertTrue(V0_32_8_001__AirbyteConfigDatabaseDenormalization.actorDoesNotExist(UUID.randomUUID(), context));
    for (final Record record : sourceConnections) {
      final SourceConnection sourceConnection = new SourceConnection()
          .withSourceId(record.get(id))
          .withConfiguration(Jsons.deserialize(record.get(configuration).data()))
          .withWorkspaceId(record.get(workspaceId))
          .withSourceDefinitionId(record.get(actorDefinitionId))
          .withTombstone(record.get(tombstone))
          .withName(record.get(name));

      Assertions.assertTrue(expectedDefinitions.contains(sourceConnection));
      Assertions.assertEquals(now(), record.get(createdAt).toInstant());
      Assertions.assertEquals(now(), record.get(updatedAt).toInstant());
      Assertions.assertFalse(V0_32_8_001__AirbyteConfigDatabaseDenormalization.actorDoesNotExist(sourceConnection.getSourceId(), context));
    }
  }

  private void assertDataForDestinationConnection(final DSLContext context) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<String> name = DSL.field("name", SQLDataType.VARCHAR(256).nullable(false));
    final Field<UUID> actorDefinitionId = DSL.field("actor_definition_id", SQLDataType.UUID.nullable(false));
    final Field<UUID> workspaceId = DSL.field("workspace_id", SQLDataType.UUID.nullable(false));
    final Field<JSONB> configuration = DSL.field("configuration", SQLDataType.JSONB.nullable(false));
    final Field<ActorType> actorType = DSL.field("actor_type", SQLDataType.VARCHAR.asEnumDataType(ActorType.class).nullable(false));
    final Field<Boolean> tombstone = DSL.field("tombstone", SQLDataType.BOOLEAN.nullable(false));
    final Field<OffsetDateTime> createdAt = DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));
    final Field<OffsetDateTime> updatedAt = DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));

    final Result<Record> destinationConnections = context.select(asterisk())
        .from(table("actor"))
        .where(actorType.eq(ActorType.destination))
        .fetch();
    final List<DestinationConnection> expectedDefinitions = destinationConnections();
    Assertions.assertEquals(expectedDefinitions.size(), destinationConnections.size());
    Assertions.assertTrue(V0_32_8_001__AirbyteConfigDatabaseDenormalization.actorDoesNotExist(UUID.randomUUID(), context));
    for (final Record record : destinationConnections) {
      final DestinationConnection destinationConnection = new DestinationConnection()
          .withDestinationId(record.get(id))
          .withConfiguration(Jsons.deserialize(record.get(configuration).data()))
          .withWorkspaceId(record.get(workspaceId))
          .withDestinationDefinitionId(record.get(actorDefinitionId))
          .withTombstone(record.get(tombstone))
          .withName(record.get(name));

      Assertions.assertTrue(expectedDefinitions.contains(destinationConnection));
      Assertions.assertEquals(now(), record.get(createdAt).toInstant());
      Assertions.assertEquals(now(), record.get(updatedAt).toInstant());
      Assertions.assertFalse(V0_32_8_001__AirbyteConfigDatabaseDenormalization.actorDoesNotExist(destinationConnection.getDestinationId(), context));
    }
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
    final List<SourceOAuthParameter> expectedDefinitions = sourceOauthParameters().stream().filter(c -> c.getWorkspaceId() != null).toList();
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
    final List<DestinationOAuthParameter> expectedDefinitions =
        destinationOauthParameters().stream().filter(c -> c.getWorkspaceId() != null).toList();
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

  private void assertDataForOperations(final DSLContext context) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<UUID> workspaceId = DSL.field("workspace_id", SQLDataType.UUID.nullable(false));
    final Field<String> name = DSL.field("name", SQLDataType.VARCHAR(256).nullable(false));
    final Field<OperatorType> operatorType = DSL.field("operator_type", SQLDataType.VARCHAR.asEnumDataType(OperatorType.class).nullable(false));
    final Field<JSONB> operatorNormalization = DSL.field("operator_normalization", SQLDataType.JSONB.nullable(true));
    final Field<JSONB> operatorDbt = DSL.field("operator_dbt", SQLDataType.JSONB.nullable(true));
    final Field<Boolean> tombstone = DSL.field("tombstone", SQLDataType.BOOLEAN.nullable(true));
    final Field<OffsetDateTime> createdAt = DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));
    final Field<OffsetDateTime> updatedAt = DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));

    final Result<Record> standardSyncOperations = context.select(asterisk())
        .from(table("operation"))
        .fetch();
    final List<StandardSyncOperation> expectedDefinitions = standardSyncOperations();
    Assertions.assertEquals(expectedDefinitions.size(), standardSyncOperations.size());
    Assertions.assertTrue(V0_32_8_001__AirbyteConfigDatabaseDenormalization.operationDoesNotExist(UUID.randomUUID(), context));
    for (final Record record : standardSyncOperations) {
      final StandardSyncOperation standardSyncOperation = new StandardSyncOperation()
          .withOperationId(record.get(id))
          .withName(record.get(name))
          .withWorkspaceId(record.get(workspaceId))
          .withOperatorType(Enums.toEnum(record.get(operatorType, String.class), StandardSyncOperation.OperatorType.class).orElseThrow())
          .withOperatorNormalization(Jsons.deserialize(record.get(operatorNormalization).data(), OperatorNormalization.class))
          .withOperatorDbt(Jsons.deserialize(record.get(operatorDbt).data(), OperatorDbt.class))
          .withTombstone(record.get(tombstone));

      Assertions.assertTrue(expectedDefinitions.contains(standardSyncOperation));
      Assertions.assertEquals(now(), record.get(createdAt).toInstant());
      Assertions.assertEquals(now(), record.get(updatedAt).toInstant());
      Assertions
          .assertFalse(V0_32_8_001__AirbyteConfigDatabaseDenormalization.operationDoesNotExist(standardSyncOperation.getOperationId(), context));
    }
  }

  private void assertDataForConnections(final DSLContext context) {
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
    final Field<OffsetDateTime> createdAt = DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));
    final Field<OffsetDateTime> updatedAt = DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));

    final Result<Record> standardSyncs = context.select(asterisk())
        .from(table("connection"))
        .fetch();
    final List<StandardSync> expectedStandardSyncs = standardSyncs();
    Assertions.assertEquals(expectedStandardSyncs.size(), standardSyncs.size());
    Assertions.assertTrue(V0_32_8_001__AirbyteConfigDatabaseDenormalization.connectionDoesNotExist(UUID.randomUUID(), context));
    for (final Record record : standardSyncs) {
      final StandardSync standardSync = new StandardSync()
          .withConnectionId(record.get(id))
          .withNamespaceDefinition(
              Enums.toEnum(record.get(namespaceDefinition, String.class), io.airbyte.config.JobSyncConfig.NamespaceDefinitionType.class)
                  .orElseThrow())
          .withNamespaceFormat(record.get(namespaceFormat))
          .withPrefix(record.get(prefix))
          .withSourceId(record.get(sourceId))
          .withDestinationId(record.get(destinationId))
          .withName(record.get(name))
          .withCatalog(Jsons.deserialize(record.get(catalog).data(), ConfiguredAirbyteCatalog.class))
          .withStatus(Enums.toEnum(record.get(status, String.class), StandardSync.Status.class).orElseThrow())
          .withSchedule(Jsons.deserialize(record.get(schedule).data(), Schedule.class))
          .withManual(record.get(manual))
          .withOperationIds(connectionOperationIds(record.get(id), context))
          .withResourceRequirements(Jsons.deserialize(record.get(resourceRequirements).data(), ResourceRequirements.class));

      Assertions.assertTrue(expectedStandardSyncs.contains(standardSync));
      Assertions.assertEquals(now(), record.get(createdAt).toInstant());
      Assertions.assertEquals(now(), record.get(updatedAt).toInstant());
      Assertions.assertFalse(V0_32_8_001__AirbyteConfigDatabaseDenormalization.connectionDoesNotExist(standardSync.getConnectionId(), context));
    }
  }

  private List<UUID> connectionOperationIds(final UUID connectionIdTo, final DSLContext context) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<UUID> connectionId = DSL.field("connection_id", SQLDataType.UUID.nullable(false));
    final Field<UUID> operationId = DSL.field("operation_id", SQLDataType.UUID.nullable(false));
    final Field<OffsetDateTime> createdAt = DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));
    final Field<OffsetDateTime> updatedAt = DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));

    final Result<Record> connectionOperations = context.select(asterisk())
        .from(table("connection_operation"))
        .where(connectionId.eq(connectionIdTo))
        .fetch();

    final List<UUID> ids = new ArrayList<>();

    for (final Record record : connectionOperations) {
      ids.add(record.get(operationId));
      Assertions.assertNotNull(record.get(id));
      Assertions.assertEquals(now(), record.get(createdAt).toInstant());
      Assertions.assertEquals(now(), record.get(updatedAt).toInstant());
    }

    return ids;
  }

  private void assertDataForStandardSyncStates(final DSLContext context) {
    final Field<UUID> id = DSL.field("id", SQLDataType.UUID.nullable(false));
    final Field<UUID> connectionId = DSL.field("connection_id", SQLDataType.UUID.nullable(false));
    final Field<JSONB> state = DSL.field("state", SQLDataType.JSONB.nullable(true));
    final Field<OffsetDateTime> createdAt = DSL.field("created_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));
    final Field<OffsetDateTime> updatedAt = DSL.field("updated_at", SQLDataType.TIMESTAMPWITHTIMEZONE.nullable(false));

    final Result<Record> standardSyncStates = context.select(asterisk())
        .from(table("state"))
        .fetch();
    final List<StandardSyncState> expectedStandardSyncsStates = standardSyncStates();
    Assertions.assertEquals(expectedStandardSyncsStates.size(), standardSyncStates.size());

    for (final Record record : standardSyncStates) {
      final StandardSyncState standardSyncState = new StandardSyncState()
          .withConnectionId(record.get(connectionId))
          .withState(Jsons.deserialize(record.get(state).data(), State.class));

      Assertions.assertTrue(expectedStandardSyncsStates.contains(standardSyncState));
      Assertions.assertNotNull(record.get(id));
      Assertions.assertEquals(now(), record.get(createdAt).toInstant());
      Assertions.assertEquals(now(), record.get(updatedAt).toInstant());
    }
  }

}
