/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.table;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.Notification;
import io.airbyte.config.Notification.NotificationType;
import io.airbyte.config.OperatorDbt;
import io.airbyte.config.OperatorNormalization;
import io.airbyte.config.OperatorNormalization.Option;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.Schedule;
import io.airbyte.config.Schedule.TimeUnit;
import io.airbyte.config.SlackNotificationConfiguration;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSourceDefinition.SourceType;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOperation.OperatorType;
import io.airbyte.config.StandardSyncState;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AuthSpecification;
import io.airbyte.protocol.models.AuthSpecification.AuthType;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
import java.net.URI;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import javax.annotation.Nullable;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.JSONB;
import org.jooq.Record;
import org.jooq.Table;

public class SetupForNormalizedTablesTest {

  private static final UUID WORKSPACE_ID = UUID.randomUUID();
  private static final UUID WORKSPACE_CUSTOMER_ID = UUID.randomUUID();
  private static final UUID SOURCE_DEFINITION_ID_1 = UUID.randomUUID();
  private static final UUID SOURCE_DEFINITION_ID_2 = UUID.randomUUID();
  private static final UUID DESTINATION_DEFINITION_ID_1 = UUID.randomUUID();
  private static final UUID DESTINATION_DEFINITION_ID_2 = UUID.randomUUID();
  private static final UUID SOURCE_ID_1 = UUID.randomUUID();
  private static final UUID SOURCE_ID_2 = UUID.randomUUID();
  private static final UUID DESTINATION_ID_1 = UUID.randomUUID();
  private static final UUID DESTINATION_ID_2 = UUID.randomUUID();
  private static final UUID OPERATION_ID_1 = UUID.randomUUID();
  private static final UUID OPERATION_ID_2 = UUID.randomUUID();
  private static final UUID CONNECTION_ID_1 = UUID.randomUUID();
  private static final UUID CONNECTION_ID_2 = UUID.randomUUID();
  private static final UUID CONNECTION_ID_3 = UUID.randomUUID();
  private static final UUID CONNECTION_ID_4 = UUID.randomUUID();
  private static final UUID SOURCE_OAUTH_PARAMETER_ID_1 = UUID.randomUUID();
  private static final UUID SOURCE_OAUTH_PARAMETER_ID_2 = UUID.randomUUID();
  private static final UUID DESTINATION_OAUTH_PARAMETER_ID_1 = UUID.randomUUID();
  private static final UUID DESTINATION_OAUTH_PARAMETER_ID_2 = UUID.randomUUID();
  private static final Table<Record> AIRBYTE_CONFIGS = table("airbyte_configs");
  private static final Field<String> CONFIG_ID = field("config_id", String.class);
  private static final Field<String> CONFIG_TYPE = field("config_type", String.class);
  private static final Field<JSONB> CONFIG_BLOB = field("config_blob", JSONB.class);
  private static final Field<OffsetDateTime> CREATED_AT = field("created_at", OffsetDateTime.class);
  private static final Field<OffsetDateTime> UPDATED_AT = field("updated_at", OffsetDateTime.class);
  private static final Instant NOW = Instant.parse("2021-12-15T20:30:40.00Z");
  private static final String CONNECTION_SPEC = "'{\"name\":\"John\", \"age\":30, \"car\":null}'";

  public static void setup(final DSLContext context) {
    createConfigInOldTable(context, standardWorkspace(), ConfigSchema.STANDARD_WORKSPACE);

    for (final StandardSourceDefinition standardSourceDefinition : standardSourceDefinitions()) {
      createConfigInOldTable(context, standardSourceDefinition, ConfigSchema.STANDARD_SOURCE_DEFINITION);
    }

    for (final StandardDestinationDefinition standardDestinationDefinition : standardDestinationDefinitions()) {
      createConfigInOldTable(context, standardDestinationDefinition, ConfigSchema.STANDARD_DESTINATION_DEFINITION);
    }

    for (final SourceConnection sourceConnection : sourceConnections()) {
      createConfigInOldTable(context, sourceConnection, ConfigSchema.SOURCE_CONNECTION);
    }

    for (final DestinationConnection destinationConnection : destinationConnections()) {
      createConfigInOldTable(context, destinationConnection, ConfigSchema.DESTINATION_CONNECTION);
    }

    for (final SourceOAuthParameter sourceOAuthParameter : sourceOauthParameters()) {
      createConfigInOldTable(context, sourceOAuthParameter, ConfigSchema.SOURCE_OAUTH_PARAM);
    }

    for (final DestinationOAuthParameter destinationOAuthParameter : destinationOauthParameters()) {
      createConfigInOldTable(context, destinationOAuthParameter, ConfigSchema.DESTINATION_OAUTH_PARAM);
    }

    for (final StandardSyncOperation standardSyncOperation : standardSyncOperations()) {
      createConfigInOldTable(context, standardSyncOperation, ConfigSchema.STANDARD_SYNC_OPERATION);
    }

    for (final StandardSync standardSync : standardSyncs()) {
      createConfigInOldTable(context, standardSync, ConfigSchema.STANDARD_SYNC);
    }
    for (final StandardSyncState standardSyncState : standardSyncStates()) {
      createConfigInOldTable(context, standardSyncState, ConfigSchema.STANDARD_SYNC_STATE);
    }
  }

  private static <T> void createConfigInOldTable(final DSLContext context, final T config, final AirbyteConfig configType) {
    insertConfigRecord(
        context,
        configType.name(),
        Jsons.jsonNode(config),
        configType.getIdFieldName());
  }

  private static void insertConfigRecord(
                                         final DSLContext context,
                                         final String configType,
                                         final JsonNode configJson,
                                         @Nullable final String idFieldName) {
    final String configId = idFieldName == null ? UUID.randomUUID().toString() : configJson.get(idFieldName).asText();
    context.insertInto(AIRBYTE_CONFIGS)
        .set(CONFIG_ID, configId)
        .set(CONFIG_TYPE, configType)
        .set(CONFIG_BLOB, JSONB.valueOf(Jsons.serialize(configJson)))
        .set(CREATED_AT, OffsetDateTime.ofInstant(NOW, ZoneOffset.UTC))
        .set(UPDATED_AT, OffsetDateTime.ofInstant(NOW, ZoneOffset.UTC))
        .onConflict(CONFIG_TYPE, CONFIG_ID)
        .doNothing()
        .execute();
  }

  public static StandardWorkspace standardWorkspace() {
    final Notification notification = new Notification()
        .withNotificationType(NotificationType.SLACK)
        .withSendOnFailure(true)
        .withSendOnSuccess(true)
        .withSlackConfiguration(new SlackNotificationConfiguration().withWebhook("webhook-url"));
    return new StandardWorkspace()
        .withWorkspaceId(WORKSPACE_ID)
        .withCustomerId(WORKSPACE_CUSTOMER_ID)
        .withName("test-workspace")
        .withSlug("random-string")
        .withEmail("abc@xyz.com")
        .withInitialSetupComplete(true)
        .withAnonymousDataCollection(true)
        .withNews(true)
        .withSecurityUpdates(true)
        .withDisplaySetupWizard(true)
        .withTombstone(false)
        .withNotifications(Collections.singletonList(notification))
        .withFirstCompletedSync(true)
        .withFeedbackDone(true);
  }

  public static List<StandardSourceDefinition> standardSourceDefinitions() {
    final ConnectorSpecification connectorSpecification = connectorSpecification();
    final StandardSourceDefinition standardSourceDefinition1 = new StandardSourceDefinition()
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_1)
        .withSourceType(SourceType.API)
        .withName("random-source-1")
        .withDockerImageTag("tag-1")
        .withDockerRepository("repository-1")
        .withDocumentationUrl("documentation-url-1")
        .withIcon("icon-1")
        .withSpec(connectorSpecification);
    final StandardSourceDefinition standardSourceDefinition2 = new StandardSourceDefinition()
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_2)
        .withSourceType(SourceType.DATABASE)
        .withName("random-source-2")
        .withDockerImageTag("tag-2")
        .withDockerRepository("repository-2")
        .withDocumentationUrl("documentation-url-2")
        .withIcon("icon-2");
    return Arrays.asList(standardSourceDefinition1, standardSourceDefinition2);
  }

  private static ConnectorSpecification connectorSpecification() {
    return new ConnectorSpecification()
        .withAuthSpecification(new AuthSpecification().withAuthType(AuthType.OAUTH_2_0))
        .withConnectionSpecification(Jsons.jsonNode(CONNECTION_SPEC))
        .withDocumentationUrl(URI.create("whatever"))
        .withAdvancedAuth(null)
        .withChangelogUrl(URI.create("whatever"))
        .withSupportedDestinationSyncModes(Arrays.asList(DestinationSyncMode.APPEND, DestinationSyncMode.OVERWRITE, DestinationSyncMode.APPEND_DEDUP))
        .withSupportsDBT(true)
        .withSupportsIncremental(true)
        .withSupportsNormalization(true);
  }

  public static List<StandardDestinationDefinition> standardDestinationDefinitions() {
    final ConnectorSpecification connectorSpecification = connectorSpecification();
    final StandardDestinationDefinition standardDestinationDefinition1 = new StandardDestinationDefinition()
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_1)
        .withName("random-destination-1")
        .withDockerImageTag("tag-3")
        .withDockerRepository("repository-3")
        .withDocumentationUrl("documentation-url-3")
        .withIcon("icon-3")
        .withSpec(connectorSpecification);
    final StandardDestinationDefinition standardDestinationDefinition2 = new StandardDestinationDefinition()
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_2)
        .withName("random-destination-2")
        .withDockerImageTag("tag-4")
        .withDockerRepository("repository-4")
        .withDocumentationUrl("documentation-url-4")
        .withIcon("icon-4")
        .withSpec(connectorSpecification);
    return Arrays.asList(standardDestinationDefinition1, standardDestinationDefinition2);
  }

  public static List<SourceConnection> sourceConnections() {
    final SourceConnection sourceConnection1 = new SourceConnection()
        .withName("source-1")
        .withTombstone(false)
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_1)
        .withWorkspaceId(WORKSPACE_ID)
        .withConfiguration(Jsons.jsonNode(CONNECTION_SPEC))
        .withSourceId(SOURCE_ID_1);
    final SourceConnection sourceConnection2 = new SourceConnection()
        .withName("source-2")
        .withTombstone(false)
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_2)
        .withWorkspaceId(WORKSPACE_ID)
        .withConfiguration(Jsons.jsonNode(CONNECTION_SPEC))
        .withSourceId(SOURCE_ID_2);
    return Arrays.asList(sourceConnection1, sourceConnection2);
  }

  public static List<DestinationConnection> destinationConnections() {
    final DestinationConnection destinationConnection1 = new DestinationConnection()
        .withName("destination-1")
        .withTombstone(false)
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_1)
        .withWorkspaceId(WORKSPACE_ID)
        .withConfiguration(Jsons.jsonNode(CONNECTION_SPEC))
        .withDestinationId(DESTINATION_ID_1);
    final DestinationConnection destinationConnection2 = new DestinationConnection()
        .withName("destination-2")
        .withTombstone(false)
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_2)
        .withWorkspaceId(WORKSPACE_ID)
        .withConfiguration(Jsons.jsonNode(CONNECTION_SPEC))
        .withDestinationId(DESTINATION_ID_2);
    return Arrays.asList(destinationConnection1, destinationConnection2);
  }

  public static List<SourceOAuthParameter> sourceOauthParameters() {
    final SourceOAuthParameter sourceOAuthParameter1 = new SourceOAuthParameter()
        .withConfiguration(Jsons.jsonNode(CONNECTION_SPEC))
        .withWorkspaceId(null)
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_1)
        .withOauthParameterId(SOURCE_OAUTH_PARAMETER_ID_1);
    final SourceOAuthParameter sourceOAuthParameter2 = new SourceOAuthParameter()
        .withConfiguration(Jsons.jsonNode(CONNECTION_SPEC))
        .withWorkspaceId(WORKSPACE_ID)
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_2)
        .withOauthParameterId(SOURCE_OAUTH_PARAMETER_ID_2);
    return Arrays.asList(sourceOAuthParameter1, sourceOAuthParameter2);
  }

  public static List<DestinationOAuthParameter> destinationOauthParameters() {
    final DestinationOAuthParameter destinationOAuthParameter1 = new DestinationOAuthParameter()
        .withConfiguration(Jsons.jsonNode(CONNECTION_SPEC))
        .withWorkspaceId(null)
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_1)
        .withOauthParameterId(DESTINATION_OAUTH_PARAMETER_ID_1);
    final DestinationOAuthParameter destinationOAuthParameter2 = new DestinationOAuthParameter()
        .withConfiguration(Jsons.jsonNode(CONNECTION_SPEC))
        .withWorkspaceId(WORKSPACE_ID)
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_2)
        .withOauthParameterId(DESTINATION_OAUTH_PARAMETER_ID_2);
    return Arrays.asList(destinationOAuthParameter1, destinationOAuthParameter2);
  }

  public static List<StandardSyncOperation> standardSyncOperations() {
    final OperatorDbt operatorDbt = new OperatorDbt()
        .withDbtArguments("dbt-arguments")
        .withDockerImage("image-tag")
        .withGitRepoBranch("git-repo-branch")
        .withGitRepoUrl("git-repo-url");
    final StandardSyncOperation standardSyncOperation1 = new StandardSyncOperation()
        .withName("operation-1")
        .withTombstone(false)
        .withOperationId(OPERATION_ID_1)
        .withWorkspaceId(WORKSPACE_ID)
        .withOperatorDbt(operatorDbt)
        .withOperatorNormalization(null)
        .withOperatorType(OperatorType.DBT);
    final StandardSyncOperation standardSyncOperation2 = new StandardSyncOperation()
        .withName("operation-1")
        .withTombstone(false)
        .withOperationId(OPERATION_ID_2)
        .withWorkspaceId(WORKSPACE_ID)
        .withOperatorDbt(null)
        .withOperatorNormalization(new OperatorNormalization().withOption(Option.BASIC))
        .withOperatorType(OperatorType.NORMALIZATION);
    return Arrays.asList(standardSyncOperation1, standardSyncOperation2);
  }

  public static List<StandardSync> standardSyncs() {
    final ResourceRequirements resourceRequirements = new ResourceRequirements()
        .withCpuRequest("1")
        .withCpuLimit("1")
        .withMemoryRequest("1")
        .withMemoryLimit("1");
    final Schedule schedule = new Schedule().withTimeUnit(TimeUnit.DAYS).withUnits(1L);
    final StandardSync standardSync1 = new StandardSync()
        .withOperationIds(Arrays.asList(OPERATION_ID_1, OPERATION_ID_2))
        .withConnectionId(CONNECTION_ID_1)
        .withSourceId(SOURCE_ID_1)
        .withDestinationId(DESTINATION_ID_1)
        .withCatalog(getConfiguredCatalog())
        .withName("standard-sync-1")
        .withManual(true)
        .withNamespaceDefinition(NamespaceDefinitionType.CUSTOMFORMAT)
        .withNamespaceFormat("")
        .withPrefix("")
        .withResourceRequirements(resourceRequirements)
        .withStatus(Status.ACTIVE)
        .withSchedule(schedule);

    final StandardSync standardSync2 = new StandardSync()
        .withOperationIds(Arrays.asList(OPERATION_ID_1, OPERATION_ID_2))
        .withConnectionId(CONNECTION_ID_2)
        .withSourceId(SOURCE_ID_1)
        .withDestinationId(DESTINATION_ID_2)
        .withCatalog(getConfiguredCatalog())
        .withName("standard-sync-2")
        .withManual(true)
        .withNamespaceDefinition(NamespaceDefinitionType.SOURCE)
        .withNamespaceFormat("")
        .withPrefix("")
        .withResourceRequirements(resourceRequirements)
        .withStatus(Status.ACTIVE)
        .withSchedule(schedule);

    final StandardSync standardSync3 = new StandardSync()
        .withOperationIds(Arrays.asList(OPERATION_ID_1, OPERATION_ID_2))
        .withConnectionId(CONNECTION_ID_3)
        .withSourceId(SOURCE_ID_2)
        .withDestinationId(DESTINATION_ID_1)
        .withCatalog(getConfiguredCatalog())
        .withName("standard-sync-3")
        .withManual(true)
        .withNamespaceDefinition(NamespaceDefinitionType.DESTINATION)
        .withNamespaceFormat("")
        .withPrefix("")
        .withResourceRequirements(resourceRequirements)
        .withStatus(Status.ACTIVE)
        .withSchedule(schedule);

    final StandardSync standardSync4 = new StandardSync()
        .withOperationIds(Arrays.asList(OPERATION_ID_1, OPERATION_ID_2))
        .withConnectionId(CONNECTION_ID_4)
        .withSourceId(SOURCE_ID_2)
        .withDestinationId(DESTINATION_ID_2)
        .withCatalog(getConfiguredCatalog())
        .withName("standard-sync-4")
        .withManual(true)
        .withNamespaceDefinition(NamespaceDefinitionType.CUSTOMFORMAT)
        .withNamespaceFormat("")
        .withPrefix("")
        .withResourceRequirements(resourceRequirements)
        .withStatus(Status.INACTIVE)
        .withSchedule(schedule);

    return Arrays.asList(standardSync1, standardSync2, standardSync3, standardSync4);
  }

  private static ConfiguredAirbyteCatalog getConfiguredCatalog() {
    final AirbyteCatalog catalog = new AirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createAirbyteStream(
            "models",
            "models_schema",
            io.airbyte.protocol.models.Field.of("id", JsonSchemaType.NUMBER),
            io.airbyte.protocol.models.Field.of("make_id", JsonSchemaType.NUMBER),
            io.airbyte.protocol.models.Field.of("model", JsonSchemaType.STRING))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of("id")))));
    return CatalogHelpers.toDefaultConfiguredCatalog(catalog);
  }

  public static List<StandardSyncState> standardSyncStates() {
    final StandardSyncState standardSyncState1 = new StandardSyncState()
        .withConnectionId(CONNECTION_ID_1)
        .withState(new State().withState(Jsons.jsonNode(CONNECTION_SPEC)));
    final StandardSyncState standardSyncState2 = new StandardSyncState()
        .withConnectionId(CONNECTION_ID_2)
        .withState(new State().withState(Jsons.jsonNode(CONNECTION_SPEC)));
    final StandardSyncState standardSyncState3 = new StandardSyncState()
        .withConnectionId(CONNECTION_ID_3)
        .withState(new State().withState(Jsons.jsonNode(CONNECTION_SPEC)));
    final StandardSyncState standardSyncState4 = new StandardSyncState()
        .withConnectionId(CONNECTION_ID_4)
        .withState(new State().withState(Jsons.jsonNode(CONNECTION_SPEC)));
    return Arrays.asList(standardSyncState1, standardSyncState2, standardSyncState3, standardSyncState4);
  }

  public static Instant now() {
    return NOW;
  }

}
