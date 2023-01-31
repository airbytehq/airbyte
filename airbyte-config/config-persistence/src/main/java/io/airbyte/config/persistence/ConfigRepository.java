/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_CATALOG;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_CATALOG_FETCH_EVENT;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_DEFINITION;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_DEFINITION_WORKSPACE_GRANT;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_OAUTH_PARAMETER;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.CONNECTION;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.CONNECTION_OPERATION;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.OPERATION;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.WORKSPACE;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.WORKSPACE_SERVICE_ACCOUNT;
import static io.airbyte.db.instance.jobs.jooq.generated.Tables.JOBS;
import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.groupConcat;
import static org.jooq.impl.DSL.noCondition;
import static org.jooq.impl.DSL.select;
import static org.jooq.impl.SQLDataType.VARCHAR;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Charsets;
import com.google.common.collect.Sets;
import com.google.common.hash.HashFunction;
import com.google.common.hash.Hashing;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.commons.version.AirbyteProtocolVersionRange;
import io.airbyte.commons.version.Version;
import io.airbyte.config.ActorCatalog;
import io.airbyte.config.ActorCatalogFetchEvent;
import io.airbyte.config.ActorCatalogWithUpdatedAt;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.Geography;
import io.airbyte.config.OperatorDbt;
import io.airbyte.config.OperatorNormalization;
import io.airbyte.config.OperatorWebhook;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOperation.OperatorType;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.WorkspaceServiceAccount;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.db.instance.configs.jooq.generated.enums.ActorType;
import io.airbyte.db.instance.configs.jooq.generated.enums.ReleaseStage;
import io.airbyte.db.instance.configs.jooq.generated.enums.StatusType;
import io.airbyte.metrics.lib.MetricQueries;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.validation.json.JsonValidationException;
import jakarta.annotation.Nonnull;
import java.io.IOException;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.lang3.ArrayUtils;
import org.jooq.Condition;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.JSONB;
import org.jooq.JoinType;
import org.jooq.Record;
import org.jooq.Record1;
import org.jooq.Record2;
import org.jooq.Result;
import org.jooq.SelectJoinStep;
import org.jooq.Table;
import org.jooq.impl.DSL;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings({"PMD.AvoidThrowingRawExceptionTypes", "PMD.CyclomaticComplexity", "PMD.AvoidLiteralsInIfCondition",
  "OptionalUsedAsFieldOrParameterType"})
public class ConfigRepository {

  public record StandardSyncQuery(@Nonnull UUID workspaceId, List<UUID> sourceId, List<UUID> destinationId, boolean includeDeleted) {}

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigRepository.class);
  private static final String OPERATION_IDS_AGG_FIELD = "operation_ids_agg";
  private static final String OPERATION_IDS_AGG_DELIMITER = ",";
  public static final String PRIMARY_KEY = "id";

  private final ExceptionWrappingDatabase database;
  private final ActorDefinitionMigrator actorDefinitionMigrator;
  private final StandardSyncPersistence standardSyncPersistence;

  public ConfigRepository(final Database database) {
    this(database, new ActorDefinitionMigrator(new ExceptionWrappingDatabase(database)), new StandardSyncPersistence(database));
  }

  ConfigRepository(final Database database,
                   final ActorDefinitionMigrator actorDefinitionMigrator,
                   final StandardSyncPersistence standardSyncPersistence) {
    this.database = new ExceptionWrappingDatabase(database);
    this.actorDefinitionMigrator = actorDefinitionMigrator;
    this.standardSyncPersistence = standardSyncPersistence;
  }

  /**
   * Conduct a health check by attempting to read from the database. Since there isn't an
   * out-of-the-box call for this, mimic doing so by reading the ID column from the Workspace table's
   * first row. This query needs to be fast as this call can be made multiple times a second.
   *
   * @return true if read succeeds, even if the table is empty, and false if any error happens.
   */
  public boolean healthCheck() {
    try {
      database.query(ctx -> ctx.select(WORKSPACE.ID).from(WORKSPACE).limit(1).fetch()).stream().count();
    } catch (final Exception e) {
      LOGGER.error("Health check error: ", e);
      return false;
    }
    return true;
  }

  public StandardWorkspace getStandardWorkspaceNoSecrets(final UUID workspaceId, final boolean includeTombstone)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return listWorkspaceQuery(Optional.of(workspaceId), includeTombstone)
        .findFirst()
        .orElseThrow(() -> new ConfigNotFoundException(ConfigSchema.STANDARD_WORKSPACE, workspaceId));
  }

  public Optional<StandardWorkspace> getWorkspaceBySlugOptional(final String slug, final boolean includeTombstone)
      throws IOException {
    final Result<Record> result;
    if (includeTombstone) {
      result = database.query(ctx -> ctx.select(WORKSPACE.asterisk())
          .from(WORKSPACE)
          .where(WORKSPACE.SLUG.eq(slug))).fetch();
    } else {
      result = database.query(ctx -> ctx.select(WORKSPACE.asterisk())
          .from(WORKSPACE)
          .where(WORKSPACE.SLUG.eq(slug)).andNot(WORKSPACE.TOMBSTONE)).fetch();
    }

    return result.stream().findFirst().map(DbConverter::buildStandardWorkspace);
  }

  public StandardWorkspace getWorkspaceBySlug(final String slug, final boolean includeTombstone) throws IOException, ConfigNotFoundException {
    return getWorkspaceBySlugOptional(slug, includeTombstone).orElseThrow(() -> new ConfigNotFoundException(ConfigSchema.STANDARD_WORKSPACE, slug));
  }

  public List<StandardWorkspace> listStandardWorkspaces(final boolean includeTombstone) throws IOException {
    return listWorkspaceQuery(Optional.empty(), includeTombstone).toList();
  }

  private Stream<StandardWorkspace> listWorkspaceQuery(final Optional<UUID> workspaceId, final boolean includeTombstone) throws IOException {
    return database.query(ctx -> ctx.select(WORKSPACE.asterisk())
        .from(WORKSPACE)
        .where(includeTombstone ? noCondition() : WORKSPACE.TOMBSTONE.notEqual(true))
        .and(workspaceId.map(WORKSPACE.ID::eq).orElse(noCondition()))
        .fetch())
        .stream()
        .map(DbConverter::buildStandardWorkspace);
  }

  /**
   * MUST NOT ACCEPT SECRETS - Should only be called from { @link SecretsRepositoryWriter }
   *
   * Write a StandardWorkspace to the database.
   *
   * @param workspace - The configuration of the workspace
   * @throws JsonValidationException - throws is the workspace is invalid
   * @throws IOException - you never know when you IO
   */
  public void writeStandardWorkspaceNoSecrets(final StandardWorkspace workspace) throws JsonValidationException, IOException {
    database.transaction(ctx -> {
      final OffsetDateTime timestamp = OffsetDateTime.now();
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(WORKSPACE)
          .where(WORKSPACE.ID.eq(workspace.getWorkspaceId())));

      if (isExistingConfig) {
        ctx.update(WORKSPACE)
            .set(WORKSPACE.ID, workspace.getWorkspaceId())
            .set(WORKSPACE.CUSTOMER_ID, workspace.getCustomerId())
            .set(WORKSPACE.NAME, workspace.getName())
            .set(WORKSPACE.SLUG, workspace.getSlug())
            .set(WORKSPACE.EMAIL, workspace.getEmail())
            .set(WORKSPACE.INITIAL_SETUP_COMPLETE, workspace.getInitialSetupComplete())
            .set(WORKSPACE.ANONYMOUS_DATA_COLLECTION, workspace.getAnonymousDataCollection())
            .set(WORKSPACE.SEND_NEWSLETTER, workspace.getNews())
            .set(WORKSPACE.SEND_SECURITY_UPDATES, workspace.getSecurityUpdates())
            .set(WORKSPACE.DISPLAY_SETUP_WIZARD, workspace.getDisplaySetupWizard())
            .set(WORKSPACE.TOMBSTONE, workspace.getTombstone() != null && workspace.getTombstone())
            .set(WORKSPACE.NOTIFICATIONS, JSONB.valueOf(Jsons.serialize(workspace.getNotifications())))
            .set(WORKSPACE.FIRST_SYNC_COMPLETE, workspace.getFirstCompletedSync())
            .set(WORKSPACE.FEEDBACK_COMPLETE, workspace.getFeedbackDone())
            .set(WORKSPACE.GEOGRAPHY, Enums.toEnum(
                workspace.getDefaultGeography().value(),
                io.airbyte.db.instance.configs.jooq.generated.enums.GeographyType.class).orElseThrow())
            .set(WORKSPACE.UPDATED_AT, timestamp)
            .set(WORKSPACE.WEBHOOK_OPERATION_CONFIGS, workspace.getWebhookOperationConfigs() == null ? null
                : JSONB.valueOf(Jsons.serialize(workspace.getWebhookOperationConfigs())))
            .where(WORKSPACE.ID.eq(workspace.getWorkspaceId()))
            .execute();
      } else {
        ctx.insertInto(WORKSPACE)
            .set(WORKSPACE.ID, workspace.getWorkspaceId())
            .set(WORKSPACE.CUSTOMER_ID, workspace.getCustomerId())
            .set(WORKSPACE.NAME, workspace.getName())
            .set(WORKSPACE.SLUG, workspace.getSlug())
            .set(WORKSPACE.EMAIL, workspace.getEmail())
            .set(WORKSPACE.INITIAL_SETUP_COMPLETE, workspace.getInitialSetupComplete())
            .set(WORKSPACE.ANONYMOUS_DATA_COLLECTION, workspace.getAnonymousDataCollection())
            .set(WORKSPACE.SEND_NEWSLETTER, workspace.getNews())
            .set(WORKSPACE.SEND_SECURITY_UPDATES, workspace.getSecurityUpdates())
            .set(WORKSPACE.DISPLAY_SETUP_WIZARD, workspace.getDisplaySetupWizard())
            .set(WORKSPACE.TOMBSTONE, workspace.getTombstone() != null && workspace.getTombstone())
            .set(WORKSPACE.NOTIFICATIONS, JSONB.valueOf(Jsons.serialize(workspace.getNotifications())))
            .set(WORKSPACE.FIRST_SYNC_COMPLETE, workspace.getFirstCompletedSync())
            .set(WORKSPACE.FEEDBACK_COMPLETE, workspace.getFeedbackDone())
            .set(WORKSPACE.CREATED_AT, timestamp)
            .set(WORKSPACE.UPDATED_AT, timestamp)
            .set(WORKSPACE.GEOGRAPHY, Enums.toEnum(
                workspace.getDefaultGeography().value(),
                io.airbyte.db.instance.configs.jooq.generated.enums.GeographyType.class).orElseThrow())
            .set(WORKSPACE.WEBHOOK_OPERATION_CONFIGS, workspace.getWebhookOperationConfigs() == null ? null
                : JSONB.valueOf(Jsons.serialize(workspace.getWebhookOperationConfigs())))
            .execute();
      }
      return null;

    });
  }

  public void setFeedback(final UUID workflowId) throws IOException {
    database.query(ctx -> ctx.update(WORKSPACE).set(WORKSPACE.FEEDBACK_COMPLETE, true).where(WORKSPACE.ID.eq(workflowId)).execute());
  }

  public StandardSourceDefinition getStandardSourceDefinition(final UUID sourceDefinitionId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return sourceDefQuery(Optional.of(sourceDefinitionId), true)
        .findFirst()
        .orElseThrow(() -> new ConfigNotFoundException(ConfigSchema.STANDARD_SOURCE_DEFINITION, sourceDefinitionId));
  }

  public StandardSourceDefinition getSourceDefinitionFromSource(final UUID sourceId) {
    try {
      final SourceConnection source = getSourceConnection(sourceId);
      return getStandardSourceDefinition(source.getSourceDefinitionId());
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  public StandardSourceDefinition getSourceDefinitionFromConnection(final UUID connectionId) {
    try {
      final StandardSync sync = getStandardSync(connectionId);
      return getSourceDefinitionFromSource(sync.getSourceId());
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  public StandardWorkspace getStandardWorkspaceFromConnection(final UUID connectionId, final boolean isTombstone) {
    try {
      final StandardSync sync = getStandardSync(connectionId);
      final SourceConnection source = getSourceConnection(sync.getSourceId());
      return getStandardWorkspaceNoSecrets(source.getWorkspaceId(), isTombstone);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  public List<StandardSourceDefinition> listStandardSourceDefinitions(final boolean includeTombstone) throws IOException {
    return sourceDefQuery(Optional.empty(), includeTombstone).toList();
  }

  private Stream<StandardSourceDefinition> sourceDefQuery(final Optional<UUID> sourceDefId, final boolean includeTombstone) throws IOException {
    return database.query(ctx -> ctx.select(ACTOR_DEFINITION.asterisk())
        .from(ACTOR_DEFINITION)
        .where(ACTOR_DEFINITION.ACTOR_TYPE.eq(ActorType.source))
        .and(sourceDefId.map(ACTOR_DEFINITION.ID::eq).orElse(noCondition()))
        .and(includeTombstone ? noCondition() : ACTOR_DEFINITION.TOMBSTONE.notEqual(true))
        .fetch())
        .stream()
        .map(DbConverter::buildStandardSourceDefinition)
        // Ensure version is set. Needed for connectors not upgraded since we added versioning.
        .map(def -> def.withProtocolVersion(AirbyteProtocolVersion.getWithDefault(def.getProtocolVersion()).serialize()));
  }

  public Map<UUID, Map.Entry<io.airbyte.config.ActorType, Version>> getActorDefinitionToProtocolVersionMap() throws IOException {
    return database.query(ConfigWriter::getActorDefinitionsInUseToProtocolVersion);
  }

  public List<StandardSourceDefinition> listPublicSourceDefinitions(final boolean includeTombstone) throws IOException {
    return listStandardActorDefinitions(
        ActorType.source,
        DbConverter::buildStandardSourceDefinition,
        includeTombstones(ACTOR_DEFINITION.TOMBSTONE, includeTombstone),
        ACTOR_DEFINITION.PUBLIC.eq(true));
  }

  public List<StandardSourceDefinition> listGrantedSourceDefinitions(final UUID workspaceId, final boolean includeTombstones)
      throws IOException {
    return listActorDefinitionsJoinedWithGrants(
        workspaceId,
        JoinType.JOIN,
        ActorType.source,
        DbConverter::buildStandardSourceDefinition,
        includeTombstones(ACTOR_DEFINITION.TOMBSTONE, includeTombstones));
  }

  public List<Entry<StandardSourceDefinition, Boolean>> listGrantableSourceDefinitions(final UUID workspaceId,
                                                                                       final boolean includeTombstones)
      throws IOException {
    return listActorDefinitionsJoinedWithGrants(
        workspaceId,
        JoinType.LEFT_OUTER_JOIN,
        ActorType.source,
        record -> actorDefinitionWithGrantStatus(record, DbConverter::buildStandardSourceDefinition),
        ACTOR_DEFINITION.CUSTOM.eq(false),
        includeTombstones(ACTOR_DEFINITION.TOMBSTONE, includeTombstones));
  }

  public void writeStandardSourceDefinition(final StandardSourceDefinition sourceDefinition) throws JsonValidationException, IOException {
    database.transaction(ctx -> {
      ConfigWriter.writeStandardSourceDefinition(Collections.singletonList(sourceDefinition), ctx);
      return null;
    });
  }

  public void writeCustomSourceDefinition(final StandardSourceDefinition sourceDefinition, final UUID workspaceId)
      throws IOException {
    database.transaction(ctx -> {
      ConfigWriter.writeStandardSourceDefinition(Collections.singletonList(sourceDefinition), ctx);
      writeActorDefinitionWorkspaceGrant(sourceDefinition.getSourceDefinitionId(), workspaceId, ctx);
      return null;
    });
  }

  private Stream<StandardDestinationDefinition> destDefQuery(final Optional<UUID> destDefId, final boolean includeTombstone) throws IOException {
    return database.query(ctx -> ctx.select(ACTOR_DEFINITION.asterisk())
        .from(ACTOR_DEFINITION)
        .where(ACTOR_DEFINITION.ACTOR_TYPE.eq(ActorType.destination))
        .and(destDefId.map(ACTOR_DEFINITION.ID::eq).orElse(noCondition()))
        .and(includeTombstone ? noCondition() : ACTOR_DEFINITION.TOMBSTONE.notEqual(true))
        .fetch())
        .stream()
        .map(DbConverter::buildStandardDestinationDefinition)
        // Ensure version is set. Needed for connectors not upgraded since we added versioning.
        .map(def -> def.withProtocolVersion(AirbyteProtocolVersion.getWithDefault(def.getProtocolVersion()).serialize()));
  }

  public StandardDestinationDefinition getStandardDestinationDefinition(final UUID destinationDefinitionId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return destDefQuery(Optional.of(destinationDefinitionId), true)
        .findFirst()
        .orElseThrow(() -> new ConfigNotFoundException(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destinationDefinitionId));
  }

  public StandardDestinationDefinition getDestinationDefinitionFromDestination(final UUID destinationId) {
    try {
      final DestinationConnection destination = getDestinationConnection(destinationId);
      return getStandardDestinationDefinition(destination.getDestinationDefinitionId());
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  public StandardDestinationDefinition getDestinationDefinitionFromConnection(final UUID connectionId) {
    try {
      final StandardSync sync = getStandardSync(connectionId);
      return getDestinationDefinitionFromDestination(sync.getDestinationId());
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  public List<StandardDestinationDefinition> listStandardDestinationDefinitions(final boolean includeTombstone) throws IOException {
    return destDefQuery(Optional.empty(), includeTombstone).toList();
  }

  public List<StandardDestinationDefinition> listPublicDestinationDefinitions(final boolean includeTombstone) throws IOException {
    return listStandardActorDefinitions(
        ActorType.destination,
        DbConverter::buildStandardDestinationDefinition,
        includeTombstones(ACTOR_DEFINITION.TOMBSTONE, includeTombstone),
        ACTOR_DEFINITION.PUBLIC.eq(true));
  }

  public List<StandardDestinationDefinition> listGrantedDestinationDefinitions(final UUID workspaceId, final boolean includeTombstones)
      throws IOException {
    return listActorDefinitionsJoinedWithGrants(
        workspaceId,
        JoinType.JOIN,
        ActorType.destination,
        DbConverter::buildStandardDestinationDefinition,
        includeTombstones(ACTOR_DEFINITION.TOMBSTONE, includeTombstones));
  }

  public List<Entry<StandardDestinationDefinition, Boolean>> listGrantableDestinationDefinitions(final UUID workspaceId,
                                                                                                 final boolean includeTombstones)
      throws IOException {
    return listActorDefinitionsJoinedWithGrants(
        workspaceId,
        JoinType.LEFT_OUTER_JOIN,
        ActorType.destination,
        record -> actorDefinitionWithGrantStatus(record, DbConverter::buildStandardDestinationDefinition),
        ACTOR_DEFINITION.CUSTOM.eq(false),
        includeTombstones(ACTOR_DEFINITION.TOMBSTONE, includeTombstones));
  }

  public void writeStandardDestinationDefinition(final StandardDestinationDefinition destinationDefinition)
      throws JsonValidationException, IOException {
    database.transaction(ctx -> {
      ConfigWriter.writeStandardDestinationDefinition(Collections.singletonList(destinationDefinition), ctx);
      return null;
    });
  }

  public void writeCustomDestinationDefinition(final StandardDestinationDefinition destinationDefinition, final UUID workspaceId)
      throws IOException {
    database.transaction(ctx -> {
      ConfigWriter.writeStandardDestinationDefinition(List.of(destinationDefinition), ctx);
      writeActorDefinitionWorkspaceGrant(destinationDefinition.getDestinationDefinitionId(), workspaceId, ctx);
      return null;
    });
  }

  public void deleteStandardSync(final UUID syncId) throws IOException {
    standardSyncPersistence.deleteStandardSync(syncId);
  }

  public void writeActorDefinitionWorkspaceGrant(final UUID actorDefinitionId, final UUID workspaceId) throws IOException {
    database.query(ctx -> writeActorDefinitionWorkspaceGrant(actorDefinitionId, workspaceId, ctx));
  }

  private int writeActorDefinitionWorkspaceGrant(final UUID actorDefinitionId, final UUID workspaceId, final DSLContext ctx) {
    return ctx.insertInto(ACTOR_DEFINITION_WORKSPACE_GRANT)
        .set(ACTOR_DEFINITION_WORKSPACE_GRANT.ACTOR_DEFINITION_ID, actorDefinitionId)
        .set(ACTOR_DEFINITION_WORKSPACE_GRANT.WORKSPACE_ID, workspaceId)
        .execute();
  }

  public boolean actorDefinitionWorkspaceGrantExists(final UUID actorDefinitionId, final UUID workspaceId) throws IOException {
    final Integer count = database.query(ctx -> ctx.fetchCount(
        DSL.selectFrom(ACTOR_DEFINITION_WORKSPACE_GRANT)
            .where(ACTOR_DEFINITION_WORKSPACE_GRANT.ACTOR_DEFINITION_ID.eq(actorDefinitionId))
            .and(ACTOR_DEFINITION_WORKSPACE_GRANT.WORKSPACE_ID.eq(workspaceId))));
    return count == 1;
  }

  public void deleteActorDefinitionWorkspaceGrant(final UUID actorDefinitionId, final UUID workspaceId) throws IOException {
    database.query(ctx -> ctx.deleteFrom(ACTOR_DEFINITION_WORKSPACE_GRANT)
        .where(ACTOR_DEFINITION_WORKSPACE_GRANT.ACTOR_DEFINITION_ID.eq(actorDefinitionId))
        .and(ACTOR_DEFINITION_WORKSPACE_GRANT.WORKSPACE_ID.eq(workspaceId))
        .execute());
  }

  public boolean workspaceCanUseDefinition(final UUID actorDefinitionId, final UUID workspaceId)
      throws IOException {
    final Result<Record> records = actorDefinitionsJoinedWithGrants(
        workspaceId,
        JoinType.LEFT_OUTER_JOIN,
        ACTOR_DEFINITION.ID.eq(actorDefinitionId),
        ACTOR_DEFINITION.PUBLIC.eq(true).or(ACTOR_DEFINITION_WORKSPACE_GRANT.WORKSPACE_ID.eq(workspaceId)));
    return records.isNotEmpty();
  }

  public boolean workspaceCanUseCustomDefinition(final UUID actorDefinitionId, final UUID workspaceId)
      throws IOException {
    final Result<Record> records = actorDefinitionsJoinedWithGrants(
        workspaceId,
        JoinType.JOIN,
        ACTOR_DEFINITION.ID.eq(actorDefinitionId),
        ACTOR_DEFINITION.CUSTOM.eq(true));
    return records.isNotEmpty();
  }

  private <T> List<T> listStandardActorDefinitions(final ActorType actorType,
                                                   final Function<Record, T> recordToActorDefinition,
                                                   final Condition... conditions)
      throws IOException {
    final Result<Record> records = database.query(ctx -> ctx.select(asterisk()).from(ACTOR_DEFINITION)
        .where(conditions)
        .and(ACTOR_DEFINITION.ACTOR_TYPE.eq(actorType))
        .fetch());

    return records.stream()
        .map(recordToActorDefinition)
        .toList();
  }

  private <T> List<T> listActorDefinitionsJoinedWithGrants(final UUID workspaceId,
                                                           final JoinType joinType,
                                                           final ActorType actorType,
                                                           final Function<Record, T> recordToReturnType,
                                                           final Condition... conditions)
      throws IOException {
    final Result<Record> records = actorDefinitionsJoinedWithGrants(
        workspaceId,
        joinType,
        ArrayUtils.addAll(conditions,
            ACTOR_DEFINITION.ACTOR_TYPE.eq(actorType),
            ACTOR_DEFINITION.PUBLIC.eq(false)));

    return records.stream()
        .map(recordToReturnType)
        .toList();
  }

  private <T> Entry<T, Boolean> actorDefinitionWithGrantStatus(final Record outerJoinRecord,
                                                               final Function<Record, T> recordToActorDefinition) {
    final T actorDefinition = recordToActorDefinition.apply(outerJoinRecord);
    final boolean granted = outerJoinRecord.get(ACTOR_DEFINITION_WORKSPACE_GRANT.WORKSPACE_ID) != null;
    return Map.entry(actorDefinition, granted);
  }

  private Result<Record> actorDefinitionsJoinedWithGrants(final UUID workspaceId,
                                                          final JoinType joinType,
                                                          final Condition... conditions)
      throws IOException {
    return database.query(ctx -> ctx.select(asterisk()).from(ACTOR_DEFINITION)
        .join(ACTOR_DEFINITION_WORKSPACE_GRANT, joinType)
        .on(ACTOR_DEFINITION.ID.eq(ACTOR_DEFINITION_WORKSPACE_GRANT.ACTOR_DEFINITION_ID),
            ACTOR_DEFINITION_WORKSPACE_GRANT.WORKSPACE_ID.eq(workspaceId))
        .where(conditions)
        .fetch());
  }

  private Stream<SourceConnection> listSourceQuery(final Optional<UUID> configId) throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(ACTOR);
      if (configId.isPresent()) {
        return query.where(ACTOR.ACTOR_TYPE.eq(ActorType.source), ACTOR.ID.eq(configId.get())).fetch();
      }
      return query.where(ACTOR.ACTOR_TYPE.eq(ActorType.source)).fetch();
    });

    return result.map(DbConverter::buildSourceConnection).stream();
  }

  /**
   * Returns source with a given id. Does not contain secrets. To hydrate with secrets see { @link
   * SecretsRepositoryReader#getSourceConnectionWithSecrets(final UUID sourceId) }.
   *
   * @param sourceId - id of source to fetch.
   * @return sources
   * @throws JsonValidationException - throws if returned sources are invalid
   * @throws IOException - you never know when you IO
   * @throws ConfigNotFoundException - throws if no source with that id can be found.
   */
  public SourceConnection getSourceConnection(final UUID sourceId) throws JsonValidationException, ConfigNotFoundException, IOException {
    return listSourceQuery(Optional.of(sourceId))
        .findFirst()
        .orElseThrow(() -> new ConfigNotFoundException(ConfigSchema.SOURCE_CONNECTION, sourceId));
  }

  /**
   * MUST NOT ACCEPT SECRETS - Should only be called from { @link SecretsRepositoryWriter }
   *
   * Write a SourceConnection to the database. The configuration of the Source will be a partial
   * configuration (no secrets, just pointer to the secrets store).
   *
   * @param partialSource - The configuration of the Source will be a partial configuration (no
   *        secrets, just pointer to the secrets store)
   * @throws IOException - you never know when you IO
   */
  public void writeSourceConnectionNoSecrets(final SourceConnection partialSource) throws IOException {
    database.transaction(ctx -> {
      writeSourceConnection(Collections.singletonList(partialSource), ctx);
      return null;
    });
  }

  private void writeSourceConnection(final List<SourceConnection> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((sourceConnection) -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(ACTOR)
          .where(ACTOR.ID.eq(sourceConnection.getSourceId())));

      if (isExistingConfig) {
        ctx.update(ACTOR)
            .set(ACTOR.ID, sourceConnection.getSourceId())
            .set(ACTOR.WORKSPACE_ID, sourceConnection.getWorkspaceId())
            .set(ACTOR.ACTOR_DEFINITION_ID, sourceConnection.getSourceDefinitionId())
            .set(ACTOR.NAME, sourceConnection.getName())
            .set(ACTOR.CONFIGURATION, JSONB.valueOf(Jsons.serialize(sourceConnection.getConfiguration())))
            .set(ACTOR.ACTOR_TYPE, ActorType.source)
            .set(ACTOR.TOMBSTONE, sourceConnection.getTombstone() != null && sourceConnection.getTombstone())
            .set(ACTOR.UPDATED_AT, timestamp)
            .where(ACTOR.ID.eq(sourceConnection.getSourceId()))
            .execute();
      } else {
        ctx.insertInto(ACTOR)
            .set(ACTOR.ID, sourceConnection.getSourceId())
            .set(ACTOR.WORKSPACE_ID, sourceConnection.getWorkspaceId())
            .set(ACTOR.ACTOR_DEFINITION_ID, sourceConnection.getSourceDefinitionId())
            .set(ACTOR.NAME, sourceConnection.getName())
            .set(ACTOR.CONFIGURATION, JSONB.valueOf(Jsons.serialize(sourceConnection.getConfiguration())))
            .set(ACTOR.ACTOR_TYPE, ActorType.source)
            .set(ACTOR.TOMBSTONE, sourceConnection.getTombstone() != null && sourceConnection.getTombstone())
            .set(ACTOR.CREATED_AT, timestamp)
            .set(ACTOR.UPDATED_AT, timestamp)
            .execute();
      }
    });
  }

  public boolean deleteSource(final UUID sourceId) throws JsonValidationException, ConfigNotFoundException, IOException {
    return deleteById(ACTOR, sourceId);
  }

  /**
   * Returns all sources in the database. Does not contain secrets. To hydrate with secrets see
   * { @link SecretsRepositoryReader#listSourceConnectionWithSecrets() }.
   *
   * @return sources
   * @throws IOException - you never know when you IO
   */
  public List<SourceConnection> listSourceConnection() throws IOException {
    return listSourceQuery(Optional.empty()).toList();
  }

  /**
   * Returns all sources for a workspace. Does not contain secrets.
   *
   * @param workspaceId - id of the workspace
   * @return sources
   * @throws IOException - you never know when you IO
   */
  public List<SourceConnection> listWorkspaceSourceConnection(final UUID workspaceId) throws IOException {
    final Result<Record> result = database.query(ctx -> ctx.select(asterisk())
        .from(ACTOR)
        .where(ACTOR.ACTOR_TYPE.eq(ActorType.source))
        .and(ACTOR.WORKSPACE_ID.eq(workspaceId))
        .andNot(ACTOR.TOMBSTONE).fetch());
    return result.stream().map(DbConverter::buildSourceConnection).collect(Collectors.toList());
  }

  private Stream<DestinationConnection> listDestinationQuery(final Optional<UUID> configId) throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(ACTOR);
      if (configId.isPresent()) {
        return query.where(ACTOR.ACTOR_TYPE.eq(ActorType.destination), ACTOR.ID.eq(configId.get())).fetch();
      }
      return query.where(ACTOR.ACTOR_TYPE.eq(ActorType.destination)).fetch();
    });

    return result.map(DbConverter::buildDestinationConnection).stream();
  }

  /**
   * Returns destination with a given id. Does not contain secrets. To hydrate with secrets see
   * { @link SecretsRepositoryReader#getDestinationConnectionWithSecrets(final UUID destinationId) }.
   *
   * @param destinationId - id of destination to fetch.
   * @return destinations
   * @throws JsonValidationException - throws if returned destinations are invalid
   * @throws IOException - you never know when you IO
   * @throws ConfigNotFoundException - throws if no destination with that id can be found.
   */
  public DestinationConnection getDestinationConnection(final UUID destinationId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return listDestinationQuery(Optional.of(destinationId))
        .findFirst()
        .orElseThrow(() -> new ConfigNotFoundException(ConfigSchema.DESTINATION_CONNECTION, destinationId));
  }

  /**
   * MUST NOT ACCEPT SECRETS - Should only be called from { @link SecretsRepositoryWriter }
   *
   * Write a DestinationConnection to the database. The configuration of the Destination will be a
   * partial configuration (no secrets, just pointer to the secrets store).
   *
   * @param partialDestination - The configuration of the Destination will be a partial configuration
   *        (no secrets, just pointer to the secrets store)
   * @throws IOException - you never know when you IO
   */
  public void writeDestinationConnectionNoSecrets(final DestinationConnection partialDestination) throws IOException {
    database.transaction(ctx -> {
      writeDestinationConnection(Collections.singletonList(partialDestination), ctx);
      return null;
    });
  }

  private void writeDestinationConnection(final List<DestinationConnection> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((destinationConnection) -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(ACTOR)
          .where(ACTOR.ID.eq(destinationConnection.getDestinationId())));

      if (isExistingConfig) {
        ctx.update(ACTOR)
            .set(ACTOR.ID, destinationConnection.getDestinationId())
            .set(ACTOR.WORKSPACE_ID, destinationConnection.getWorkspaceId())
            .set(ACTOR.ACTOR_DEFINITION_ID, destinationConnection.getDestinationDefinitionId())
            .set(ACTOR.NAME, destinationConnection.getName())
            .set(ACTOR.CONFIGURATION, JSONB.valueOf(Jsons.serialize(destinationConnection.getConfiguration())))
            .set(ACTOR.ACTOR_TYPE, ActorType.destination)
            .set(ACTOR.TOMBSTONE, destinationConnection.getTombstone() != null && destinationConnection.getTombstone())
            .set(ACTOR.UPDATED_AT, timestamp)
            .where(ACTOR.ID.eq(destinationConnection.getDestinationId()))
            .execute();

      } else {
        ctx.insertInto(ACTOR)
            .set(ACTOR.ID, destinationConnection.getDestinationId())
            .set(ACTOR.WORKSPACE_ID, destinationConnection.getWorkspaceId())
            .set(ACTOR.ACTOR_DEFINITION_ID, destinationConnection.getDestinationDefinitionId())
            .set(ACTOR.NAME, destinationConnection.getName())
            .set(ACTOR.CONFIGURATION, JSONB.valueOf(Jsons.serialize(destinationConnection.getConfiguration())))
            .set(ACTOR.ACTOR_TYPE, ActorType.destination)
            .set(ACTOR.TOMBSTONE, destinationConnection.getTombstone() != null && destinationConnection.getTombstone())
            .set(ACTOR.CREATED_AT, timestamp)
            .set(ACTOR.UPDATED_AT, timestamp)
            .execute();
      }
    });
  }

  /**
   * Returns all destinations in the database. Does not contain secrets. To hydrate with secrets see
   * { @link SecretsRepositoryReader#listDestinationConnectionWithSecrets() }.
   *
   * @return destinations
   * @throws IOException - you never know when you IO
   */
  public List<DestinationConnection> listDestinationConnection() throws IOException {
    return listDestinationQuery(Optional.empty()).toList();
  }

  /**
   * Returns all destinations for a workspace. Does not contain secrets.
   *
   * @param workspaceId - id of the workspace
   * @return destinations
   * @throws IOException - you never know when you IO
   */
  public List<DestinationConnection> listWorkspaceDestinationConnection(final UUID workspaceId) throws IOException {
    final Result<Record> result = database.query(ctx -> ctx.select(asterisk())
        .from(ACTOR)
        .where(ACTOR.ACTOR_TYPE.eq(ActorType.destination))
        .and(ACTOR.WORKSPACE_ID.eq(workspaceId))
        .andNot(ACTOR.TOMBSTONE).fetch());
    return result.stream().map(DbConverter::buildDestinationConnection).collect(Collectors.toList());
  }

  /**
   * List workspace IDs with most recently running jobs within a given time window (in hours).
   *
   * @param timeWindowInHours - integer, e.g. 24, 48, etc
   * @return List<UUID> - list of workspace IDs
   * @throws IOException - failed to query data
   */
  public List<UUID> listWorkspacesByMostRecentlyRunningJobs(final int timeWindowInHours) throws IOException {
    final Result<Record1<UUID>> records = database.query(ctx -> ctx.selectDistinct(ACTOR.WORKSPACE_ID)
        .from(ACTOR)
        .join(CONNECTION)
        .on(CONNECTION.SOURCE_ID.eq(ACTOR.ID))
        .join(JOBS)
        .on(CONNECTION.ID.cast(VARCHAR(255)).eq(JOBS.SCOPE))
        .where(JOBS.UPDATED_AT.greaterOrEqual(OffsetDateTime.now().minusHours(timeWindowInHours)))
        .fetch());
    return records.stream().map(record -> record.get(ACTOR.WORKSPACE_ID)).collect(Collectors.toList());
  }

  /**
   * Returns all active sources using a definition
   *
   * @param definitionId - id for the definition
   * @return sources
   * @throws IOException - exception while interacting with the db
   */
  public List<SourceConnection> listSourcesForDefinition(final UUID definitionId) throws IOException {
    final Result<Record> result = database.query(ctx -> ctx.select(asterisk())
        .from(ACTOR)
        .where(ACTOR.ACTOR_TYPE.eq(ActorType.source))
        .and(ACTOR.ACTOR_DEFINITION_ID.eq(definitionId))
        .andNot(ACTOR.TOMBSTONE).fetch());
    return result.stream().map(DbConverter::buildSourceConnection).collect(Collectors.toList());
  }

  /**
   * Returns all active destinations using a definition
   *
   * @param definitionId - id for the definition
   * @return destinations
   * @throws IOException - exception while interacting with the db
   */
  public List<DestinationConnection> listDestinationsForDefinition(final UUID definitionId) throws IOException {
    final Result<Record> result = database.query(ctx -> ctx.select(asterisk())
        .from(ACTOR)
        .where(ACTOR.ACTOR_TYPE.eq(ActorType.destination))
        .and(ACTOR.ACTOR_DEFINITION_ID.eq(definitionId))
        .andNot(ACTOR.TOMBSTONE).fetch());
    return result.stream().map(DbConverter::buildDestinationConnection).collect(Collectors.toList());
  }

  public StandardSync getStandardSync(final UUID connectionId) throws JsonValidationException, IOException, ConfigNotFoundException {
    return standardSyncPersistence.getStandardSync(connectionId);
  }

  public void writeStandardSync(final StandardSync standardSync) throws IOException {
    standardSyncPersistence.writeStandardSync(standardSync);
  }

  /**
   * For the StandardSyncs related to actorDefinitionId, clear the unsupported protocol version flag
   * if both connectors are now within support range.
   *
   * @param actorDefinitionId the actorDefinitionId to query
   * @param actorType the ActorType of actorDefinitionId
   * @param supportedRange the supported range of protocol versions
   */
  // We have conflicting imports here, ActorType is imported from jooq for most internal uses. Since
  // this is a public method, we should be using the ActorType from airbyte-config.
  public void clearUnsupportedProtocolVersionFlag(final UUID actorDefinitionId,
                                                  final io.airbyte.config.ActorType actorType,
                                                  final AirbyteProtocolVersionRange supportedRange)
      throws IOException {
    standardSyncPersistence.clearUnsupportedProtocolVersionFlag(actorDefinitionId, actorType, supportedRange);
  }

  public List<StandardSync> listStandardSyncs() throws IOException {
    return standardSyncPersistence.listStandardSync();
  }

  public List<StandardSync> listStandardSyncsUsingOperation(final UUID operationId)
      throws IOException {

    final Result<Record> connectionAndOperationIdsResult = database.query(ctx -> ctx
        // SELECT connection.* plus the connection's associated operationIds as a concatenated list
        .select(
            CONNECTION.asterisk(),
            groupConcat(CONNECTION_OPERATION.OPERATION_ID).separator(OPERATION_IDS_AGG_DELIMITER).as(OPERATION_IDS_AGG_FIELD))
        .from(CONNECTION)

        // inner join with all connection_operation rows that match the connection's id
        .join(CONNECTION_OPERATION).on(CONNECTION_OPERATION.CONNECTION_ID.eq(CONNECTION.ID))

        // only keep rows for connections that have an operationId that matches the input.
        // needs to be a sub query because we want to keep all operationIds for matching connections
        // in the main query
        .where(CONNECTION.ID.in(
            select(CONNECTION.ID).from(CONNECTION).join(CONNECTION_OPERATION).on(CONNECTION_OPERATION.CONNECTION_ID.eq(CONNECTION.ID))
                .where(CONNECTION_OPERATION.OPERATION_ID.eq(operationId))))

        // group by connection.id so that the groupConcat above works
        .groupBy(CONNECTION.ID)).fetch();

    return getStandardSyncsFromResult(connectionAndOperationIdsResult);
  }

  public List<StandardSync> listWorkspaceStandardSyncs(final UUID workspaceId, final boolean includeDeleted) throws IOException {
    return listWorkspaceStandardSyncs(new StandardSyncQuery(workspaceId, null, null, includeDeleted));
  }

  public List<StandardSync> listWorkspaceStandardSyncs(final StandardSyncQuery standardSyncQuery) throws IOException {
    final Result<Record> connectionAndOperationIdsResult = database.query(ctx -> ctx
        // SELECT connection.* plus the connection's associated operationIds as a concatenated list
        .select(
            CONNECTION.asterisk(),
            groupConcat(CONNECTION_OPERATION.OPERATION_ID).separator(OPERATION_IDS_AGG_DELIMITER).as(OPERATION_IDS_AGG_FIELD))
        .from(CONNECTION)

        // left join with all connection_operation rows that match the connection's id.
        // left join includes connections that don't have any connection_operations
        .leftJoin(CONNECTION_OPERATION).on(CONNECTION_OPERATION.CONNECTION_ID.eq(CONNECTION.ID))

        // join with source actors so that we can filter by workspaceId
        .join(ACTOR).on(CONNECTION.SOURCE_ID.eq(ACTOR.ID))
        .where(ACTOR.WORKSPACE_ID.eq(standardSyncQuery.workspaceId)
            .and(standardSyncQuery.destinationId == null || standardSyncQuery.destinationId.isEmpty() ? noCondition()
                : CONNECTION.DESTINATION_ID.in(standardSyncQuery.destinationId))
            .and(standardSyncQuery.sourceId == null || standardSyncQuery.sourceId.isEmpty() ? noCondition()
                : CONNECTION.SOURCE_ID.in(standardSyncQuery.sourceId))
            .and(standardSyncQuery.includeDeleted ? noCondition() : CONNECTION.STATUS.notEqual(StatusType.deprecated)))

        // group by connection.id so that the groupConcat above works
        .groupBy(CONNECTION.ID)).fetch();

    return getStandardSyncsFromResult(connectionAndOperationIdsResult);
  }

  public List<StandardSync> listConnectionsBySource(final UUID sourceId, final boolean includeDeleted) throws IOException {
    final Result<Record> connectionAndOperationIdsResult = database.query(ctx -> ctx
        .select(
            CONNECTION.asterisk(),
            groupConcat(CONNECTION_OPERATION.OPERATION_ID).separator(OPERATION_IDS_AGG_DELIMITER).as(OPERATION_IDS_AGG_FIELD))
        .from(CONNECTION)
        .leftJoin(CONNECTION_OPERATION).on(CONNECTION_OPERATION.CONNECTION_ID.eq(CONNECTION.ID))
        .where(CONNECTION.SOURCE_ID.eq(sourceId)
            .and(includeDeleted ? noCondition() : CONNECTION.STATUS.notEqual(StatusType.deprecated)))
        .groupBy(CONNECTION.ID)).fetch();

    return getStandardSyncsFromResult(connectionAndOperationIdsResult);
  }

  private List<StandardSync> getStandardSyncsFromResult(final Result<Record> connectionAndOperationIdsResult) {
    final List<StandardSync> standardSyncs = new ArrayList<>();

    for (final Record record : connectionAndOperationIdsResult) {
      final String operationIdsFromRecord = record.get(OPERATION_IDS_AGG_FIELD, String.class);

      // can be null when connection has no connectionOperations
      final List<UUID> operationIds = operationIdsFromRecord == null
          ? Collections.emptyList()
          : Arrays.stream(operationIdsFromRecord.split(OPERATION_IDS_AGG_DELIMITER)).map(UUID::fromString).toList();

      standardSyncs.add(DbConverter.buildStandardSync(record, operationIds));
    }

    return standardSyncs;
  }

  private Stream<StandardSyncOperation> listStandardSyncOperationQuery(final Optional<UUID> configId) throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(OPERATION);
      if (configId.isPresent()) {
        return query.where(OPERATION.ID.eq(configId.get())).fetch();
      }
      return query.fetch();
    });

    return result.map(ConfigRepository::buildStandardSyncOperation).stream();
  }

  private static StandardSyncOperation buildStandardSyncOperation(final Record record) {
    return new StandardSyncOperation()
        .withOperationId(record.get(OPERATION.ID))
        .withName(record.get(OPERATION.NAME))
        .withWorkspaceId(record.get(OPERATION.WORKSPACE_ID))
        .withOperatorType(Enums.toEnum(record.get(OPERATION.OPERATOR_TYPE, String.class), OperatorType.class).orElseThrow())
        .withOperatorNormalization(Jsons.deserialize(record.get(OPERATION.OPERATOR_NORMALIZATION).data(), OperatorNormalization.class))
        .withOperatorDbt(Jsons.deserialize(record.get(OPERATION.OPERATOR_DBT).data(), OperatorDbt.class))
        .withOperatorWebhook(record.get(OPERATION.OPERATOR_WEBHOOK) == null ? null
            : Jsons.deserialize(record.get(OPERATION.OPERATOR_WEBHOOK).data(), OperatorWebhook.class))
        .withTombstone(record.get(OPERATION.TOMBSTONE));
  }

  public StandardSyncOperation getStandardSyncOperation(final UUID operationId) throws JsonValidationException, IOException, ConfigNotFoundException {
    return listStandardSyncOperationQuery(Optional.of(operationId))
        .findFirst()
        .orElseThrow(() -> new ConfigNotFoundException(ConfigSchema.STANDARD_SYNC_OPERATION, operationId));
  }

  public void writeStandardSyncOperation(final StandardSyncOperation standardSyncOperation) throws IOException {
    database.transaction(ctx -> {
      writeStandardSyncOperation(Collections.singletonList(standardSyncOperation), ctx);
      return null;
    });
  }

  private void writeStandardSyncOperation(final List<StandardSyncOperation> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((standardSyncOperation) -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(OPERATION)
          .where(OPERATION.ID.eq(standardSyncOperation.getOperationId())));

      if (isExistingConfig) {
        ctx.update(OPERATION)
            .set(OPERATION.ID, standardSyncOperation.getOperationId())
            .set(OPERATION.WORKSPACE_ID, standardSyncOperation.getWorkspaceId())
            .set(OPERATION.NAME, standardSyncOperation.getName())
            .set(OPERATION.OPERATOR_TYPE, Enums.toEnum(standardSyncOperation.getOperatorType().value(),
                io.airbyte.db.instance.configs.jooq.generated.enums.OperatorType.class).orElseThrow())
            .set(OPERATION.OPERATOR_NORMALIZATION, JSONB.valueOf(Jsons.serialize(standardSyncOperation.getOperatorNormalization())))
            .set(OPERATION.OPERATOR_DBT, JSONB.valueOf(Jsons.serialize(standardSyncOperation.getOperatorDbt())))
            .set(OPERATION.OPERATOR_WEBHOOK, JSONB.valueOf(Jsons.serialize(standardSyncOperation.getOperatorWebhook())))
            .set(OPERATION.TOMBSTONE, standardSyncOperation.getTombstone() != null && standardSyncOperation.getTombstone())
            .set(OPERATION.UPDATED_AT, timestamp)
            .where(OPERATION.ID.eq(standardSyncOperation.getOperationId()))
            .execute();

      } else {
        ctx.insertInto(OPERATION)
            .set(OPERATION.ID, standardSyncOperation.getOperationId())
            .set(OPERATION.WORKSPACE_ID, standardSyncOperation.getWorkspaceId())
            .set(OPERATION.NAME, standardSyncOperation.getName())
            .set(OPERATION.OPERATOR_TYPE, Enums.toEnum(standardSyncOperation.getOperatorType().value(),
                io.airbyte.db.instance.configs.jooq.generated.enums.OperatorType.class).orElseThrow())
            .set(OPERATION.OPERATOR_NORMALIZATION, JSONB.valueOf(Jsons.serialize(standardSyncOperation.getOperatorNormalization())))
            .set(OPERATION.OPERATOR_DBT, JSONB.valueOf(Jsons.serialize(standardSyncOperation.getOperatorDbt())))
            .set(OPERATION.OPERATOR_WEBHOOK, JSONB.valueOf(Jsons.serialize(standardSyncOperation.getOperatorWebhook())))
            .set(OPERATION.TOMBSTONE, standardSyncOperation.getTombstone() != null && standardSyncOperation.getTombstone())
            .set(OPERATION.CREATED_AT, timestamp)
            .set(OPERATION.UPDATED_AT, timestamp)
            .execute();
      }
    });
  }

  public List<StandardSyncOperation> listStandardSyncOperations() throws IOException, JsonValidationException {
    return listStandardSyncOperationQuery(Optional.empty()).toList();
  }

  /**
   * Updates {@link io.airbyte.db.instance.configs.jooq.generated.tables.ConnectionOperation} records
   * for the given {@code connectionId}.
   *
   * @param connectionId ID of the associated connection to update operations for
   * @param newOperationIds Set of all operationIds that should be associated to the connection
   * @throws IOException - exception while interacting with the db
   */
  public void updateConnectionOperationIds(final UUID connectionId, final Set<UUID> newOperationIds) throws IOException {
    database.transaction(ctx -> {
      final Set<UUID> existingOperationIds = ctx
          .selectFrom(CONNECTION_OPERATION)
          .where(CONNECTION_OPERATION.CONNECTION_ID.eq(connectionId))
          .fetchSet(CONNECTION_OPERATION.OPERATION_ID);

      final Set<UUID> existingOperationIdsToKeep = Sets.intersection(existingOperationIds, newOperationIds);

      // DELETE existing connection_operation records that aren't in the input list
      final Set<UUID> operationIdsToDelete = Sets.difference(existingOperationIds, existingOperationIdsToKeep);

      ctx.deleteFrom(CONNECTION_OPERATION)
          .where(CONNECTION_OPERATION.CONNECTION_ID.eq(connectionId))
          .and(CONNECTION_OPERATION.OPERATION_ID.in(operationIdsToDelete))
          .execute();

      // INSERT connection_operation records that are in the input list and don't yet exist
      final Set<UUID> operationIdsToAdd = Sets.difference(newOperationIds, existingOperationIdsToKeep);

      operationIdsToAdd.forEach(operationId -> ctx
          .insertInto(CONNECTION_OPERATION)
          .columns(CONNECTION_OPERATION.ID, CONNECTION_OPERATION.CONNECTION_ID, CONNECTION_OPERATION.OPERATION_ID)
          .values(UUID.randomUUID(), connectionId, operationId)
          .execute());

      return null;
    });
  }

  public void deleteStandardSyncOperation(final UUID standardSyncOperationId) throws IOException {
    database.transaction(ctx -> {
      ctx.deleteFrom(CONNECTION_OPERATION)
          .where(CONNECTION_OPERATION.OPERATION_ID.eq(standardSyncOperationId)).execute();
      ctx.update(OPERATION)
          .set(OPERATION.TOMBSTONE, true)
          .where(OPERATION.ID.eq(standardSyncOperationId)).execute();
      return null;
    });
  }

  private Stream<SourceOAuthParameter> listSourceOauthParamQuery(final Optional<UUID> configId) throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(ACTOR_OAUTH_PARAMETER);
      if (configId.isPresent()) {
        return query.where(ACTOR_OAUTH_PARAMETER.ACTOR_TYPE.eq(ActorType.source), ACTOR_OAUTH_PARAMETER.ID.eq(configId.get())).fetch();
      }
      return query.where(ACTOR_OAUTH_PARAMETER.ACTOR_TYPE.eq(ActorType.source)).fetch();
    });

    return result.map(DbConverter::buildSourceOAuthParameter).stream();
  }

  public Optional<SourceOAuthParameter> getSourceOAuthParamByDefinitionIdOptional(final UUID workspaceId, final UUID sourceDefinitionId)
      throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(ACTOR_OAUTH_PARAMETER);
      return query.where(ACTOR_OAUTH_PARAMETER.ACTOR_TYPE.eq(ActorType.source),
          ACTOR_OAUTH_PARAMETER.WORKSPACE_ID.eq(workspaceId),
          ACTOR_OAUTH_PARAMETER.ACTOR_DEFINITION_ID.eq(sourceDefinitionId)).fetch();
    });

    return result.stream().findFirst().map(DbConverter::buildSourceOAuthParameter);
  }

  public void writeSourceOAuthParam(final SourceOAuthParameter sourceOAuthParameter) throws IOException {
    database.transaction(ctx -> {
      writeSourceOauthParameter(Collections.singletonList(sourceOAuthParameter), ctx);
      return null;
    });
  }

  private void writeSourceOauthParameter(final List<SourceOAuthParameter> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((sourceOAuthParameter) -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(ACTOR_OAUTH_PARAMETER)
          .where(ACTOR_OAUTH_PARAMETER.ID.eq(sourceOAuthParameter.getOauthParameterId())));

      if (isExistingConfig) {
        ctx.update(ACTOR_OAUTH_PARAMETER)
            .set(ACTOR_OAUTH_PARAMETER.ID, sourceOAuthParameter.getOauthParameterId())
            .set(ACTOR_OAUTH_PARAMETER.WORKSPACE_ID, sourceOAuthParameter.getWorkspaceId())
            .set(ACTOR_OAUTH_PARAMETER.ACTOR_DEFINITION_ID, sourceOAuthParameter.getSourceDefinitionId())
            .set(ACTOR_OAUTH_PARAMETER.CONFIGURATION, JSONB.valueOf(Jsons.serialize(sourceOAuthParameter.getConfiguration())))
            .set(ACTOR_OAUTH_PARAMETER.ACTOR_TYPE, ActorType.source)
            .set(ACTOR_OAUTH_PARAMETER.UPDATED_AT, timestamp)
            .where(ACTOR_OAUTH_PARAMETER.ID.eq(sourceOAuthParameter.getOauthParameterId()))
            .execute();
      } else {
        ctx.insertInto(ACTOR_OAUTH_PARAMETER)
            .set(ACTOR_OAUTH_PARAMETER.ID, sourceOAuthParameter.getOauthParameterId())
            .set(ACTOR_OAUTH_PARAMETER.WORKSPACE_ID, sourceOAuthParameter.getWorkspaceId())
            .set(ACTOR_OAUTH_PARAMETER.ACTOR_DEFINITION_ID, sourceOAuthParameter.getSourceDefinitionId())
            .set(ACTOR_OAUTH_PARAMETER.CONFIGURATION, JSONB.valueOf(Jsons.serialize(sourceOAuthParameter.getConfiguration())))
            .set(ACTOR_OAUTH_PARAMETER.ACTOR_TYPE, ActorType.source)
            .set(ACTOR_OAUTH_PARAMETER.CREATED_AT, timestamp)
            .set(ACTOR_OAUTH_PARAMETER.UPDATED_AT, timestamp)
            .execute();
      }
    });
  }

  public List<SourceOAuthParameter> listSourceOAuthParam() throws JsonValidationException, IOException {
    return listSourceOauthParamQuery(Optional.empty()).toList();
  }

  private Stream<DestinationOAuthParameter> listDestinationOauthParamQuery(final Optional<UUID> configId)
      throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(ACTOR_OAUTH_PARAMETER);
      if (configId.isPresent()) {
        return query.where(ACTOR_OAUTH_PARAMETER.ACTOR_TYPE.eq(ActorType.destination), ACTOR_OAUTH_PARAMETER.ID.eq(configId.get())).fetch();
      }
      return query.where(ACTOR_OAUTH_PARAMETER.ACTOR_TYPE.eq(ActorType.destination)).fetch();
    });

    return result.map(DbConverter::buildDestinationOAuthParameter).stream();
  }

  public Optional<DestinationOAuthParameter> getDestinationOAuthParamByDefinitionIdOptional(final UUID workspaceId,
                                                                                            final UUID destinationDefinitionId)
      throws IOException {
    final Result<Record> result = database.query(ctx -> {
      final SelectJoinStep<Record> query = ctx.select(asterisk()).from(ACTOR_OAUTH_PARAMETER);
      return query.where(ACTOR_OAUTH_PARAMETER.ACTOR_TYPE.eq(ActorType.destination),
          ACTOR_OAUTH_PARAMETER.WORKSPACE_ID.eq(workspaceId),
          ACTOR_OAUTH_PARAMETER.ACTOR_DEFINITION_ID.eq(destinationDefinitionId)).fetch();
    });

    return result.stream().findFirst().map(DbConverter::buildDestinationOAuthParameter);
  }

  public void writeDestinationOAuthParam(final DestinationOAuthParameter destinationOAuthParameter) throws IOException {
    database.transaction(ctx -> {
      writeDestinationOauthParameter(Collections.singletonList(destinationOAuthParameter), ctx);
      return null;
    });
  }

  private void writeDestinationOauthParameter(final List<DestinationOAuthParameter> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((destinationOAuthParameter) -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(ACTOR_OAUTH_PARAMETER)
          .where(ACTOR_OAUTH_PARAMETER.ID.eq(destinationOAuthParameter.getOauthParameterId())));

      if (isExistingConfig) {
        ctx.update(ACTOR_OAUTH_PARAMETER)
            .set(ACTOR_OAUTH_PARAMETER.ID, destinationOAuthParameter.getOauthParameterId())
            .set(ACTOR_OAUTH_PARAMETER.WORKSPACE_ID, destinationOAuthParameter.getWorkspaceId())
            .set(ACTOR_OAUTH_PARAMETER.ACTOR_DEFINITION_ID, destinationOAuthParameter.getDestinationDefinitionId())
            .set(ACTOR_OAUTH_PARAMETER.CONFIGURATION, JSONB.valueOf(Jsons.serialize(destinationOAuthParameter.getConfiguration())))
            .set(ACTOR_OAUTH_PARAMETER.ACTOR_TYPE, ActorType.destination)
            .set(ACTOR_OAUTH_PARAMETER.UPDATED_AT, timestamp)
            .where(ACTOR_OAUTH_PARAMETER.ID.eq(destinationOAuthParameter.getOauthParameterId()))
            .execute();

      } else {
        ctx.insertInto(ACTOR_OAUTH_PARAMETER)
            .set(ACTOR_OAUTH_PARAMETER.ID, destinationOAuthParameter.getOauthParameterId())
            .set(ACTOR_OAUTH_PARAMETER.WORKSPACE_ID, destinationOAuthParameter.getWorkspaceId())
            .set(ACTOR_OAUTH_PARAMETER.ACTOR_DEFINITION_ID, destinationOAuthParameter.getDestinationDefinitionId())
            .set(ACTOR_OAUTH_PARAMETER.CONFIGURATION, JSONB.valueOf(Jsons.serialize(destinationOAuthParameter.getConfiguration())))
            .set(ACTOR_OAUTH_PARAMETER.ACTOR_TYPE, ActorType.destination)
            .set(ACTOR_OAUTH_PARAMETER.CREATED_AT, timestamp)
            .set(ACTOR_OAUTH_PARAMETER.UPDATED_AT, timestamp)
            .execute();
      }
    });

  }

  public List<DestinationOAuthParameter> listDestinationOAuthParam() throws JsonValidationException, IOException {
    return listDestinationOauthParamQuery(Optional.empty()).toList();
  }

  private Map<UUID, AirbyteCatalog> findCatalogByHash(final String catalogHash, final DSLContext context) {
    final Result<Record2<UUID, JSONB>> records = context.select(ACTOR_CATALOG.ID, ACTOR_CATALOG.CATALOG)
        .from(ACTOR_CATALOG)
        .where(ACTOR_CATALOG.CATALOG_HASH.eq(catalogHash)).fetch();

    final Map<UUID, AirbyteCatalog> result = new HashMap<>();
    for (final Record record : records) {
      // We do not apply the on-the-fly migration here because the only caller is getOrInsertActorCatalog
      // which is using this to figure out if the catalog has already been inserted. Migrating on the fly
      // here will cause us to add a duplicate each time we check for existence of a catalog.
      final AirbyteCatalog catalog = Jsons.deserialize(record.get(ACTOR_CATALOG.CATALOG).toString(), AirbyteCatalog.class);
      result.put(record.get(ACTOR_CATALOG.ID), catalog);
    }
    return result;
  }

  /**
   * Updates the database with the most up-to-date source and destination definitions in the connector
   * catalog.
   *
   * @param seedSourceDefs - most up-to-date source definitions
   * @param seedDestDefs - most up-to-date destination definitions
   * @throws IOException - throws if exception when interacting with db
   */
  public void seedActorDefinitions(final List<StandardSourceDefinition> seedSourceDefs, final List<StandardDestinationDefinition> seedDestDefs)
      throws IOException {
    actorDefinitionMigrator.migrate(seedSourceDefs, seedDestDefs);
  }

  // Data-carrier records to hold combined result of query for a Source or Destination and its
  // corresponding Definition. This enables the API layer to
  // process combined information about a Source/Destination/Definition pair without requiring two
  // separate queries and in-memory join operation,
  // because the config models are grouped immediately in the repository layer.
  @VisibleForTesting
  public record SourceAndDefinition(SourceConnection source, StandardSourceDefinition definition) {

  }

  @VisibleForTesting
  public record DestinationAndDefinition(DestinationConnection destination, StandardDestinationDefinition definition) {

  }

  public List<SourceAndDefinition> getSourceAndDefinitionsFromSourceIds(final List<UUID> sourceIds) throws IOException {
    final Result<Record> records = database.query(ctx -> ctx
        .select(ACTOR.asterisk(), ACTOR_DEFINITION.asterisk())
        .from(ACTOR)
        .join(ACTOR_DEFINITION)
        .on(ACTOR.ACTOR_DEFINITION_ID.eq(ACTOR_DEFINITION.ID))
        .where(ACTOR.ACTOR_TYPE.eq(ActorType.source), ACTOR.ID.in(sourceIds))
        .fetch());

    final List<SourceAndDefinition> sourceAndDefinitions = new ArrayList<>();

    for (final Record record : records) {
      final SourceConnection source = DbConverter.buildSourceConnection(record);
      final StandardSourceDefinition definition = DbConverter.buildStandardSourceDefinition(record);
      sourceAndDefinitions.add(new SourceAndDefinition(source, definition));
    }

    return sourceAndDefinitions;
  }

  public List<DestinationAndDefinition> getDestinationAndDefinitionsFromDestinationIds(final List<UUID> destinationIds) throws IOException {
    final Result<Record> records = database.query(ctx -> ctx
        .select(ACTOR.asterisk(), ACTOR_DEFINITION.asterisk())
        .from(ACTOR)
        .join(ACTOR_DEFINITION)
        .on(ACTOR.ACTOR_DEFINITION_ID.eq(ACTOR_DEFINITION.ID))
        .where(ACTOR.ACTOR_TYPE.eq(ActorType.destination), ACTOR.ID.in(destinationIds))
        .fetch());

    final List<DestinationAndDefinition> destinationAndDefinitions = new ArrayList<>();

    for (final Record record : records) {
      final DestinationConnection destination = DbConverter.buildDestinationConnection(record);
      final StandardDestinationDefinition definition = DbConverter.buildStandardDestinationDefinition(record);
      destinationAndDefinitions.add(new DestinationAndDefinition(destination, definition));
    }

    return destinationAndDefinitions;
  }

  public ActorCatalog getActorCatalogById(final UUID actorCatalogId)
      throws IOException, ConfigNotFoundException {
    final Result<Record> result = database.query(ctx -> ctx.select(ACTOR_CATALOG.asterisk())
        .from(ACTOR_CATALOG).where(ACTOR_CATALOG.ID.eq(actorCatalogId))).fetch();

    if (result.size() > 0) {
      return DbConverter.buildActorCatalog(result.get(0));
    }
    throw new ConfigNotFoundException(ConfigSchema.ACTOR_CATALOG, actorCatalogId);
  }

  /**
   * Store an Airbyte catalog in DB if it is not present already
   *
   * Checks in the config DB if the catalog is present already, if so returns it identifier. It is not
   * present, it is inserted in DB with a new identifier and that identifier is returned.
   *
   * @param airbyteCatalog An Airbyte catalog to cache
   * @param context - db context
   * @return the db identifier for the cached catalog.
   */
  private UUID getOrInsertActorCatalog(final AirbyteCatalog airbyteCatalog,
                                       final DSLContext context,
                                       final OffsetDateTime timestamp) {
    final HashFunction hashFunction = Hashing.murmur3_32_fixed();
    final String catalogHash = hashFunction.hashBytes(Jsons.serialize(airbyteCatalog).getBytes(
        Charsets.UTF_8)).toString();
    final Map<UUID, AirbyteCatalog> catalogs = findCatalogByHash(catalogHash, context);

    for (final Map.Entry<UUID, AirbyteCatalog> entry : catalogs.entrySet()) {
      if (entry.getValue().equals(airbyteCatalog)) {
        return entry.getKey();
      }
    }

    final UUID catalogId = UUID.randomUUID();
    context.insertInto(ACTOR_CATALOG)
        .set(ACTOR_CATALOG.ID, catalogId)
        .set(ACTOR_CATALOG.CATALOG, JSONB.valueOf(Jsons.serialize(airbyteCatalog)))
        .set(ACTOR_CATALOG.CATALOG_HASH, catalogHash)
        .set(ACTOR_CATALOG.CREATED_AT, timestamp)
        .set(ACTOR_CATALOG.MODIFIED_AT, timestamp).execute();
    return catalogId;
  }

  public Optional<ActorCatalog> getActorCatalog(final UUID actorId,
                                                final String actorVersion,
                                                final String configHash)
      throws IOException {
    final Result<Record> records = database.transaction(ctx -> ctx.select(ACTOR_CATALOG.asterisk())
        .from(ACTOR_CATALOG).join(ACTOR_CATALOG_FETCH_EVENT)
        .on(ACTOR_CATALOG.ID.eq(ACTOR_CATALOG_FETCH_EVENT.ACTOR_CATALOG_ID))
        .where(ACTOR_CATALOG_FETCH_EVENT.ACTOR_ID.eq(actorId))
        .and(ACTOR_CATALOG_FETCH_EVENT.ACTOR_VERSION.eq(actorVersion))
        .and(ACTOR_CATALOG_FETCH_EVENT.CONFIG_HASH.eq(configHash))
        .orderBy(ACTOR_CATALOG_FETCH_EVENT.CREATED_AT.desc()).limit(1)).fetch();

    return records.stream().findFirst().map(DbConverter::buildActorCatalog);
  }

  public Optional<ActorCatalogWithUpdatedAt> getMostRecentSourceActorCatalog(final UUID sourceId) throws IOException {
    final Result<Record> records = database.query(ctx -> ctx.select(ACTOR_CATALOG.asterisk(), ACTOR_CATALOG_FETCH_EVENT.CREATED_AT)
        .from(ACTOR_CATALOG)
        .join(ACTOR_CATALOG_FETCH_EVENT)
        .on(ACTOR_CATALOG_FETCH_EVENT.ACTOR_CATALOG_ID.eq(ACTOR_CATALOG.ID))
        .where(ACTOR_CATALOG_FETCH_EVENT.ACTOR_ID.eq(sourceId))
        .orderBy(ACTOR_CATALOG_FETCH_EVENT.CREATED_AT.desc()).limit(1).fetch());
    return records.stream().findFirst().map(DbConverter::buildActorCatalogWithUpdatedAt);
  }

  public Optional<ActorCatalog> getMostRecentActorCatalogForSource(final UUID sourceId) throws IOException {
    final Result<Record> records = database.query(ctx -> ctx.select(ACTOR_CATALOG.asterisk())
        .from(ACTOR_CATALOG)
        .join(ACTOR_CATALOG_FETCH_EVENT)
        .on(ACTOR_CATALOG_FETCH_EVENT.ACTOR_CATALOG_ID.eq(ACTOR_CATALOG.ID))
        .where(ACTOR_CATALOG_FETCH_EVENT.ACTOR_ID.eq(sourceId))
        .orderBy(ACTOR_CATALOG_FETCH_EVENT.CREATED_AT.desc()).limit(1).fetch());
    return records.stream().findFirst().map(DbConverter::buildActorCatalog);
  }

  public Optional<ActorCatalogFetchEvent> getMostRecentActorCatalogFetchEventForSource(final UUID sourceId) throws IOException {

    final Result<Record> records = database.query(ctx -> ctx.select(ACTOR_CATALOG_FETCH_EVENT.asterisk())
        .from(ACTOR_CATALOG_FETCH_EVENT)
        .where(ACTOR_CATALOG_FETCH_EVENT.ACTOR_ID.eq(sourceId))
        .orderBy(ACTOR_CATALOG_FETCH_EVENT.CREATED_AT.desc()).limit(1).fetch());
    return records.stream().findFirst().map(DbConverter::buildActorCatalogFetchEvent);
  }

  @SuppressWarnings({"unused", "SqlNoDataSourceInspection"})
  public Map<UUID, ActorCatalogFetchEvent> getMostRecentActorCatalogFetchEventForSources(final List<UUID> sourceIds) throws IOException {
    // noinspection SqlResolve
    if (sourceIds.isEmpty()) {
      return Collections.emptyMap();
    }
    return database.query(ctx -> ctx.fetch(
        """
        select distinct actor_catalog_id, actor_id, created_at from
          (select actor_catalog_id, actor_id, created_at, row_number() over (partition by actor_id order by created_at desc) as creation_order_row_number
          from public.actor_catalog_fetch_event
          where actor_id in ({0})
          ) table_with_rank
        where creation_order_row_number = 1;
        """,
        DSL.list(sourceIds.stream().map(DSL::value).collect(Collectors.toList()))))
        .stream().map(DbConverter::buildActorCatalogFetchEvent)
        .collect(Collectors.toMap(ActorCatalogFetchEvent::getActorId, record -> record));
  }

  /**
   * Stores source catalog information.
   *
   * This function is called each time the schema of a source is fetched. This can occur because the
   * source is set up for the first time, because the configuration or version of the connector
   * changed or because the user explicitly requested a schema refresh. Schemas are stored separately
   * and de-duplicated upon insertion. Once a schema has been successfully stored, a call to
   * getActorCatalog(actorId, connectionVersion, configurationHash) will return the most recent schema
   * stored for those parameters.
   *
   * @param catalog - catalog that was fetched.
   * @param actorId - actor the catalog was fetched by
   * @param connectorVersion - version of the connector when catalog was fetched
   * @param configurationHash - hash of the config of the connector when catalog was fetched
   * @return The identifier (UUID) of the fetch event inserted in the database
   * @throws IOException - error while interacting with db
   */
  public UUID writeActorCatalogFetchEvent(final AirbyteCatalog catalog,
                                          final UUID actorId,
                                          final String connectorVersion,
                                          final String configurationHash)
      throws IOException {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    final UUID fetchEventID = UUID.randomUUID();
    return database.transaction(ctx -> {
      final UUID catalogId = getOrInsertActorCatalog(catalog, ctx, timestamp);
      ctx.insertInto(ACTOR_CATALOG_FETCH_EVENT)
          .set(ACTOR_CATALOG_FETCH_EVENT.ID, fetchEventID)
          .set(ACTOR_CATALOG_FETCH_EVENT.ACTOR_ID, actorId)
          .set(ACTOR_CATALOG_FETCH_EVENT.ACTOR_CATALOG_ID, catalogId)
          .set(ACTOR_CATALOG_FETCH_EVENT.CONFIG_HASH, configurationHash)
          .set(ACTOR_CATALOG_FETCH_EVENT.ACTOR_VERSION, connectorVersion)
          .set(ACTOR_CATALOG_FETCH_EVENT.MODIFIED_AT, timestamp)
          .set(ACTOR_CATALOG_FETCH_EVENT.CREATED_AT, timestamp).execute();
      return catalogId;
    });
  }

  public int countConnectionsForWorkspace(final UUID workspaceId) throws IOException {
    return database.query(ctx -> ctx.selectCount()
        .from(CONNECTION)
        .join(ACTOR).on(CONNECTION.SOURCE_ID.eq(ACTOR.ID))
        .where(ACTOR.WORKSPACE_ID.eq(workspaceId))
        .and(CONNECTION.STATUS.notEqual(StatusType.deprecated))
        .andNot(ACTOR.TOMBSTONE)).fetchOne().into(int.class);
  }

  public int countSourcesForWorkspace(final UUID workspaceId) throws IOException {
    return database.query(ctx -> ctx.selectCount()
        .from(ACTOR)
        .where(ACTOR.WORKSPACE_ID.equal(workspaceId))
        .and(ACTOR.ACTOR_TYPE.eq(ActorType.source))
        .andNot(ACTOR.TOMBSTONE)).fetchOne().into(int.class);
  }

  public int countDestinationsForWorkspace(final UUID workspaceId) throws IOException {
    return database.query(ctx -> ctx.selectCount()
        .from(ACTOR)
        .where(ACTOR.WORKSPACE_ID.equal(workspaceId))
        .and(ACTOR.ACTOR_TYPE.eq(ActorType.destination))
        .andNot(ACTOR.TOMBSTONE)).fetchOne().into(int.class);
  }

  /**
   * The following methods are present to allow the JobCreationAndStatusUpdateActivity class to emit
   * metrics without exposing the underlying database connection.
   */

  public List<ReleaseStage> getSrcIdAndDestIdToReleaseStages(final UUID srcId, final UUID dstId) throws IOException {
    return database.query(ctx -> MetricQueries.srcIdAndDestIdToReleaseStages(ctx, srcId, dstId));
  }

  public List<ReleaseStage> getJobIdToReleaseStages(final long jobId) throws IOException {
    return database.query(ctx -> MetricQueries.jobIdToReleaseStages(ctx, jobId));
  }

  private Condition includeTombstones(final Field<Boolean> tombstoneField, final boolean includeTombstones) {
    if (includeTombstones) {
      return DSL.trueCondition();
    } else {
      return tombstoneField.eq(false);
    }
  }

  public WorkspaceServiceAccount getWorkspaceServiceAccountNoSecrets(final UUID workspaceId) throws IOException, ConfigNotFoundException {
    // breaking the pattern of doing a list query, because we never want to list this resource without
    // scoping by workspace id.
    return database.query(ctx -> ctx.select(asterisk()).from(WORKSPACE_SERVICE_ACCOUNT)
        .where(WORKSPACE_SERVICE_ACCOUNT.WORKSPACE_ID.eq(workspaceId))
        .fetch())
        .map(DbConverter::buildWorkspaceServiceAccount)
        .stream()
        .findFirst()
        .orElseThrow(() -> new ConfigNotFoundException(ConfigSchema.WORKSPACE_SERVICE_ACCOUNT, workspaceId));
  }

  public void writeWorkspaceServiceAccountNoSecrets(final WorkspaceServiceAccount workspaceServiceAccount) throws IOException {
    database.transaction(ctx -> {
      writeWorkspaceServiceAccount(Collections.singletonList(workspaceServiceAccount), ctx);
      return null;
    });
  }

  private void writeWorkspaceServiceAccount(final List<WorkspaceServiceAccount> configs, final DSLContext ctx) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    configs.forEach((workspaceServiceAccount) -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(WORKSPACE_SERVICE_ACCOUNT)
          .where(WORKSPACE_SERVICE_ACCOUNT.WORKSPACE_ID.eq(workspaceServiceAccount.getWorkspaceId())));

      if (isExistingConfig) {
        ctx.update(WORKSPACE_SERVICE_ACCOUNT)
            .set(WORKSPACE_SERVICE_ACCOUNT.WORKSPACE_ID, workspaceServiceAccount.getWorkspaceId())
            .set(WORKSPACE_SERVICE_ACCOUNT.SERVICE_ACCOUNT_ID, workspaceServiceAccount.getServiceAccountId())
            .set(WORKSPACE_SERVICE_ACCOUNT.SERVICE_ACCOUNT_EMAIL, workspaceServiceAccount.getServiceAccountEmail())
            .set(WORKSPACE_SERVICE_ACCOUNT.JSON_CREDENTIAL, JSONB.valueOf(Jsons.serialize(workspaceServiceAccount.getJsonCredential())))
            .set(WORKSPACE_SERVICE_ACCOUNT.HMAC_KEY, JSONB.valueOf(Jsons.serialize(workspaceServiceAccount.getHmacKey())))
            .set(WORKSPACE_SERVICE_ACCOUNT.UPDATED_AT, timestamp)
            .where(WORKSPACE_SERVICE_ACCOUNT.WORKSPACE_ID.eq(workspaceServiceAccount.getWorkspaceId()))
            .execute();
      } else {
        ctx.insertInto(WORKSPACE_SERVICE_ACCOUNT)
            .set(WORKSPACE_SERVICE_ACCOUNT.WORKSPACE_ID, workspaceServiceAccount.getWorkspaceId())
            .set(WORKSPACE_SERVICE_ACCOUNT.SERVICE_ACCOUNT_ID, workspaceServiceAccount.getServiceAccountId())
            .set(WORKSPACE_SERVICE_ACCOUNT.SERVICE_ACCOUNT_EMAIL, workspaceServiceAccount.getServiceAccountEmail())
            .set(WORKSPACE_SERVICE_ACCOUNT.JSON_CREDENTIAL, JSONB.valueOf(Jsons.serialize(workspaceServiceAccount.getJsonCredential())))
            .set(WORKSPACE_SERVICE_ACCOUNT.HMAC_KEY, JSONB.valueOf(Jsons.serialize(workspaceServiceAccount.getHmacKey())))
            .set(WORKSPACE_SERVICE_ACCOUNT.CREATED_AT, timestamp)
            .set(WORKSPACE_SERVICE_ACCOUNT.UPDATED_AT, timestamp)
            .execute();
      }
    });
  }

  public List<StreamDescriptor> getAllStreamsForConnection(final UUID connectionId) throws ConfigNotFoundException, IOException {
    return standardSyncPersistence.getAllStreamsForConnection(connectionId);
  }

  public ConfiguredAirbyteCatalog getConfiguredCatalogForConnection(final UUID connectionId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSync standardSync = getStandardSync(connectionId);
    return standardSync.getCatalog();
  }

  public Geography getGeographyForConnection(final UUID connectionId) throws IOException {
    return database.query(ctx -> ctx.select(CONNECTION.GEOGRAPHY)
        .from(CONNECTION)
        .where(CONNECTION.ID.eq(connectionId))
        .limit(1))
        .fetchOneInto(Geography.class);
  }

  /**
   * Specialized query for efficiently determining eligibility for the Free Connector Program. If a
   * workspace has at least one Alpha or Beta connector, users of that workspace will be prompted to
   * sign up for the program. This check is performed on nearly every page load so the query needs to
   * be as efficient as possible.
   *
   * @param workspaceId ID of the workspace to check connectors for
   * @return boolean indicating if an alpha or beta connector exists within the workspace
   */
  public boolean getWorkspaceHasAlphaOrBetaConnector(final UUID workspaceId) throws IOException {
    final Condition releaseStageAlphaOrBeta = ACTOR_DEFINITION.RELEASE_STAGE.eq(ReleaseStage.alpha)
        .or(ACTOR_DEFINITION.RELEASE_STAGE.eq(ReleaseStage.beta));

    final Integer countResult = database.query(ctx -> ctx.selectCount()
        .from(ACTOR)
        .join(ACTOR_DEFINITION).on(ACTOR_DEFINITION.ID.eq(ACTOR.ACTOR_DEFINITION_ID))
        .where(ACTOR.WORKSPACE_ID.eq(workspaceId))
        .and(ACTOR.TOMBSTONE.notEqual(true))
        .and(releaseStageAlphaOrBeta))
        .fetchOneInto(Integer.class);

    return countResult > 0;
  }

  /**
   * Deletes all records with given id. If it deletes anything, returns true. Otherwise, false.
   *
   * @param table - table from which to delete the record
   * @param id - id of the record to delete
   * @return true if anything was deleted, otherwise false.
   * @throws IOException - you never know when you io
   */
  @SuppressWarnings("SameParameterValue")
  private boolean deleteById(final Table<?> table, final UUID id) throws IOException {
    return database.transaction(ctx -> ctx.deleteFrom(table)).where(DSL.field(DSL.name(PRIMARY_KEY)).eq(id)).execute() > 0;
  }

}
