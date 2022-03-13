/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR;
import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR_CATALOG;
import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR_CATALOG_FETCH_EVENT;
import static io.airbyte.db.instance.configs.jooq.Tables.CONNECTION;
import static io.airbyte.db.instance.configs.jooq.Tables.CONNECTION_OPERATION;
import static org.jooq.impl.DSL.asterisk;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Charsets;
import com.google.common.hash.HashFunction;
import com.google.common.hash.Hashing;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.MoreBooleans;
import io.airbyte.config.ActorCatalog;
import io.airbyte.config.ActorCatalogFetchEvent;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
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
import io.airbyte.config.State;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.db.instance.configs.jooq.enums.ActorType;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.time.OffsetDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.DSLContext;
import org.jooq.JSONB;
import org.jooq.Record;
import org.jooq.Record1;
import org.jooq.Record2;
import org.jooq.Result;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigRepository {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigRepository.class);

  private final ConfigPersistence persistence;
  private final ExceptionWrappingDatabase database;

  // todo (cgardens) - very bad that this exposed. usages should be removed. do not use it.
  @Deprecated
  public ExceptionWrappingDatabase getDatabase() {
    return database;
  }

  public ConfigRepository(final ConfigPersistence persistence, final Database database) {
    this.persistence = persistence;
    this.database = new ExceptionWrappingDatabase(database);;
  }

  public StandardWorkspace getStandardWorkspace(final UUID workspaceId, final boolean includeTombstone)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardWorkspace workspace = persistence.getConfig(ConfigSchema.STANDARD_WORKSPACE, workspaceId.toString(), StandardWorkspace.class);

    if (!MoreBooleans.isTruthy(workspace.getTombstone()) || includeTombstone) {
      return workspace;
    }
    throw new ConfigNotFoundException(ConfigSchema.STANDARD_WORKSPACE, workspaceId.toString());
  }

  public Optional<StandardWorkspace> getWorkspaceBySlugOptional(final String slug, final boolean includeTombstone)
      throws JsonValidationException, IOException {
    for (final StandardWorkspace workspace : listStandardWorkspaces(includeTombstone)) {
      if (workspace.getSlug().equals(slug)) {
        return Optional.of(workspace);
      }
    }
    return Optional.empty();
  }

  public StandardWorkspace getWorkspaceBySlug(final String slug, final boolean includeTombstone)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return getWorkspaceBySlugOptional(slug, includeTombstone).orElseThrow(() -> new ConfigNotFoundException(ConfigSchema.STANDARD_WORKSPACE, slug));
  }

  public List<StandardWorkspace> listStandardWorkspaces(final boolean includeTombstone) throws JsonValidationException, IOException {

    final List<StandardWorkspace> workspaces = new ArrayList<>();

    for (final StandardWorkspace workspace : persistence.listConfigs(ConfigSchema.STANDARD_WORKSPACE, StandardWorkspace.class)) {
      if (!MoreBooleans.isTruthy(workspace.getTombstone()) || includeTombstone) {
        workspaces.add(workspace);
      }
    }

    return workspaces;
  }

  public void writeStandardWorkspace(final StandardWorkspace workspace) throws JsonValidationException, IOException {
    persistence.writeConfig(ConfigSchema.STANDARD_WORKSPACE, workspace.getWorkspaceId().toString(), workspace);
  }

  public void setFeedback(final UUID workflowId) throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardWorkspace workspace = this.getStandardWorkspace(workflowId, false);

    workspace.setFeedbackDone(true);

    persistence.writeConfig(ConfigSchema.STANDARD_WORKSPACE, workspace.getWorkspaceId().toString(), workspace);
  }

  public StandardSourceDefinition getStandardSourceDefinition(final UUID sourceDefinitionId)
      throws JsonValidationException, IOException, ConfigNotFoundException {

    return persistence.getConfig(
        ConfigSchema.STANDARD_SOURCE_DEFINITION,
        sourceDefinitionId.toString(),
        StandardSourceDefinition.class);
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
      return getStandardWorkspace(source.getWorkspaceId(), isTombstone);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  public List<StandardSourceDefinition> listStandardSourceDefinitions(final boolean includeTombstone) throws JsonValidationException, IOException {
    final List<StandardSourceDefinition> sourceDefinitions = new ArrayList<>();
    for (final StandardSourceDefinition sourceDefinition : persistence.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION,
        StandardSourceDefinition.class)) {
      if (!MoreBooleans.isTruthy(sourceDefinition.getTombstone()) || includeTombstone) {
        sourceDefinitions.add(sourceDefinition);
      }
    }

    return sourceDefinitions;
  }

  public void writeStandardSourceDefinition(final StandardSourceDefinition sourceDefinition) throws JsonValidationException, IOException {
    persistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, sourceDefinition.getSourceDefinitionId().toString(), sourceDefinition);
  }

  public void deleteStandardSourceDefinition(final UUID sourceDefId) throws IOException {
    try {
      persistence.deleteConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, sourceDefId.toString());
    } catch (final ConfigNotFoundException e) {
      LOGGER.info("Attempted to delete source definition with id: {}, but it does not exist", sourceDefId);
    }
  }

  public void deleteSourceDefinitionAndAssociations(final UUID sourceDefinitionId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    deleteConnectorDefinitionAndAssociations(
        ConfigSchema.STANDARD_SOURCE_DEFINITION,
        ConfigSchema.SOURCE_CONNECTION,
        SourceConnection.class,
        SourceConnection::getSourceId,
        SourceConnection::getSourceDefinitionId,
        sourceDefinitionId);
  }

  public StandardDestinationDefinition getStandardDestinationDefinition(final UUID destinationDefinitionId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destinationDefinitionId.toString(),
        StandardDestinationDefinition.class);
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

  public List<StandardDestinationDefinition> listStandardDestinationDefinitions(final boolean includeTombstone)
      throws JsonValidationException, IOException {
    final List<StandardDestinationDefinition> destinationDefinitions = new ArrayList<>();

    for (final StandardDestinationDefinition destinationDefinition : persistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION,
        StandardDestinationDefinition.class)) {
      if (!MoreBooleans.isTruthy(destinationDefinition.getTombstone()) || includeTombstone) {
        destinationDefinitions.add(destinationDefinition);
      }
    }

    return destinationDefinitions;
  }

  public void writeStandardDestinationDefinition(final StandardDestinationDefinition destinationDefinition)
      throws JsonValidationException, IOException {
    persistence.writeConfig(
        ConfigSchema.STANDARD_DESTINATION_DEFINITION,
        destinationDefinition.getDestinationDefinitionId().toString(),
        destinationDefinition);
  }

  public void deleteStandardDestinationDefinition(final UUID destDefId) throws IOException {
    try {
      persistence.deleteConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destDefId.toString());
    } catch (final ConfigNotFoundException e) {
      LOGGER.info("Attempted to delete destination definition with id: {}, but it does not exist", destDefId);
    }
  }

  public void deleteStandardSyncDefinition(final UUID syncDefId) throws IOException {
    try {
      persistence.deleteConfig(ConfigSchema.STANDARD_SYNC, syncDefId.toString());
    } catch (final ConfigNotFoundException e) {
      LOGGER.info("Attempted to delete destination definition with id: {}, but it does not exist", syncDefId);
    }
  }

  public void deleteDestinationDefinitionAndAssociations(final UUID destinationDefinitionId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    deleteConnectorDefinitionAndAssociations(
        ConfigSchema.STANDARD_DESTINATION_DEFINITION,
        ConfigSchema.DESTINATION_CONNECTION,
        DestinationConnection.class,
        DestinationConnection::getDestinationId,
        DestinationConnection::getDestinationDefinitionId,
        destinationDefinitionId);
  }

  private <T> void deleteConnectorDefinitionAndAssociations(
                                                            final ConfigSchema definitionType,
                                                            final ConfigSchema connectorType,
                                                            final Class<T> connectorClass,
                                                            final Function<T, UUID> connectorIdGetter,
                                                            final Function<T, UUID> connectorDefinitionIdGetter,
                                                            final UUID definitionId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final Set<T> connectors = persistence.listConfigs(connectorType, connectorClass)
        .stream()
        .filter(connector -> connectorDefinitionIdGetter.apply(connector).equals(definitionId))
        .collect(Collectors.toSet());
    for (final T connector : connectors) {
      final Set<StandardSync> syncs = persistence.listConfigs(ConfigSchema.STANDARD_SYNC, StandardSync.class)
          .stream()
          .filter(sync -> sync.getSourceId().equals(connectorIdGetter.apply(connector))
              || sync.getDestinationId().equals(connectorIdGetter.apply(connector)))
          .collect(Collectors.toSet());

      for (final StandardSync sync : syncs) {
        persistence.deleteConfig(ConfigSchema.STANDARD_SYNC, sync.getConnectionId().toString());
      }
      persistence.deleteConfig(connectorType, connectorIdGetter.apply(connector).toString());
    }
    persistence.deleteConfig(definitionType, definitionId.toString());
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
    return persistence.getConfig(ConfigSchema.SOURCE_CONNECTION, sourceId.toString(), SourceConnection.class);
  }

  /**
   * MUST NOT ACCEPT SECRETS - Should only be called from { @link SecretsRepositoryWriter }
   *
   * Write a SourceConnection to the database. The configuration of the Source will be a partial
   * configuration (no secrets, just pointer to the secrets store).
   *
   * @param partialSource - The configuration of the Source will be a partial configuration (no
   *        secrets, just pointer to the secrets store)
   * @throws JsonValidationException - throws is the source is invalid
   * @throws IOException - you never know when you IO
   */
  public void writeSourceConnectionNoSecrets(final SourceConnection partialSource) throws JsonValidationException, IOException {
    persistence.writeConfig(ConfigSchema.SOURCE_CONNECTION, partialSource.getSourceId().toString(), partialSource);
  }

  /**
   * Returns all sources in the database. Does not contain secrets. To hydrate with secrets see
   * { @link SecretsRepositoryReader#listSourceConnectionWithSecrets() }.
   *
   * @return sources
   * @throws JsonValidationException - throws if returned sources are invalid
   * @throws IOException - you never know when you IO
   */
  public List<SourceConnection> listSourceConnection() throws JsonValidationException, IOException {
    return persistence.listConfigs(ConfigSchema.SOURCE_CONNECTION, SourceConnection.class);
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
    return persistence.getConfig(ConfigSchema.DESTINATION_CONNECTION, destinationId.toString(), DestinationConnection.class);
  }

  /**
   * MUST NOT ACCEPT SECRETS - Should only be called from { @link SecretsRepositoryWriter }
   *
   * Write a DestinationConnection to the database. The configuration of the Destination will be a
   * partial configuration (no secrets, just pointer to the secrets store).
   *
   * @param partialDestination - The configuration of the Destination will be a partial configuration
   *        (no secrets, just pointer to the secrets store)
   * @throws JsonValidationException - throws is the destination is invalid
   * @throws IOException - you never know when you IO
   */
  public void writeDestinationConnectionNoSecrets(final DestinationConnection partialDestination) throws JsonValidationException, IOException {
    persistence.writeConfig(ConfigSchema.DESTINATION_CONNECTION, partialDestination.getDestinationId().toString(), partialDestination);
  }

  /**
   * Returns all destinations in the database. Does not contain secrets. To hydrate with secrets see
   * { @link SecretsRepositoryReader#listDestinationConnectionWithSecrets() }.
   *
   * @return destinations
   * @throws JsonValidationException - throws if returned destinations are invalid
   * @throws IOException - you never know when you IO
   */
  public List<DestinationConnection> listDestinationConnection() throws JsonValidationException, IOException {
    return persistence.listConfigs(ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class);
  }

  public StandardSync getStandardSync(final UUID connectionId) throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(ConfigSchema.STANDARD_SYNC, connectionId.toString(), StandardSync.class);
  }

  public void writeStandardSync(final StandardSync standardSync) throws JsonValidationException, IOException {
    persistence.writeConfig(ConfigSchema.STANDARD_SYNC, standardSync.getConnectionId().toString(), standardSync);
  }

  public List<StandardSync> listStandardSyncs() throws ConfigNotFoundException, IOException, JsonValidationException {
    return persistence.listConfigs(ConfigSchema.STANDARD_SYNC, StandardSync.class);
  }

  public List<StandardSync> listWorkspaceStandardSyncs(final UUID workspaceId) throws IOException {
    final Result<Record> result = database.query(ctx -> ctx.select(CONNECTION.asterisk())
        .from(CONNECTION)
        .join(ACTOR).on(CONNECTION.SOURCE_ID.eq(ACTOR.ID))
        .where(ACTOR.WORKSPACE_ID.eq(workspaceId))).fetch();
    final List<StandardSync> standardSyncs = new ArrayList<>();
    for (final Record record : result) {
      final UUID connectionId = record.get(CONNECTION.ID);
      final Result<Record> connectionOperationRecords = database.query(ctx -> ctx.select(asterisk())
          .from(CONNECTION_OPERATION)
          .where(CONNECTION_OPERATION.CONNECTION_ID.eq(connectionId))
          .fetch());

      final List<UUID> connectionOperationIds =
          connectionOperationRecords.stream().map(r -> r.get(CONNECTION_OPERATION.OPERATION_ID)).collect(Collectors.toList());
      standardSyncs.add(DbConverter.buildStandardSync(record, connectionOperationIds));
    }
    return standardSyncs;
  }

  public StandardSyncOperation getStandardSyncOperation(final UUID operationId) throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(ConfigSchema.STANDARD_SYNC_OPERATION, operationId.toString(), StandardSyncOperation.class);
  }

  public void writeStandardSyncOperation(final StandardSyncOperation standardSyncOperation) throws JsonValidationException, IOException {
    persistence.writeConfig(ConfigSchema.STANDARD_SYNC_OPERATION, standardSyncOperation.getOperationId().toString(), standardSyncOperation);
  }

  public List<StandardSyncOperation> listStandardSyncOperations() throws IOException, JsonValidationException {
    return persistence.listConfigs(ConfigSchema.STANDARD_SYNC_OPERATION, StandardSyncOperation.class);
  }

  public SourceOAuthParameter getSourceOAuthParams(final UUID SourceOAuthParameterId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(ConfigSchema.SOURCE_OAUTH_PARAM, SourceOAuthParameterId.toString(), SourceOAuthParameter.class);
  }

  public Optional<SourceOAuthParameter> getSourceOAuthParamByDefinitionIdOptional(final UUID workspaceId, final UUID sourceDefinitionId)
      throws JsonValidationException, IOException {
    for (final SourceOAuthParameter oAuthParameter : listSourceOAuthParam()) {
      if (sourceDefinitionId.equals(oAuthParameter.getSourceDefinitionId()) &&
          Objects.equals(workspaceId, oAuthParameter.getWorkspaceId())) {
        return Optional.of(oAuthParameter);
      }
    }
    return Optional.empty();
  }

  public void writeSourceOAuthParam(final SourceOAuthParameter SourceOAuthParameter) throws JsonValidationException, IOException {
    persistence.writeConfig(ConfigSchema.SOURCE_OAUTH_PARAM, SourceOAuthParameter.getOauthParameterId().toString(), SourceOAuthParameter);
  }

  public List<SourceOAuthParameter> listSourceOAuthParam() throws JsonValidationException, IOException {
    return persistence.listConfigs(ConfigSchema.SOURCE_OAUTH_PARAM, SourceOAuthParameter.class);
  }

  public DestinationOAuthParameter getDestinationOAuthParams(final UUID destinationOAuthParameterId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return persistence.getConfig(ConfigSchema.DESTINATION_OAUTH_PARAM, destinationOAuthParameterId.toString(), DestinationOAuthParameter.class);
  }

  public Optional<DestinationOAuthParameter> getDestinationOAuthParamByDefinitionIdOptional(final UUID workspaceId,
                                                                                            final UUID destinationDefinitionId)
      throws JsonValidationException, IOException {
    for (final DestinationOAuthParameter oAuthParameter : listDestinationOAuthParam()) {
      if (destinationDefinitionId.equals(oAuthParameter.getDestinationDefinitionId()) &&
          Objects.equals(workspaceId, oAuthParameter.getWorkspaceId())) {
        return Optional.of(oAuthParameter);
      }
    }
    return Optional.empty();
  }

  public void writeDestinationOAuthParam(final DestinationOAuthParameter destinationOAuthParameter) throws JsonValidationException, IOException {
    persistence.writeConfig(ConfigSchema.DESTINATION_OAUTH_PARAM, destinationOAuthParameter.getOauthParameterId().toString(),
        destinationOAuthParameter);
  }

  public List<DestinationOAuthParameter> listDestinationOAuthParam() throws JsonValidationException, IOException {
    return persistence.listConfigs(ConfigSchema.DESTINATION_OAUTH_PARAM, DestinationOAuthParameter.class);
  }

  public Optional<State> getConnectionState(final UUID connectionId) throws IOException {
    try {
      final StandardSyncState connectionState = persistence.getConfig(
          ConfigSchema.STANDARD_SYNC_STATE,
          connectionId.toString(),
          StandardSyncState.class);
      return Optional.of(connectionState.getState());
    } catch (final ConfigNotFoundException e) {
      return Optional.empty();
    } catch (final JsonValidationException e) {
      throw new IllegalStateException(e);
    }
  }

  public void updateConnectionState(final UUID connectionId, final State state) throws IOException {
    LOGGER.info("Updating connection {} state: {}", connectionId, state);
    final StandardSyncState connectionState = new StandardSyncState().withConnectionId(connectionId).withState(state);
    try {
      persistence.writeConfig(ConfigSchema.STANDARD_SYNC_STATE, connectionId.toString(), connectionState);
    } catch (final JsonValidationException e) {
      throw new IllegalStateException(e);
    }
  }

  public Optional<ActorCatalog> getSourceCatalog(final UUID sourceId,
                                                 final String configurationHash,
                                                 final String connectorVersion)
      throws JsonValidationException, IOException {
    for (final ActorCatalogFetchEvent event : listActorCatalogFetchEvents()) {
      if (event.getConnectorVersion().equals(connectorVersion)
          && event.getConfigHash().equals(configurationHash)
          && event.getActorId().equals(sourceId)) {
        return getCatalogById(event.getActorCatalogId());
      }
    }
    return Optional.empty();
  }

  public List<ActorCatalogFetchEvent> listActorCatalogFetchEvents()
      throws JsonValidationException, IOException {
    final List<ActorCatalogFetchEvent> actorCatalogFetchEvents = new ArrayList<>();

    for (final ActorCatalogFetchEvent event : persistence.listConfigs(ConfigSchema.ACTOR_CATALOG_FETCH_EVENT,
        ActorCatalogFetchEvent.class)) {
      actorCatalogFetchEvents.add(event);
    }
    return actorCatalogFetchEvents;
  }

  public Optional<ActorCatalog> getCatalogById(final UUID catalogId)
      throws IOException {
    try {
      return Optional.of(persistence.getConfig(ConfigSchema.ACTOR_CATALOG, catalogId.toString(),
          ActorCatalog.class));
    } catch (final ConfigNotFoundException e) {
      return Optional.empty();
    } catch (final JsonValidationException e) {
      throw new IllegalStateException(e);
    }
  }

  public Optional<ActorCatalog> findExistingCatalog(final ActorCatalog actorCatalog)
      throws JsonValidationException, IOException {
    for (final ActorCatalog fetchedCatalog : listActorCatalogs()) {
      if (actorCatalog.getCatalogHash().equals(fetchedCatalog.getCatalogHash())) {
        return Optional.of(fetchedCatalog);
      }
    }
    return Optional.empty();
  }

  public List<ActorCatalog> listActorCatalogs()
      throws JsonValidationException, IOException {
    final List<ActorCatalog> actorCatalogs = new ArrayList<>();

    for (final ActorCatalog event : persistence.listConfigs(ConfigSchema.ACTOR_CATALOG,
        ActorCatalog.class)) {
      actorCatalogs.add(event);
    }
    return actorCatalogs;
  }

  private Map<UUID, AirbyteCatalog> findCatalogByHash(final String catalogHash, final DSLContext context) {
    final Result<Record2<UUID, JSONB>> records = context.select(ACTOR_CATALOG.ID, ACTOR_CATALOG.CATALOG)
        .from(ACTOR_CATALOG)
        .where(ACTOR_CATALOG.CATALOG_HASH.eq(catalogHash)).fetch();

    final Map<UUID, AirbyteCatalog> result = new HashMap<>();
    for (final Record record : records) {
      final AirbyteCatalog catalog = Jsons.deserialize(
          record.get(ACTOR_CATALOG.CATALOG).toString(), AirbyteCatalog.class);
      result.put(record.get(ACTOR_CATALOG.ID), catalog);
    }
    return result;
  }

  /**
   * Store an Airbyte catalog in DB if it is not present already
   *
   * Checks in the config DB if the catalog is present already, if so returns it identifier. It is not
   * present, it is inserted in DB with a new identifier and that identifier is returned.
   *
   * @param airbyteCatalog An Airbyte catalog to cache
   * @param context
   * @return the db identifier for the cached catalog.
   */
  private UUID getOrInsertActorCatalog(final AirbyteCatalog airbyteCatalog,
                                       final DSLContext context) {
    final OffsetDateTime timestamp = OffsetDateTime.now();
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

  public Optional<AirbyteCatalog> getActorCatalog(final UUID actorId,
                                                  final String actorVersion,
                                                  final String configHash)
      throws IOException {
    final Result<Record1<JSONB>> records = database.transaction(ctx -> ctx.select(ACTOR_CATALOG.CATALOG)
        .from(ACTOR_CATALOG).join(ACTOR_CATALOG_FETCH_EVENT)
        .on(ACTOR_CATALOG.ID.eq(ACTOR_CATALOG_FETCH_EVENT.ACTOR_CATALOG_ID))
        .where(ACTOR_CATALOG_FETCH_EVENT.ACTOR_ID.eq(actorId))
        .and(ACTOR_CATALOG_FETCH_EVENT.ACTOR_VERSION.eq(actorVersion))
        .and(ACTOR_CATALOG_FETCH_EVENT.CONFIG_HASH.eq(configHash))
        .orderBy(ACTOR_CATALOG_FETCH_EVENT.CREATED_AT.desc()).limit(1)).fetch();

    if (records.size() >= 1) {
      final JSONB record = records.get(0).get(ACTOR_CATALOG.CATALOG);
      return Optional.of(Jsons.deserialize(record.toString(), AirbyteCatalog.class));
    }
    return Optional.empty();

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
   * @param catalog
   * @param actorId
   * @param connectorVersion
   * @param configurationHash
   * @return The identifier (UUID) of the fetch event inserted in the database
   * @throws IOException
   */
  public UUID writeActorCatalogFetchEvent(final AirbyteCatalog catalog,
                                          final UUID actorId,
                                          final String connectorVersion,
                                          final String configurationHash)
      throws IOException {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    final UUID fetchEventID = UUID.randomUUID();
    database.transaction(ctx -> {
      final UUID catalogId = getOrInsertActorCatalog(catalog, ctx);
      return ctx.insertInto(ACTOR_CATALOG_FETCH_EVENT)
          .set(ACTOR_CATALOG_FETCH_EVENT.ID, fetchEventID)
          .set(ACTOR_CATALOG_FETCH_EVENT.ACTOR_ID, actorId)
          .set(ACTOR_CATALOG_FETCH_EVENT.ACTOR_CATALOG_ID, catalogId)
          .set(ACTOR_CATALOG_FETCH_EVENT.CONFIG_HASH, configurationHash)
          .set(ACTOR_CATALOG_FETCH_EVENT.ACTOR_VERSION, connectorVersion)
          .set(ACTOR_CATALOG_FETCH_EVENT.MODIFIED_AT, timestamp)
          .set(ACTOR_CATALOG_FETCH_EVENT.CREATED_AT, timestamp).execute();
    });

    return fetchEventID;
  }

  public int countConnectionsForWorkspace(final UUID workspaceId) throws IOException {
    return database.query(ctx -> ctx.selectCount()
        .from(CONNECTION)
        .join(ACTOR).on(CONNECTION.SOURCE_ID.eq(ACTOR.ID))
        .where(ACTOR.WORKSPACE_ID.eq(workspaceId))
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
   * MUST NOT ACCEPT SECRETS - Package private so that secrets are not accidentally passed in. Should
   * only be called from { @link SecretsRepositoryWriter }
   *
   * Takes as inputs configurations that it then uses to overwrite the contents of the existing Config
   * Database.
   *
   * @param configs - configurations to load.
   * @param dryRun - whether to test run of the load
   * @throws IOException - you never know when you IO.
   */
  void replaceAllConfigsNoSecrets(final Map<AirbyteConfig, Stream<?>> configs, final boolean dryRun) throws IOException {
    persistence.replaceAllConfigs(configs, dryRun);
  }

  /**
   * Dumps all configurations in the Config Database. Note: It will not contain secrets as the Config
   * Database does not contain connector configurations that include secrets. In order to hydrate with
   * secrets see { @link SecretsRepositoryReader#dumpConfigs() }.
   *
   * @return all configurations in the Config Database
   * @throws IOException - you never know when you IO
   */
  public Map<String, Stream<JsonNode>> dumpConfigsNoSecrets() throws IOException {
    return persistence.dumpConfigs();
  }

  /**
   * MUST NOT ACCEPT SECRETS - Package private so that secrets are not accidentally passed in. Should
   * only be called from { @link SecretsRepositoryWriter }
   *
   * Loads all Data from a ConfigPersistence into the database.
   *
   * @param seedPersistenceWithoutSecrets - seed persistence WITHOUT secrets
   * @throws IOException - you never know when you IO
   */
  public void loadDataNoSecrets(final ConfigPersistence seedPersistenceWithoutSecrets) throws IOException {
    persistence.loadData(seedPersistenceWithoutSecrets);
  }

}
