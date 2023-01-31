/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_CATALOG;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_CATALOG_FETCH_EVENT;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_DEFINITION;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_OAUTH_PARAMETER;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.CONNECTION;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.WORKSPACE;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.WORKSPACE_SERVICE_ACCOUNT;

import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.protocol.migrations.v1.CatalogMigrationV1Helper;
import io.airbyte.config.ActorCatalog;
import io.airbyte.config.ActorCatalogFetchEvent;
import io.airbyte.config.ActorCatalogWithUpdatedAt;
import io.airbyte.config.ActorDefinitionResourceRequirements;
import io.airbyte.config.AllowedHosts;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.FieldSelectionData;
import io.airbyte.config.Geography;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.NormalizationDestinationDefinitionConfig;
import io.airbyte.config.Notification;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.Schedule;
import io.airbyte.config.ScheduleData;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSourceDefinition.SourceType;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.NonBreakingChangesPreference;
import io.airbyte.config.StandardSync.ScheduleType;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.SuggestedStreams;
import io.airbyte.config.WorkspaceServiceAccount;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.UUID;
import org.jooq.Record;

/**
 * Provides static methods for converting from repository layer results (often in the form of a jooq
 * {@link Record}) to config models.
 */
public class DbConverter {

  public static StandardSync buildStandardSync(final Record record, final List<UUID> connectionOperationId) {
    return new StandardSync()
        .withConnectionId(record.get(CONNECTION.ID))
        .withNamespaceDefinition(
            Enums.toEnum(record.get(CONNECTION.NAMESPACE_DEFINITION, String.class), NamespaceDefinitionType.class)
                .orElseThrow())
        .withNamespaceFormat(record.get(CONNECTION.NAMESPACE_FORMAT))
        .withPrefix(record.get(CONNECTION.PREFIX))
        .withSourceId(record.get(CONNECTION.SOURCE_ID))
        .withDestinationId(record.get(CONNECTION.DESTINATION_ID))
        .withName(record.get(CONNECTION.NAME))
        .withCatalog(parseConfiguredAirbyteCatalog(record.get(CONNECTION.CATALOG).data()))
        .withFieldSelectionData(record.get(CONNECTION.FIELD_SELECTION_DATA) == null ? null
            : Jsons.deserialize(record.get(CONNECTION.FIELD_SELECTION_DATA).data(), FieldSelectionData.class))
        .withStatus(
            record.get(CONNECTION.STATUS) == null ? null
                : Enums.toEnum(record.get(CONNECTION.STATUS, String.class), Status.class).orElseThrow())
        .withSchedule(Jsons.deserialize(record.get(CONNECTION.SCHEDULE).data(), Schedule.class))
        .withManual(record.get(CONNECTION.MANUAL))
        .withScheduleType(record.get(CONNECTION.SCHEDULE_TYPE) == null ? null
            : Enums.toEnum(record.get(CONNECTION.SCHEDULE_TYPE, String.class), ScheduleType.class).orElseThrow())
        .withScheduleData(
            record.get(CONNECTION.SCHEDULE_DATA) == null ? null
                : Jsons.deserialize(record.get(CONNECTION.SCHEDULE_DATA).data(), ScheduleData.class))
        .withOperationIds(connectionOperationId)
        .withResourceRequirements(
            Jsons.deserialize(record.get(CONNECTION.RESOURCE_REQUIREMENTS).data(), ResourceRequirements.class))
        .withSourceCatalogId(record.get(CONNECTION.SOURCE_CATALOG_ID))
        .withBreakingChange(record.get(CONNECTION.BREAKING_CHANGE))
        .withGeography(Enums.toEnum(record.get(CONNECTION.GEOGRAPHY, String.class), Geography.class).orElseThrow())
        .withNonBreakingChangesPreference(
            Enums.toEnum(record.get(CONNECTION.NON_BREAKING_CHANGE_PREFERENCE, String.class), NonBreakingChangesPreference.class).orElseThrow())
        .withNotifySchemaChanges(record.get(CONNECTION.NOTIFY_SCHEMA_CHANGES));
  }

  private static ConfiguredAirbyteCatalog parseConfiguredAirbyteCatalog(final String configuredAirbyteCatalogString) {
    final ConfiguredAirbyteCatalog configuredAirbyteCatalog = Jsons.deserialize(configuredAirbyteCatalogString, ConfiguredAirbyteCatalog.class);
    // On-the-fly migration of persisted data types related objects (protocol v0->v1)
    CatalogMigrationV1Helper.upgradeSchemaIfNeeded(configuredAirbyteCatalog);
    return configuredAirbyteCatalog;
  }

  public static StandardWorkspace buildStandardWorkspace(final Record record) {
    final List<Notification> notificationList = new ArrayList<>();
    final List fetchedNotifications = Jsons.deserialize(record.get(WORKSPACE.NOTIFICATIONS).data(), List.class);
    for (final Object notification : fetchedNotifications) {
      notificationList.add(Jsons.convertValue(notification, Notification.class));
    }
    return new StandardWorkspace()
        .withWorkspaceId(record.get(WORKSPACE.ID))
        .withName(record.get(WORKSPACE.NAME))
        .withSlug(record.get(WORKSPACE.SLUG))
        .withInitialSetupComplete(record.get(WORKSPACE.INITIAL_SETUP_COMPLETE))
        .withCustomerId(record.get(WORKSPACE.CUSTOMER_ID))
        .withEmail(record.get(WORKSPACE.EMAIL))
        .withAnonymousDataCollection(record.get(WORKSPACE.ANONYMOUS_DATA_COLLECTION))
        .withNews(record.get(WORKSPACE.SEND_NEWSLETTER))
        .withSecurityUpdates(record.get(WORKSPACE.SEND_SECURITY_UPDATES))
        .withDisplaySetupWizard(record.get(WORKSPACE.DISPLAY_SETUP_WIZARD))
        .withTombstone(record.get(WORKSPACE.TOMBSTONE))
        .withNotifications(notificationList)
        .withFirstCompletedSync(record.get(WORKSPACE.FIRST_SYNC_COMPLETE))
        .withFeedbackDone(record.get(WORKSPACE.FEEDBACK_COMPLETE))
        .withDefaultGeography(
            Enums.toEnum(record.get(WORKSPACE.GEOGRAPHY, String.class), Geography.class).orElseThrow())
        .withWebhookOperationConfigs(record.get(WORKSPACE.WEBHOOK_OPERATION_CONFIGS) == null ? null
            : Jsons.deserialize(record.get(WORKSPACE.WEBHOOK_OPERATION_CONFIGS).data()));
  }

  public static SourceConnection buildSourceConnection(final Record record) {
    return new SourceConnection()
        .withSourceId(record.get(ACTOR.ID))
        .withConfiguration(Jsons.deserialize(record.get(ACTOR.CONFIGURATION).data()))
        .withWorkspaceId(record.get(ACTOR.WORKSPACE_ID))
        .withSourceDefinitionId(record.get(ACTOR.ACTOR_DEFINITION_ID))
        .withTombstone(record.get(ACTOR.TOMBSTONE))
        .withName(record.get(ACTOR.NAME));
  }

  public static DestinationConnection buildDestinationConnection(final Record record) {
    return new DestinationConnection()
        .withDestinationId(record.get(ACTOR.ID))
        .withConfiguration(Jsons.deserialize(record.get(ACTOR.CONFIGURATION).data()))
        .withWorkspaceId(record.get(ACTOR.WORKSPACE_ID))
        .withDestinationDefinitionId(record.get(ACTOR.ACTOR_DEFINITION_ID))
        .withTombstone(record.get(ACTOR.TOMBSTONE))
        .withName(record.get(ACTOR.NAME));
  }

  public static StandardSourceDefinition buildStandardSourceDefinition(final Record record) {
    return new StandardSourceDefinition()
        .withSourceDefinitionId(record.get(ACTOR_DEFINITION.ID))
        .withDockerImageTag(record.get(ACTOR_DEFINITION.DOCKER_IMAGE_TAG))
        .withIcon(record.get(ACTOR_DEFINITION.ICON))
        .withDockerRepository(record.get(ACTOR_DEFINITION.DOCKER_REPOSITORY))
        .withDocumentationUrl(record.get(ACTOR_DEFINITION.DOCUMENTATION_URL))
        .withName(record.get(ACTOR_DEFINITION.NAME))
        .withSourceType(record.get(ACTOR_DEFINITION.SOURCE_TYPE) == null ? null
            : Enums.toEnum(record.get(ACTOR_DEFINITION.SOURCE_TYPE, String.class), SourceType.class).orElseThrow())
        .withSpec(Jsons.deserialize(record.get(ACTOR_DEFINITION.SPEC).data(), ConnectorSpecification.class))
        .withProtocolVersion(record.get(ACTOR_DEFINITION.PROTOCOL_VERSION, String.class))
        .withTombstone(record.get(ACTOR_DEFINITION.TOMBSTONE))
        .withPublic(record.get(ACTOR_DEFINITION.PUBLIC))
        .withCustom(record.get(ACTOR_DEFINITION.CUSTOM))
        .withReleaseStage(record.get(ACTOR_DEFINITION.RELEASE_STAGE) == null ? null
            : Enums.toEnum(record.get(ACTOR_DEFINITION.RELEASE_STAGE, String.class), StandardSourceDefinition.ReleaseStage.class).orElseThrow())
        .withReleaseDate(record.get(ACTOR_DEFINITION.RELEASE_DATE) == null ? null
            : record.get(ACTOR_DEFINITION.RELEASE_DATE).toString())
        .withResourceRequirements(record.get(ACTOR_DEFINITION.RESOURCE_REQUIREMENTS) == null
            ? null
            : Jsons.deserialize(record.get(ACTOR_DEFINITION.RESOURCE_REQUIREMENTS).data(), ActorDefinitionResourceRequirements.class))
        .withAllowedHosts(record.get(ACTOR_DEFINITION.ALLOWED_HOSTS) == null
            ? null
            : Jsons.deserialize(record.get(ACTOR_DEFINITION.ALLOWED_HOSTS).data(), AllowedHosts.class))
        .withSuggestedStreams(record.get(ACTOR_DEFINITION.SUGGESTED_STREAMS) == null
            ? null
            : Jsons.deserialize(record.get(ACTOR_DEFINITION.SUGGESTED_STREAMS).data(), SuggestedStreams.class));
  }

  public static StandardDestinationDefinition buildStandardDestinationDefinition(final Record record) {
    return new StandardDestinationDefinition()
        .withDestinationDefinitionId(record.get(ACTOR_DEFINITION.ID))
        .withDockerImageTag(record.get(ACTOR_DEFINITION.DOCKER_IMAGE_TAG))
        .withIcon(record.get(ACTOR_DEFINITION.ICON))
        .withDockerRepository(record.get(ACTOR_DEFINITION.DOCKER_REPOSITORY))
        .withDocumentationUrl(record.get(ACTOR_DEFINITION.DOCUMENTATION_URL))
        .withName(record.get(ACTOR_DEFINITION.NAME))
        .withSpec(Jsons.deserialize(record.get(ACTOR_DEFINITION.SPEC).data(), ConnectorSpecification.class))
        .withProtocolVersion(record.get(ACTOR_DEFINITION.PROTOCOL_VERSION, String.class))
        .withTombstone(record.get(ACTOR_DEFINITION.TOMBSTONE))
        .withPublic(record.get(ACTOR_DEFINITION.PUBLIC))
        .withCustom(record.get(ACTOR_DEFINITION.CUSTOM))
        .withReleaseStage(record.get(ACTOR_DEFINITION.RELEASE_STAGE) == null ? null
            : Enums.toEnum(record.get(ACTOR_DEFINITION.RELEASE_STAGE, String.class), StandardDestinationDefinition.ReleaseStage.class).orElseThrow())
        .withReleaseDate(record.get(ACTOR_DEFINITION.RELEASE_DATE) == null ? null
            : record.get(ACTOR_DEFINITION.RELEASE_DATE).toString())
        .withSupportsDbt(record.get(ACTOR_DEFINITION.SUPPORTS_DBT) == null ? null
            : record.get(ACTOR_DEFINITION.SUPPORTS_DBT))
        .withNormalizationConfig(
            Objects.nonNull(record.get(ACTOR_DEFINITION.NORMALIZATION_REPOSITORY)) && Objects.nonNull(record.get(ACTOR_DEFINITION.NORMALIZATION_TAG))
                &&
                Objects.nonNull(record.get(ACTOR_DEFINITION.NORMALIZATION_INTEGRATION_TYPE))
                    ? new NormalizationDestinationDefinitionConfig()
                        .withNormalizationRepository(record.get(ACTOR_DEFINITION.NORMALIZATION_REPOSITORY))
                        .withNormalizationTag(record.get(ACTOR_DEFINITION.NORMALIZATION_TAG))
                        .withNormalizationIntegrationType(record.get(ACTOR_DEFINITION.NORMALIZATION_INTEGRATION_TYPE))
                    : null)
        .withResourceRequirements(record.get(ACTOR_DEFINITION.RESOURCE_REQUIREMENTS) == null
            ? null
            : Jsons.deserialize(record.get(ACTOR_DEFINITION.RESOURCE_REQUIREMENTS).data(), ActorDefinitionResourceRequirements.class))
        .withAllowedHosts(record.get(ACTOR_DEFINITION.ALLOWED_HOSTS) == null
            ? null
            : Jsons.deserialize(record.get(ACTOR_DEFINITION.ALLOWED_HOSTS).data(), AllowedHosts.class));
  }

  public static DestinationOAuthParameter buildDestinationOAuthParameter(final Record record) {
    return new DestinationOAuthParameter()
        .withOauthParameterId(record.get(ACTOR_OAUTH_PARAMETER.ID))
        .withConfiguration(Jsons.deserialize(record.get(ACTOR_OAUTH_PARAMETER.CONFIGURATION).data()))
        .withWorkspaceId(record.get(ACTOR_OAUTH_PARAMETER.WORKSPACE_ID))
        .withDestinationDefinitionId(record.get(ACTOR_OAUTH_PARAMETER.ACTOR_DEFINITION_ID));
  }

  public static SourceOAuthParameter buildSourceOAuthParameter(final Record record) {
    return new SourceOAuthParameter()
        .withOauthParameterId(record.get(ACTOR_OAUTH_PARAMETER.ID))
        .withConfiguration(Jsons.deserialize(record.get(ACTOR_OAUTH_PARAMETER.CONFIGURATION).data()))
        .withWorkspaceId(record.get(ACTOR_OAUTH_PARAMETER.WORKSPACE_ID))
        .withSourceDefinitionId(record.get(ACTOR_OAUTH_PARAMETER.ACTOR_DEFINITION_ID));
  }

  public static ActorCatalog buildActorCatalog(final Record record) {
    return new ActorCatalog()
        .withId(record.get(ACTOR_CATALOG.ID))
        .withCatalog(Jsons.jsonNode(parseAirbyteCatalog(record.get(ACTOR_CATALOG.CATALOG).toString())))
        .withCatalogHash(record.get(ACTOR_CATALOG.CATALOG_HASH));
  }

  public static ActorCatalogWithUpdatedAt buildActorCatalogWithUpdatedAt(final Record record) {
    return new ActorCatalogWithUpdatedAt()
        .withId(record.get(ACTOR_CATALOG.ID))
        .withCatalog(Jsons.jsonNode(parseAirbyteCatalog(record.get(ACTOR_CATALOG.CATALOG).toString())))
        .withCatalogHash(record.get(ACTOR_CATALOG.CATALOG_HASH))
        .withUpdatedAt(record.get(ACTOR_CATALOG_FETCH_EVENT.CREATED_AT, LocalDateTime.class).toEpochSecond(ZoneOffset.UTC));
  }

  public static AirbyteCatalog parseAirbyteCatalog(final String airbyteCatalogString) {
    final AirbyteCatalog airbyteCatalog = Jsons.deserialize(airbyteCatalogString, AirbyteCatalog.class);
    // On-the-fly migration of persisted data types related objects (protocol v0->v1)
    CatalogMigrationV1Helper.upgradeSchemaIfNeeded(airbyteCatalog);
    return airbyteCatalog;
  }

  public static ActorCatalogFetchEvent buildActorCatalogFetchEvent(final Record record) {
    return new ActorCatalogFetchEvent()
        .withActorId(record.get(ACTOR_CATALOG_FETCH_EVENT.ACTOR_ID))
        .withActorCatalogId(record.get(ACTOR_CATALOG_FETCH_EVENT.ACTOR_CATALOG_ID))
        .withCreatedAt(record.get(ACTOR_CATALOG_FETCH_EVENT.CREATED_AT, LocalDateTime.class).toEpochSecond(ZoneOffset.UTC));
  }

  public static WorkspaceServiceAccount buildWorkspaceServiceAccount(final Record record) {
    return new WorkspaceServiceAccount()
        .withWorkspaceId(record.get(WORKSPACE_SERVICE_ACCOUNT.WORKSPACE_ID))
        .withServiceAccountId(record.get(WORKSPACE_SERVICE_ACCOUNT.SERVICE_ACCOUNT_ID))
        .withServiceAccountEmail(record.get(WORKSPACE_SERVICE_ACCOUNT.SERVICE_ACCOUNT_EMAIL))
        .withJsonCredential(record.get(WORKSPACE_SERVICE_ACCOUNT.JSON_CREDENTIAL) == null ? null
            : Jsons.deserialize(record.get(WORKSPACE_SERVICE_ACCOUNT.JSON_CREDENTIAL).data()))
        .withHmacKey(record.get(WORKSPACE_SERVICE_ACCOUNT.HMAC_KEY) == null ? null
            : Jsons.deserialize(record.get(WORKSPACE_SERVICE_ACCOUNT.HMAC_KEY).data()));
  }

}
