/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ActorCatalog;
import io.airbyte.config.ActorCatalogFetchEvent;
import io.airbyte.config.ActorDefinitionResourceRequirements;
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
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

public class MockData {

  private static final UUID WORKSPACE_ID_1 = UUID.randomUUID();
  private static final UUID WORKSPACE_ID_2 = UUID.randomUUID();
  private static final UUID WORKSPACE_ID_3 = UUID.randomUUID();
  private static final UUID WORKSPACE_CUSTOMER_ID = UUID.randomUUID();
  private static final UUID SOURCE_DEFINITION_ID_1 = UUID.randomUUID();
  private static final UUID SOURCE_DEFINITION_ID_2 = UUID.randomUUID();
  private static final UUID SOURCE_DEFINITION_ID_3 = UUID.randomUUID();
  private static final UUID SOURCE_DEFINITION_ID_4 = UUID.randomUUID();
  private static final UUID DESTINATION_DEFINITION_ID_1 = UUID.randomUUID();
  private static final UUID DESTINATION_DEFINITION_ID_2 = UUID.randomUUID();
  private static final UUID DESTINATION_DEFINITION_ID_3 = UUID.randomUUID();
  private static final UUID DESTINATION_DEFINITION_ID_4 = UUID.randomUUID();
  private static final UUID SOURCE_ID_1 = UUID.randomUUID();
  private static final UUID SOURCE_ID_2 = UUID.randomUUID();
  private static final UUID SOURCE_ID_3 = UUID.randomUUID();
  private static final UUID DESTINATION_ID_1 = UUID.randomUUID();
  private static final UUID DESTINATION_ID_2 = UUID.randomUUID();
  private static final UUID DESTINATION_ID_3 = UUID.randomUUID();
  private static final UUID OPERATION_ID_1 = UUID.randomUUID();
  private static final UUID OPERATION_ID_2 = UUID.randomUUID();
  private static final UUID OPERATION_ID_3 = UUID.randomUUID();
  private static final UUID CONNECTION_ID_1 = UUID.randomUUID();
  private static final UUID CONNECTION_ID_2 = UUID.randomUUID();
  private static final UUID CONNECTION_ID_3 = UUID.randomUUID();
  private static final UUID CONNECTION_ID_4 = UUID.randomUUID();
  private static final UUID CONNECTION_ID_5 = UUID.randomUUID();
  private static final UUID SOURCE_OAUTH_PARAMETER_ID_1 = UUID.randomUUID();
  private static final UUID SOURCE_OAUTH_PARAMETER_ID_2 = UUID.randomUUID();
  private static final UUID DESTINATION_OAUTH_PARAMETER_ID_1 = UUID.randomUUID();
  private static final UUID DESTINATION_OAUTH_PARAMETER_ID_2 = UUID.randomUUID();
  private static final UUID ACTOR_CATALOG_ID_1 = UUID.randomUUID();
  private static final UUID ACTOR_CATALOG_ID_2 = UUID.randomUUID();
  private static final UUID ACTOR_CATALOG_ID_3 = UUID.randomUUID();
  private static final UUID ACTOR_CATALOG_FETCH_EVENT_ID_1 = UUID.randomUUID();
  private static final UUID ACTOR_CATALOG_FETCH_EVENT_ID_2 = UUID.randomUUID();

  private static final Instant NOW = Instant.parse("2021-12-15T20:30:40.00Z");

  public static List<StandardWorkspace> standardWorkspaces() {
    final Notification notification = new Notification()
        .withNotificationType(NotificationType.SLACK)
        .withSendOnFailure(true)
        .withSendOnSuccess(true)
        .withSlackConfiguration(new SlackNotificationConfiguration().withWebhook("webhook-url"));

    final StandardWorkspace workspace1 = new StandardWorkspace()
        .withWorkspaceId(WORKSPACE_ID_1)
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

    final StandardWorkspace workspace2 = new StandardWorkspace()
        .withWorkspaceId(WORKSPACE_ID_2)
        .withName("Another Workspace")
        .withSlug("another-workspace")
        .withInitialSetupComplete(true)
        .withTombstone(false);

    final StandardWorkspace workspace3 = new StandardWorkspace()
        .withWorkspaceId(WORKSPACE_ID_3)
        .withName("Tombstoned")
        .withSlug("tombstoned")
        .withInitialSetupComplete(true)
        .withTombstone(true);

    return Arrays.asList(workspace1, workspace2, workspace3);
  }

  public static StandardSourceDefinition publicSourceDefinition() {
    return new StandardSourceDefinition()
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_1)
        .withSourceType(SourceType.API)
        .withName("random-source-1")
        .withDockerImageTag("tag-1")
        .withDockerRepository("repository-1")
        .withDocumentationUrl("documentation-url-1")
        .withIcon("icon-1")
        .withSpec(connectorSpecification())
        .withTombstone(false)
        .withPublic(true)
        .withCustom(false)
        .withResourceRequirements(new ActorDefinitionResourceRequirements().withDefault(new ResourceRequirements().withCpuRequest("2")));
  }

  public static StandardSourceDefinition grantableSourceDefinition1() {
    return new StandardSourceDefinition()
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_2)
        .withSourceType(SourceType.DATABASE)
        .withName("random-source-2")
        .withDockerImageTag("tag-2")
        .withDockerRepository("repository-2")
        .withDocumentationUrl("documentation-url-2")
        .withIcon("icon-2")
        .withTombstone(false)
        .withPublic(false)
        .withCustom(false);
  }

  public static StandardSourceDefinition grantableSourceDefinition2() {
    return new StandardSourceDefinition()
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_3)
        .withSourceType(SourceType.DATABASE)
        .withName("random-source-3")
        .withDockerImageTag("tag-3")
        .withDockerRepository("repository-3")
        .withDocumentationUrl("documentation-url-3")
        .withIcon("icon-3")
        .withTombstone(false)
        .withPublic(false)
        .withCustom(false);
  }

  public static StandardSourceDefinition customSourceDefinition() {
    return new StandardSourceDefinition()
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_4)
        .withSourceType(SourceType.DATABASE)
        .withName("random-source-4")
        .withDockerImageTag("tag-4")
        .withDockerRepository("repository-4")
        .withDocumentationUrl("documentation-url-4")
        .withIcon("icon-4")
        .withTombstone(false)
        .withPublic(false)
        .withCustom(true);
  }

  public static List<StandardSourceDefinition> standardSourceDefinitions() {
    return Arrays.asList(
        publicSourceDefinition(),
        grantableSourceDefinition1(),
        grantableSourceDefinition2(),
        customSourceDefinition());
  }

  private static ConnectorSpecification connectorSpecification() {
    return new ConnectorSpecification()
        .withAuthSpecification(new AuthSpecification().withAuthType(AuthType.OAUTH_2_0))
        .withConnectionSpecification(Jsons.jsonNode("'{\"name\":\"John\", \"age\":30, \"car\":null}'"))
        .withDocumentationUrl(URI.create("whatever"))
        .withAdvancedAuth(null)
        .withChangelogUrl(URI.create("whatever"))
        .withSupportedDestinationSyncModes(Arrays.asList(DestinationSyncMode.APPEND, DestinationSyncMode.OVERWRITE, DestinationSyncMode.APPEND_DEDUP))
        .withSupportsDBT(true)
        .withSupportsIncremental(true)
        .withSupportsNormalization(true);
  }

  public static StandardDestinationDefinition publicDestinationDefinition() {
    return new StandardDestinationDefinition()
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_1)
        .withName("random-destination-1")
        .withDockerImageTag("tag-3")
        .withDockerRepository("repository-3")
        .withDocumentationUrl("documentation-url-3")
        .withIcon("icon-3")
        .withSpec(connectorSpecification())
        .withTombstone(false)
        .withPublic(true)
        .withCustom(false)
        .withResourceRequirements(new ActorDefinitionResourceRequirements().withDefault(new ResourceRequirements().withCpuRequest("2")));
  }

  public static StandardDestinationDefinition grantableDestinationDefinition1() {
    return new StandardDestinationDefinition()
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_2)
        .withName("random-destination-2")
        .withDockerImageTag("tag-4")
        .withDockerRepository("repository-4")
        .withDocumentationUrl("documentation-url-4")
        .withIcon("icon-4")
        .withSpec(connectorSpecification())
        .withTombstone(false)
        .withPublic(false)
        .withCustom(false);
  }

  public static StandardDestinationDefinition grantableDestinationDefinition2() {
    return new StandardDestinationDefinition()
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_3)
        .withName("random-destination-3")
        .withDockerImageTag("tag-33")
        .withDockerRepository("repository-33")
        .withDocumentationUrl("documentation-url-33")
        .withIcon("icon-3")
        .withSpec(connectorSpecification())
        .withTombstone(false)
        .withPublic(false)
        .withCustom(false);
  }

  public static StandardDestinationDefinition cusstomDestinationDefinition() {
    return new StandardDestinationDefinition()
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_4)
        .withName("random-destination-4")
        .withDockerImageTag("tag-44")
        .withDockerRepository("repository-44")
        .withDocumentationUrl("documentation-url-44")
        .withIcon("icon-4")
        .withSpec(connectorSpecification())
        .withTombstone(false)
        .withPublic(false)
        .withCustom(true);
  }

  public static List<StandardDestinationDefinition> standardDestinationDefinitions() {
    return Arrays.asList(
        publicDestinationDefinition(),
        grantableDestinationDefinition1(),
        grantableDestinationDefinition2(),
        cusstomDestinationDefinition());
  }

  public static List<SourceConnection> sourceConnections() {
    final SourceConnection sourceConnection1 = new SourceConnection()
        .withName("source-1")
        .withTombstone(false)
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_1)
        .withWorkspaceId(WORKSPACE_ID_1)
        .withConfiguration(Jsons.jsonNode("'{\"name\":\"John\", \"age\":30, \"car\":null}'"))
        .withSourceId(SOURCE_ID_1);
    final SourceConnection sourceConnection2 = new SourceConnection()
        .withName("source-2")
        .withTombstone(false)
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_2)
        .withWorkspaceId(WORKSPACE_ID_1)
        .withConfiguration(Jsons.jsonNode("'{\"name\":\"John\", \"age\":30, \"car\":null}'"))
        .withSourceId(SOURCE_ID_2);
    final SourceConnection sourceConnection3 = new SourceConnection()
        .withName("source-3")
        .withTombstone(false)
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_1)
        .withWorkspaceId(WORKSPACE_ID_2)
        .withConfiguration(Jsons.jsonNode(("")))
        .withSourceId(SOURCE_ID_3);
    return Arrays.asList(sourceConnection1, sourceConnection2, sourceConnection3);
  }

  public static List<DestinationConnection> destinationConnections() {
    final DestinationConnection destinationConnection1 = new DestinationConnection()
        .withName("destination-1")
        .withTombstone(false)
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_1)
        .withWorkspaceId(WORKSPACE_ID_1)
        .withConfiguration(Jsons.jsonNode("'{\"name\":\"John\", \"age\":30, \"car\":null}'"))
        .withDestinationId(DESTINATION_ID_1);
    final DestinationConnection destinationConnection2 = new DestinationConnection()
        .withName("destination-2")
        .withTombstone(false)
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_2)
        .withWorkspaceId(WORKSPACE_ID_1)
        .withConfiguration(Jsons.jsonNode("'{\"name\":\"John\", \"age\":30, \"car\":null}'"))
        .withDestinationId(DESTINATION_ID_2);
    final DestinationConnection destinationConnection3 = new DestinationConnection()
        .withName("destination-3")
        .withTombstone(true)
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_2)
        .withWorkspaceId(WORKSPACE_ID_2)
        .withConfiguration(Jsons.jsonNode(""))
        .withDestinationId(DESTINATION_ID_3);
    return Arrays.asList(destinationConnection1, destinationConnection2, destinationConnection3);
  }

  public static List<SourceOAuthParameter> sourceOauthParameters() {
    final SourceOAuthParameter sourceOAuthParameter1 = new SourceOAuthParameter()
        .withConfiguration(Jsons.jsonNode("'{\"name\":\"John\", \"age\":30, \"car\":null}'"))
        .withWorkspaceId(WORKSPACE_ID_1)
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_1)
        .withOauthParameterId(SOURCE_OAUTH_PARAMETER_ID_1);
    final SourceOAuthParameter sourceOAuthParameter2 = new SourceOAuthParameter()
        .withConfiguration(Jsons.jsonNode("'{\"name\":\"John\", \"age\":30, \"car\":null}'"))
        .withWorkspaceId(WORKSPACE_ID_1)
        .withSourceDefinitionId(SOURCE_DEFINITION_ID_2)
        .withOauthParameterId(SOURCE_OAUTH_PARAMETER_ID_2);
    return Arrays.asList(sourceOAuthParameter1, sourceOAuthParameter2);
  }

  public static List<DestinationOAuthParameter> destinationOauthParameters() {
    final DestinationOAuthParameter destinationOAuthParameter1 = new DestinationOAuthParameter()
        .withConfiguration(Jsons.jsonNode("'{\"name\":\"John\", \"age\":30, \"car\":null}'"))
        .withWorkspaceId(WORKSPACE_ID_1)
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID_1)
        .withOauthParameterId(DESTINATION_OAUTH_PARAMETER_ID_1);
    final DestinationOAuthParameter destinationOAuthParameter2 = new DestinationOAuthParameter()
        .withConfiguration(Jsons.jsonNode("'{\"name\":\"John\", \"age\":30, \"car\":null}'"))
        .withWorkspaceId(WORKSPACE_ID_1)
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
        .withWorkspaceId(WORKSPACE_ID_1)
        .withOperatorDbt(operatorDbt)
        .withOperatorNormalization(null)
        .withOperatorType(OperatorType.DBT);
    final StandardSyncOperation standardSyncOperation2 = new StandardSyncOperation()
        .withName("operation-1")
        .withTombstone(false)
        .withOperationId(OPERATION_ID_2)
        .withWorkspaceId(WORKSPACE_ID_1)
        .withOperatorDbt(null)
        .withOperatorNormalization(new OperatorNormalization().withOption(Option.BASIC))
        .withOperatorType(OperatorType.NORMALIZATION);
    final StandardSyncOperation standardSyncOperation3 = new StandardSyncOperation()
        .withName("operation-3")
        .withTombstone(false)
        .withOperationId(OPERATION_ID_3)
        .withWorkspaceId(WORKSPACE_ID_2)
        .withOperatorDbt(null)
        .withOperatorNormalization(new OperatorNormalization().withOption(Option.BASIC))
        .withOperatorType(OperatorType.NORMALIZATION);
    return Arrays.asList(standardSyncOperation1, standardSyncOperation2, standardSyncOperation3);
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

    final StandardSync standardSync5 = new StandardSync()
        .withOperationIds(Arrays.asList(OPERATION_ID_3))
        .withConnectionId(CONNECTION_ID_5)
        .withSourceId(SOURCE_ID_3)
        .withDestinationId(DESTINATION_ID_3)
        .withCatalog(getConfiguredCatalog())
        .withName("standard-sync-5")
        .withManual(true)
        .withNamespaceDefinition(NamespaceDefinitionType.CUSTOMFORMAT)
        .withNamespaceFormat("")
        .withPrefix("")
        .withResourceRequirements(resourceRequirements)
        .withStatus(Status.ACTIVE)
        .withSchedule(schedule);
    return Arrays.asList(standardSync1, standardSync2, standardSync3, standardSync4, standardSync5);
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
        .withState(new State().withState(Jsons.jsonNode("'{\"name\":\"John\", \"age\":30, \"car\":null}'")));
    final StandardSyncState standardSyncState2 = new StandardSyncState()
        .withConnectionId(CONNECTION_ID_2)
        .withState(new State().withState(Jsons.jsonNode("'{\"name\":\"John\", \"age\":30, \"car\":null}'")));
    final StandardSyncState standardSyncState3 = new StandardSyncState()
        .withConnectionId(CONNECTION_ID_3)
        .withState(new State().withState(Jsons.jsonNode("'{\"name\":\"John\", \"age\":30, \"car\":null}'")));
    final StandardSyncState standardSyncState4 = new StandardSyncState()
        .withConnectionId(CONNECTION_ID_4)
        .withState(new State().withState(Jsons.jsonNode("'{\"name\":\"John\", \"age\":30, \"car\":null}'")));
    return Arrays.asList(standardSyncState1, standardSyncState2, standardSyncState3, standardSyncState4);
  }

  public static List<ActorCatalog> actorCatalogs() {
    final ActorCatalog actorCatalog1 = new ActorCatalog()
        .withId(ACTOR_CATALOG_ID_1)
        .withCatalog(Jsons.deserialize("{}"))
        .withCatalogHash("TESTHASH");
    final ActorCatalog actorCatalog2 = new ActorCatalog()
        .withId(ACTOR_CATALOG_ID_2)
        .withCatalog(Jsons.deserialize("{}"))
        .withCatalogHash("12345");
    final ActorCatalog actorCatalog3 = new ActorCatalog()
        .withId(ACTOR_CATALOG_ID_3)
        .withCatalog(Jsons.deserialize("{}"))
        .withCatalogHash("SomeOtherHash");
    return Arrays.asList(actorCatalog1, actorCatalog2, actorCatalog3);
  }

  public static List<ActorCatalogFetchEvent> actorCatalogFetchEvents() {
    final ActorCatalogFetchEvent actorCatalogFetchEvent1 = new ActorCatalogFetchEvent()
        .withId(ACTOR_CATALOG_FETCH_EVENT_ID_1)
        .withActorCatalogId(ACTOR_CATALOG_ID_1)
        .withActorId(SOURCE_ID_1)
        .withConfigHash("CONFIG_HASH")
        .withConnectorVersion("1.0.0");
    final ActorCatalogFetchEvent actorCatalogFetchEvent2 = new ActorCatalogFetchEvent()
        .withId(ACTOR_CATALOG_FETCH_EVENT_ID_2)
        .withActorCatalogId(ACTOR_CATALOG_ID_2)
        .withActorId(SOURCE_ID_2)
        .withConfigHash("1394")
        .withConnectorVersion("1.2.0");
    return Arrays.asList(actorCatalogFetchEvent1);
  }

  public static Instant now() {
    return NOW;
  }

}
