/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import static java.util.stream.Collectors.toMap;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import io.airbyte.api.model.generated.AirbyteCatalog;
import io.airbyte.api.model.generated.AirbyteStream;
import io.airbyte.api.model.generated.AirbyteStreamAndConfiguration;
import io.airbyte.api.model.generated.AirbyteStreamConfiguration;
import io.airbyte.api.model.generated.CatalogDiff;
import io.airbyte.api.model.generated.ConnectionCreate;
import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.ConnectionRead;
import io.airbyte.api.model.generated.ConnectionStateType;
import io.airbyte.api.model.generated.ConnectionUpdate;
import io.airbyte.api.model.generated.DestinationIdRequestBody;
import io.airbyte.api.model.generated.DestinationRead;
import io.airbyte.api.model.generated.DestinationSnippetRead;
import io.airbyte.api.model.generated.FieldTransform;
import io.airbyte.api.model.generated.JobRead;
import io.airbyte.api.model.generated.OperationCreate;
import io.airbyte.api.model.generated.OperationReadList;
import io.airbyte.api.model.generated.OperationUpdate;
import io.airbyte.api.model.generated.SchemaChange;
import io.airbyte.api.model.generated.SelectedFieldInfo;
import io.airbyte.api.model.generated.SourceDiscoverSchemaRead;
import io.airbyte.api.model.generated.SourceDiscoverSchemaRequestBody;
import io.airbyte.api.model.generated.SourceIdRequestBody;
import io.airbyte.api.model.generated.SourceRead;
import io.airbyte.api.model.generated.SourceSnippetRead;
import io.airbyte.api.model.generated.StreamDescriptor;
import io.airbyte.api.model.generated.StreamTransform;
import io.airbyte.api.model.generated.StreamTransform.TransformTypeEnum;
import io.airbyte.api.model.generated.WebBackendConnectionCreate;
import io.airbyte.api.model.generated.WebBackendConnectionListItem;
import io.airbyte.api.model.generated.WebBackendConnectionListRequestBody;
import io.airbyte.api.model.generated.WebBackendConnectionRead;
import io.airbyte.api.model.generated.WebBackendConnectionReadList;
import io.airbyte.api.model.generated.WebBackendConnectionRequestBody;
import io.airbyte.api.model.generated.WebBackendConnectionUpdate;
import io.airbyte.api.model.generated.WebBackendOperationCreateOrUpdate;
import io.airbyte.api.model.generated.WebBackendWorkspaceState;
import io.airbyte.api.model.generated.WebBackendWorkspaceStateResult;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.MoreBooleans;
import io.airbyte.commons.server.converters.ApiPojoConverters;
import io.airbyte.commons.server.handlers.helpers.CatalogConverter;
import io.airbyte.commons.server.scheduler.EventRunner;
import io.airbyte.config.ActorCatalog;
import io.airbyte.config.ActorCatalogFetchEvent;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.ConfigRepository.StandardSyncQuery;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.helper.ProtocolConverters;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;

@Singleton
public class WebBackendConnectionsHandler {

  private final ConnectionsHandler connectionsHandler;
  private final StateHandler stateHandler;
  private final SourceHandler sourceHandler;
  private final DestinationHandler destinationHandler;
  private final JobHistoryHandler jobHistoryHandler;
  private final SchedulerHandler schedulerHandler;
  private final OperationsHandler operationsHandler;
  private final EventRunner eventRunner;
  // todo (cgardens) - this handler should NOT have access to the db. only access via handler.
  private final ConfigRepository configRepository;

  public WebBackendConnectionsHandler(final ConnectionsHandler connectionsHandler,
                                      final StateHandler stateHandler,
                                      final SourceHandler sourceHandler,
                                      final DestinationHandler destinationHandler,
                                      final JobHistoryHandler jobHistoryHandler,
                                      final SchedulerHandler schedulerHandler,
                                      final OperationsHandler operationsHandler,
                                      final EventRunner eventRunner,
                                      final ConfigRepository configRepository) {
    this.connectionsHandler = connectionsHandler;
    this.stateHandler = stateHandler;
    this.sourceHandler = sourceHandler;
    this.destinationHandler = destinationHandler;
    this.jobHistoryHandler = jobHistoryHandler;
    this.schedulerHandler = schedulerHandler;
    this.operationsHandler = operationsHandler;
    this.eventRunner = eventRunner;
    this.configRepository = configRepository;
  }

  public WebBackendWorkspaceStateResult getWorkspaceState(final WebBackendWorkspaceState webBackendWorkspaceState) throws IOException {
    final var workspaceId = webBackendWorkspaceState.getWorkspaceId();
    final var connectionCount = configRepository.countConnectionsForWorkspace(workspaceId);
    final var destinationCount = configRepository.countDestinationsForWorkspace(workspaceId);
    final var sourceCount = configRepository.countSourcesForWorkspace(workspaceId);

    return new WebBackendWorkspaceStateResult()
        .hasConnections(connectionCount > 0)
        .hasDestinations(destinationCount > 0)
        .hasSources(sourceCount > 0);
  }

  public ConnectionStateType getStateType(final ConnectionIdRequestBody connectionIdRequestBody) throws IOException {
    return Enums.convertTo(stateHandler.getState(connectionIdRequestBody).getStateType(), ConnectionStateType.class);
  }

  public WebBackendConnectionReadList webBackendListConnectionsForWorkspace(final WebBackendConnectionListRequestBody webBackendConnectionListRequestBody)
      throws IOException {

    final StandardSyncQuery query = new StandardSyncQuery(
        webBackendConnectionListRequestBody.getWorkspaceId(),
        webBackendConnectionListRequestBody.getSourceId(),
        webBackendConnectionListRequestBody.getDestinationId(),
        // passing 'false' so that deleted connections are not included
        false);

    final List<StandardSync> standardSyncs = configRepository.listWorkspaceStandardSyncs(query);
    final List<UUID> sourceIds = standardSyncs.stream().map(StandardSync::getSourceId).toList();
    final List<UUID> destinationIds = standardSyncs.stream().map(StandardSync::getDestinationId).toList();
    final List<UUID> connectionIds = standardSyncs.stream().map(StandardSync::getConnectionId).toList();

    // Fetching all the related objects we need for the final output
    final Map<UUID, SourceSnippetRead> sourceReadById = getSourceSnippetReadById(sourceIds);
    final Map<UUID, DestinationSnippetRead> destinationReadById = getDestinationSnippetReadById(destinationIds);
    final Map<UUID, JobRead> latestJobByConnectionId = getLatestJobByConnectionId(connectionIds);
    // This call could be removed, running jobs should be a subset of latest jobs, need to expose the
    // right status filtering for this.
    final Map<UUID, JobRead> runningJobByConnectionId = getRunningJobByConnectionId(connectionIds);
    final Map<UUID, ActorCatalogFetchEvent> newestFetchEventsByActorId =
        configRepository.getMostRecentActorCatalogFetchEventForSources(sourceIds);

    final List<WebBackendConnectionListItem> connectionItems = Lists.newArrayList();

    for (final StandardSync standardSync : standardSyncs) {
      connectionItems.add(
          buildWebBackendConnectionListItem(
              standardSync,
              sourceReadById,
              destinationReadById,
              latestJobByConnectionId,
              runningJobByConnectionId,
              Optional.ofNullable(newestFetchEventsByActorId.get(standardSync.getSourceId()))));
    }

    return new WebBackendConnectionReadList().connections(connectionItems);
  }

  private Map<UUID, JobRead> getLatestJobByConnectionId(final List<UUID> connectionIds) throws IOException {
    return jobHistoryHandler.getLatestSyncJobsForConnections(connectionIds).stream()
        .collect(Collectors.toMap(j -> UUID.fromString(j.getConfigId()), Function.identity()));
  }

  private Map<UUID, JobRead> getRunningJobByConnectionId(final List<UUID> connectionIds) throws IOException {
    return jobHistoryHandler.getRunningSyncJobForConnections(connectionIds).stream()
        .collect(Collectors.toMap(j -> UUID.fromString(j.getConfigId()), Function.identity()));
  }

  private Map<UUID, SourceSnippetRead> getSourceSnippetReadById(final List<UUID> sourceIds) throws IOException {
    return configRepository.getSourceAndDefinitionsFromSourceIds(sourceIds)
        .stream()
        .map(sourceAndDefinition -> SourceHandler.toSourceSnippetRead(sourceAndDefinition.source(), sourceAndDefinition.definition()))
        .collect(Collectors.toMap(SourceSnippetRead::getSourceId, Function.identity()));
  }

  private Map<UUID, DestinationSnippetRead> getDestinationSnippetReadById(final List<UUID> destinationIds) throws IOException {
    return configRepository.getDestinationAndDefinitionsFromDestinationIds(destinationIds)
        .stream()
        .map(destinationAndDefinition -> DestinationHandler.toDestinationSnippetRead(destinationAndDefinition.destination(),
            destinationAndDefinition.definition()))
        .collect(Collectors.toMap(DestinationSnippetRead::getDestinationId, Function.identity()));
  }

  private WebBackendConnectionRead buildWebBackendConnectionRead(final ConnectionRead connectionRead, final Optional<UUID> currentSourceCatalogId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final SourceRead source = getSourceRead(connectionRead.getSourceId());
    final DestinationRead destination = getDestinationRead(connectionRead.getDestinationId());
    final OperationReadList operations = getOperationReadList(connectionRead);
    final Optional<JobRead> latestSyncJob = jobHistoryHandler.getLatestSyncJob(connectionRead.getConnectionId());
    final Optional<JobRead> latestRunningSyncJob = jobHistoryHandler.getLatestRunningSyncJob(connectionRead.getConnectionId());

    final WebBackendConnectionRead webBackendConnectionRead = getWebBackendConnectionRead(connectionRead, source, destination, operations)
        .catalogId(connectionRead.getSourceCatalogId());

    webBackendConnectionRead.setIsSyncing(latestRunningSyncJob.isPresent());

    latestSyncJob.ifPresent(job -> {
      webBackendConnectionRead.setLatestSyncJobCreatedAt(job.getCreatedAt());
      webBackendConnectionRead.setLatestSyncJobStatus(job.getStatus());
    });

    final Optional<ActorCatalogFetchEvent> mostRecentFetchEvent =
        configRepository.getMostRecentActorCatalogFetchEventForSource(connectionRead.getSourceId());

    final SchemaChange schemaChange = getSchemaChange(connectionRead, currentSourceCatalogId, mostRecentFetchEvent);

    webBackendConnectionRead.setSchemaChange(schemaChange);

    return webBackendConnectionRead;
  }

  static private WebBackendConnectionListItem buildWebBackendConnectionListItem(
                                                                                final StandardSync standardSync,
                                                                                final Map<UUID, SourceSnippetRead> sourceReadById,
                                                                                final Map<UUID, DestinationSnippetRead> destinationReadById,
                                                                                final Map<UUID, JobRead> latestJobByConnectionId,
                                                                                final Map<UUID, JobRead> runningJobByConnectionId,
                                                                                final Optional<ActorCatalogFetchEvent> latestFetchEvent) {

    final SourceSnippetRead source = sourceReadById.get(standardSync.getSourceId());
    final DestinationSnippetRead destination = destinationReadById.get(standardSync.getDestinationId());
    final Optional<JobRead> latestSyncJob = Optional.ofNullable(latestJobByConnectionId.get(standardSync.getConnectionId()));
    final Optional<JobRead> latestRunningSyncJob = Optional.ofNullable(runningJobByConnectionId.get(standardSync.getConnectionId()));
    final ConnectionRead connectionRead = ApiPojoConverters.internalToConnectionRead(standardSync);
    final Optional<UUID> currentCatalogId = connectionRead == null ? Optional.empty() : Optional.ofNullable(connectionRead.getSourceCatalogId());

    final SchemaChange schemaChange = getSchemaChange(connectionRead, currentCatalogId, latestFetchEvent);

    final WebBackendConnectionListItem listItem = new WebBackendConnectionListItem()
        .connectionId(standardSync.getConnectionId())
        .status(ApiPojoConverters.toApiStatus(standardSync.getStatus()))
        .name(standardSync.getName())
        .scheduleType(ApiPojoConverters.toApiConnectionScheduleType(standardSync))
        .scheduleData(ApiPojoConverters.toApiConnectionScheduleData(standardSync))
        .source(source)
        .destination(destination)
        .isSyncing(latestRunningSyncJob.isPresent())
        .schemaChange(schemaChange);

    latestSyncJob.ifPresent(job -> {
      listItem.setLatestSyncJobCreatedAt(job.getCreatedAt());
      listItem.setLatestSyncJobStatus(job.getStatus());
    });

    return listItem;
  }

  /*
   * A breakingChange boolean is stored on the connectionRead object and corresponds to the boolean
   * breakingChange field on the connection table. If there is not a breaking change, we still have to
   * check whether there is a non-breaking schema change by fetching the most recent
   * ActorCatalogFetchEvent. A new ActorCatalogFetchEvent is stored each time there is a source schema
   * refresh, so if the most recent ActorCatalogFetchEvent has a different actor catalog than the
   * existing actor catalog, there is a schema change.
   */
  @VisibleForTesting
  static SchemaChange getSchemaChange(
                                      final ConnectionRead connectionRead,
                                      final Optional<UUID> currentSourceCatalogId,
                                      final Optional<ActorCatalogFetchEvent> mostRecentFetchEvent) {
    if (connectionRead == null || currentSourceCatalogId.isEmpty()) {
      return SchemaChange.NO_CHANGE;
    }

    if (connectionRead.getBreakingChange() != null && connectionRead.getBreakingChange()) {
      return SchemaChange.BREAKING;
    }

    if (mostRecentFetchEvent.isPresent() && !mostRecentFetchEvent.map(ActorCatalogFetchEvent::getActorCatalogId).equals(currentSourceCatalogId)) {
      return SchemaChange.NON_BREAKING;
    }

    return SchemaChange.NO_CHANGE;
  }

  private SourceRead getSourceRead(final UUID sourceId) throws JsonValidationException, IOException, ConfigNotFoundException {
    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody().sourceId(sourceId);
    return sourceHandler.getSource(sourceIdRequestBody);
  }

  private DestinationRead getDestinationRead(final UUID destinationId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final DestinationIdRequestBody destinationIdRequestBody = new DestinationIdRequestBody().destinationId(destinationId);
    return destinationHandler.getDestination(destinationIdRequestBody);
  }

  private OperationReadList getOperationReadList(final ConnectionRead connectionRead)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody().connectionId(connectionRead.getConnectionId());
    return operationsHandler.listOperationsForConnection(connectionIdRequestBody);
  }

  private static WebBackendConnectionRead getWebBackendConnectionRead(final ConnectionRead connectionRead,
                                                                      final SourceRead source,
                                                                      final DestinationRead destination,
                                                                      final OperationReadList operations) {
    return new WebBackendConnectionRead()
        .connectionId(connectionRead.getConnectionId())
        .sourceId(connectionRead.getSourceId())
        .destinationId(connectionRead.getDestinationId())
        .operationIds(connectionRead.getOperationIds())
        .name(connectionRead.getName())
        .namespaceDefinition(connectionRead.getNamespaceDefinition())
        .namespaceFormat(connectionRead.getNamespaceFormat())
        .prefix(connectionRead.getPrefix())
        .syncCatalog(connectionRead.getSyncCatalog())
        .status(connectionRead.getStatus())
        .schedule(connectionRead.getSchedule())
        .scheduleType(connectionRead.getScheduleType())
        .scheduleData(connectionRead.getScheduleData())
        .source(source)
        .destination(destination)
        .operations(operations.getOperations())
        .resourceRequirements(connectionRead.getResourceRequirements())
        .geography(connectionRead.getGeography())
        .notifySchemaChanges(connectionRead.getNotifySchemaChanges())
        .nonBreakingChangesPreference(connectionRead.getNonBreakingChangesPreference());
  }

  // todo (cgardens) - This logic is a headache to follow it stems from the internal data model not
  // tracking selected streams in any reasonable way. We should update that.
  public WebBackendConnectionRead webBackendGetConnection(final WebBackendConnectionRequestBody webBackendConnectionRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody()
        .connectionId(webBackendConnectionRequestBody.getConnectionId());

    final ConnectionRead connection = connectionsHandler.getConnection(connectionIdRequestBody.getConnectionId());

    /*
     * This variable contains all configuration but will be missing streams that were not selected.
     */
    final AirbyteCatalog configuredCatalog = connection.getSyncCatalog();
    /*
     * This catalog represents the full catalog that was used to create the configured catalog. It will
     * have all streams that were present at the time. It will have no configuration set.
     */
    final Optional<AirbyteCatalog> catalogUsedToMakeConfiguredCatalog = connectionsHandler
        .getConnectionAirbyteCatalog(webBackendConnectionRequestBody.getConnectionId());

    /*
     * This catalog represents the full catalog that exists now for the source. It will have no
     * configuration set.
     */
    final Optional<SourceDiscoverSchemaRead> refreshedCatalog;
    if (MoreBooleans.isTruthy(webBackendConnectionRequestBody.getWithRefreshedCatalog())) {
      refreshedCatalog = getRefreshedSchema(connection.getSourceId(), connection.getConnectionId());
    } else {
      refreshedCatalog = Optional.empty();
    }

    final CatalogDiff diff;
    final AirbyteCatalog syncCatalog;
    final Optional<UUID> currentSourceCatalogId = Optional.ofNullable(connection.getSourceCatalogId());
    if (refreshedCatalog.isPresent()) {
      connection.sourceCatalogId(refreshedCatalog.get().getCatalogId());
      /*
       * constructs a full picture of all existing configured + all new / updated streams in the newest
       * catalog.
       *
       * Diffing the catalog used to make the configured catalog gives us the clearest diff between the
       * schema when the configured catalog was made and now. In the case where we do not have the
       * original catalog used to make the configured catalog, we make due, but using the configured
       * catalog itself. The drawback is that any stream that was not selected in the configured catalog
       * but was present at time of configuration will appear in the diff as an added stream which is
       * confusing. We need to figure out why source_catalog_id is not always populated in the db.
       */
      syncCatalog = updateSchemaWithRefreshedDiscoveredCatalog(configuredCatalog, catalogUsedToMakeConfiguredCatalog.orElse(configuredCatalog),
          refreshedCatalog.get().getCatalog());

      diff = refreshedCatalog.get().getCatalogDiff();
      connection.setBreakingChange(refreshedCatalog.get().getBreakingChange());
      connection.setStatus(refreshedCatalog.get().getConnectionStatus());
    } else if (catalogUsedToMakeConfiguredCatalog.isPresent()) {
      // reconstructs a full picture of the full schema at the time the catalog was configured.
      syncCatalog = updateSchemaWithOriginalDiscoveredCatalog(configuredCatalog, catalogUsedToMakeConfiguredCatalog.get());
      // diff not relevant if there was no refresh.
      diff = null;
    } else {
      // fallback. over time this should be rarely used because source_catalog_id should always be set.
      syncCatalog = configuredCatalog;
      // diff not relevant if there was no refresh.
      diff = null;
    }

    connection.setSyncCatalog(syncCatalog);
    return buildWebBackendConnectionRead(connection, currentSourceCatalogId).catalogDiff(diff);
  }

  private AirbyteCatalog updateSchemaWithOriginalDiscoveredCatalog(final AirbyteCatalog configuredCatalog,
                                                                   final AirbyteCatalog originalDiscoveredCatalog) {
    // We pass the original discovered catalog in as the "new" discovered catalog.
    return updateSchemaWithRefreshedDiscoveredCatalog(configuredCatalog, originalDiscoveredCatalog, originalDiscoveredCatalog);
  }

  private Optional<SourceDiscoverSchemaRead> getRefreshedSchema(final UUID sourceId, final UUID connectionId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final SourceDiscoverSchemaRequestBody discoverSchemaReadReq = new SourceDiscoverSchemaRequestBody()
        .sourceId(sourceId)
        .disableCache(true)
        .connectionId(connectionId);
    final SourceDiscoverSchemaRead schemaRead = schedulerHandler.discoverSchemaForSourceFromSourceId(discoverSchemaReadReq);
    return Optional.ofNullable(schemaRead);
  }

  /**
   * Applies existing configurations to a newly discovered catalog. For example, if the users stream
   * is in the old and new catalog, any configuration that was previously set for users, we add to the
   * new catalog.
   *
   * @param originalConfigured fully configured, original catalog
   * @param originalDiscovered the original discovered catalog used to make the original configured
   *        catalog
   * @param discovered newly discovered catalog, no configurations set
   * @return merged catalog, most up-to-date schema with most up-to-date configurations from old
   *         catalog
   */
  @VisibleForTesting
  protected static AirbyteCatalog updateSchemaWithRefreshedDiscoveredCatalog(final AirbyteCatalog originalConfigured,
                                                                             final AirbyteCatalog originalDiscovered,
                                                                             final AirbyteCatalog discovered) {
    /*
     * We can't directly use s.getStream() as the key, because it contains a bunch of other fields, so
     * we just define a quick-and-dirty record class.
     */
    final Map<Stream, AirbyteStreamAndConfiguration> streamDescriptorToOriginalStream = originalConfigured.getStreams()
        .stream()
        .collect(toMap(s -> new Stream(s.getStream().getName(), s.getStream().getNamespace()), s -> s));
    final Map<Stream, AirbyteStreamAndConfiguration> streamDescriptorToOriginalDiscoveredStream = originalDiscovered.getStreams()
        .stream()
        .collect(toMap(s -> new Stream(s.getStream().getName(), s.getStream().getNamespace()), s -> s));

    final List<AirbyteStreamAndConfiguration> streams = new ArrayList<>();

    for (final AirbyteStreamAndConfiguration discoveredStream : discovered.getStreams()) {
      final AirbyteStream stream = discoveredStream.getStream();
      final AirbyteStreamAndConfiguration originalConfiguredStream = streamDescriptorToOriginalStream.get(
          new Stream(stream.getName(), stream.getNamespace()));
      final AirbyteStreamAndConfiguration originalDiscoveredStream = streamDescriptorToOriginalDiscoveredStream.get(
          new Stream(stream.getName(), stream.getNamespace()));
      final AirbyteStreamConfiguration outputStreamConfig;

      if (originalConfiguredStream != null) {
        final AirbyteStreamConfiguration originalStreamConfig = originalConfiguredStream.getConfig();
        final AirbyteStreamConfiguration discoveredStreamConfig = discoveredStream.getConfig();
        outputStreamConfig = new AirbyteStreamConfiguration();

        if (stream.getSupportedSyncModes().contains(originalStreamConfig.getSyncMode())) {
          outputStreamConfig.setSyncMode(originalStreamConfig.getSyncMode());
        } else {
          outputStreamConfig.setSyncMode(discoveredStreamConfig.getSyncMode());
        }

        if (originalStreamConfig.getCursorField().size() > 0) {
          outputStreamConfig.setCursorField(originalStreamConfig.getCursorField());
        } else {
          outputStreamConfig.setCursorField(discoveredStreamConfig.getCursorField());
        }

        outputStreamConfig.setDestinationSyncMode(originalStreamConfig.getDestinationSyncMode());
        if (originalStreamConfig.getPrimaryKey().size() > 0) {
          outputStreamConfig.setPrimaryKey(originalStreamConfig.getPrimaryKey());
        } else {
          outputStreamConfig.setPrimaryKey(discoveredStreamConfig.getPrimaryKey());
        }

        outputStreamConfig.setAliasName(originalStreamConfig.getAliasName());
        outputStreamConfig.setSelected(originalConfiguredStream.getConfig().getSelected());

        outputStreamConfig.setFieldSelectionEnabled(originalStreamConfig.getFieldSelectionEnabled());
        if (outputStreamConfig.getFieldSelectionEnabled()) {
          // TODO(mfsiega-airbyte): support nested fields.
          // If field selection is enabled, populate the selected fields.
          final Set<String> originallyDiscovered = new HashSet<>();
          final Set<String> refreshDiscovered = new HashSet<>();
          // NOTE: by only taking the first element of the path, we're restricting to top-level fields.
          final Set<String> originallySelected = new HashSet<>(
              originalConfiguredStream.getConfig().getSelectedFields().stream().map((field) -> field.getFieldPath().get(0)).toList());
          originalDiscoveredStream.getStream().getJsonSchema().findPath("properties").fieldNames()
              .forEachRemaining((name) -> originallyDiscovered.add(name));
          stream.getJsonSchema().findPath("properties").fieldNames().forEachRemaining((name) -> refreshDiscovered.add(name));
          // We include a selected field if it:
          // (is in the newly discovered schema) AND (it was either originally selected OR not in the
          // originally discovered schema at all)
          // NOTE: this implies that the default behaviour for newly-discovered columns is to add them.
          for (final String discoveredField : refreshDiscovered) {
            if (originallySelected.contains(discoveredField) || !originallyDiscovered.contains(discoveredField)) {
              outputStreamConfig.addSelectedFieldsItem(new SelectedFieldInfo().addFieldPathItem(discoveredField));
            }
          }
        }

      } else {
        outputStreamConfig = discoveredStream.getConfig();
        outputStreamConfig.setSelected(false);
      }
      final AirbyteStreamAndConfiguration outputStream = new AirbyteStreamAndConfiguration()
          .stream(Jsons.clone(stream))
          .config(outputStreamConfig);
      streams.add(outputStream);
    }
    return new AirbyteCatalog().streams(streams);
  }

  public WebBackendConnectionRead webBackendCreateConnection(final WebBackendConnectionCreate webBackendConnectionCreate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<UUID> operationIds = createOperations(webBackendConnectionCreate);

    final ConnectionCreate connectionCreate = toConnectionCreate(webBackendConnectionCreate, operationIds);
    final Optional<UUID> currentSourceCatalogId = Optional.ofNullable(connectionCreate.getSourceCatalogId());
    return buildWebBackendConnectionRead(connectionsHandler.createConnection(connectionCreate), currentSourceCatalogId);
  }

  /**
   * Given a WebBackendConnectionUpdate, patch the connection by applying any non-null properties from
   * the patch to the connection.
   *
   * As a convenience to the front-end, this endpoint also creates new operations present in the
   * request, and bundles those newly-created operationIds into the connection update.
   */
  public WebBackendConnectionRead webBackendUpdateConnection(final WebBackendConnectionUpdate webBackendConnectionPatch)
      throws ConfigNotFoundException, IOException, JsonValidationException {

    final UUID connectionId = webBackendConnectionPatch.getConnectionId();
    final ConnectionRead originalConnectionRead = connectionsHandler.getConnection(connectionId);
    boolean breakingChange = originalConnectionRead.getBreakingChange() != null && originalConnectionRead.getBreakingChange();

    // If there have been changes to the sync catalog, check whether these changes result in or fix a
    // broken connection
    if (webBackendConnectionPatch.getSyncCatalog() != null) {
      // Get the most recent actor catalog fetched for this connection's source and the newly updated sync
      // catalog
      Optional<ActorCatalog> mostRecentActorCatalog = configRepository.getMostRecentActorCatalogForSource(originalConnectionRead.getSourceId());
      AirbyteCatalog newAirbyteCatalog = webBackendConnectionPatch.getSyncCatalog();
      // Get the diff between these two catalogs to check for breaking changes
      if (mostRecentActorCatalog.isPresent()) {
        final io.airbyte.protocol.models.AirbyteCatalog mostRecentAirbyteCatalog =
            Jsons.object(mostRecentActorCatalog.get().getCatalog(), io.airbyte.protocol.models.AirbyteCatalog.class);
        final StandardSourceDefinition sourceDefinition = configRepository.getSourceDefinitionFromSource(originalConnectionRead.getSourceId());
        final CatalogDiff catalogDiff =
            connectionsHandler.getDiff(newAirbyteCatalog, CatalogConverter.toApi(mostRecentAirbyteCatalog, sourceDefinition),
                CatalogConverter.toConfiguredProtocol(newAirbyteCatalog));
        breakingChange = containsBreakingChange(catalogDiff);
      }
    }

    // before doing any updates, fetch the existing catalog so that it can be diffed
    // with the final catalog to determine which streams might need to be reset.
    final ConfiguredAirbyteCatalog oldConfiguredCatalog =
        configRepository.getConfiguredCatalogForConnection(connectionId);

    final List<UUID> newAndExistingOperationIds = createOrUpdateOperations(originalConnectionRead, webBackendConnectionPatch);

    // pass in operationIds because the patch object doesn't include operationIds that were just created
    // above.
    final ConnectionUpdate connectionPatch = toConnectionPatch(webBackendConnectionPatch, newAndExistingOperationIds, breakingChange);

    // persist the update and set the connectionRead to the updated form.
    final ConnectionRead updatedConnectionRead = connectionsHandler.updateConnection(connectionPatch);

    // detect if any streams need to be reset based on the patch and initial catalog, if so, reset them
    resetStreamsIfNeeded(webBackendConnectionPatch, oldConfiguredCatalog, updatedConnectionRead, originalConnectionRead);
    /*
     * This catalog represents the full catalog that was used to create the configured catalog. It will
     * have all streams that were present at the time. It will have no configuration set.
     */
    final Optional<AirbyteCatalog> catalogUsedToMakeConfiguredCatalog = connectionsHandler
        .getConnectionAirbyteCatalog(connectionId);
    if (catalogUsedToMakeConfiguredCatalog.isPresent()) {
      // Update the Catalog returned to include all streams, including disabled ones
      final AirbyteCatalog syncCatalog =
          updateSchemaWithRefreshedDiscoveredCatalog(updatedConnectionRead.getSyncCatalog(), catalogUsedToMakeConfiguredCatalog.get(),
              catalogUsedToMakeConfiguredCatalog.get());
      updatedConnectionRead.setSyncCatalog(syncCatalog);
    }

    final Optional<UUID> currentSourceCatalogId = Optional.ofNullable(updatedConnectionRead.getSourceCatalogId());
    return buildWebBackendConnectionRead(updatedConnectionRead, currentSourceCatalogId);
  }

  /**
   * Given a fully updated connection, check for a diff between the old catalog and the updated
   * catalog to see if any streams need to be reset.
   */
  private void resetStreamsIfNeeded(final WebBackendConnectionUpdate webBackendConnectionPatch,
                                    final ConfiguredAirbyteCatalog oldConfiguredCatalog,
                                    final ConnectionRead updatedConnectionRead,
                                    final ConnectionRead oldConnectionRead)
      throws IOException, JsonValidationException, ConfigNotFoundException {

    final UUID connectionId = webBackendConnectionPatch.getConnectionId();
    final Boolean skipReset = webBackendConnectionPatch.getSkipReset() != null ? webBackendConnectionPatch.getSkipReset() : false;
    if (!skipReset) {
      final AirbyteCatalog apiExistingCatalog = CatalogConverter.toApi(oldConfiguredCatalog,
          CatalogConverter.getFieldSelectionData(oldConnectionRead.getSyncCatalog()));
      final AirbyteCatalog upToDateAirbyteCatalog = updatedConnectionRead.getSyncCatalog();
      final CatalogDiff catalogDiff =
          connectionsHandler.getDiff(apiExistingCatalog, upToDateAirbyteCatalog, CatalogConverter.toConfiguredProtocol(upToDateAirbyteCatalog));
      final List<StreamDescriptor> apiStreamsToReset = getStreamsToReset(catalogDiff);
      final Set<StreamDescriptor> changedConfigStreamDescriptors =
          connectionsHandler.getConfigurationDiff(apiExistingCatalog, upToDateAirbyteCatalog);
      final Set<StreamDescriptor> allStreamToReset = new HashSet<>();
      allStreamToReset.addAll(apiStreamsToReset);
      allStreamToReset.addAll(changedConfigStreamDescriptors);
      List<io.airbyte.protocol.models.StreamDescriptor> streamsToReset =
          allStreamToReset.stream().map(ProtocolConverters::streamDescriptorToProtocol).toList();

      if (!streamsToReset.isEmpty()) {
        final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody().connectionId(connectionId);
        final ConnectionStateType stateType = getStateType(connectionIdRequestBody);

        if (stateType == ConnectionStateType.LEGACY || stateType == ConnectionStateType.NOT_SET) {
          streamsToReset = configRepository.getAllStreamsForConnection(connectionId);
        }
        eventRunner.resetConnection(
            connectionId,
            streamsToReset, true);
      }
    }
  }

  private List<UUID> createOperations(final WebBackendConnectionCreate webBackendConnectionCreate)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    if (webBackendConnectionCreate.getOperations() == null) {
      return Collections.emptyList();
    }
    final List<UUID> operationIds = new ArrayList<>();
    for (final var operationCreate : webBackendConnectionCreate.getOperations()) {
      operationIds.add(operationsHandler.createOperation(operationCreate).getOperationId());
    }
    return operationIds;
  }

  private List<UUID> createOrUpdateOperations(final ConnectionRead connectionRead, final WebBackendConnectionUpdate webBackendConnectionPatch)
      throws JsonValidationException, ConfigNotFoundException, IOException {

    // this is a patch-style update, so don't make any changes if the request doesn't include operations
    if (webBackendConnectionPatch.getOperations() == null) {
      return null;
    }

    // wrap operationIds in a new ArrayList so that it is modifiable below, when calling .removeAll
    final List<UUID> originalOperationIds =
        connectionRead.getOperationIds() == null ? new ArrayList<>() : new ArrayList<>(connectionRead.getOperationIds());

    final List<WebBackendOperationCreateOrUpdate> updatedOperations = webBackendConnectionPatch.getOperations();
    final List<UUID> finalOperationIds = new ArrayList<>();

    for (final var operationCreateOrUpdate : updatedOperations) {
      if (operationCreateOrUpdate.getOperationId() == null || !originalOperationIds.contains(operationCreateOrUpdate.getOperationId())) {
        final OperationCreate operationCreate = toOperationCreate(operationCreateOrUpdate);
        finalOperationIds.add(operationsHandler.createOperation(operationCreate).getOperationId());
      } else {
        final OperationUpdate operationUpdate = toOperationUpdate(operationCreateOrUpdate);
        finalOperationIds.add(operationsHandler.updateOperation(operationUpdate).getOperationId());
      }
    }

    // remove operationIds that weren't included in the update
    originalOperationIds.removeAll(finalOperationIds);
    operationsHandler.deleteOperationsForConnection(connectionRead.getConnectionId(), originalOperationIds);
    return finalOperationIds;
  }

  @VisibleForTesting
  protected static OperationCreate toOperationCreate(final WebBackendOperationCreateOrUpdate operationCreateOrUpdate) {
    final OperationCreate operationCreate = new OperationCreate();

    operationCreate.name(operationCreateOrUpdate.getName());
    operationCreate.workspaceId(operationCreateOrUpdate.getWorkspaceId());
    operationCreate.operatorConfiguration(operationCreateOrUpdate.getOperatorConfiguration());

    return operationCreate;
  }

  @VisibleForTesting
  protected static OperationUpdate toOperationUpdate(final WebBackendOperationCreateOrUpdate operationCreateOrUpdate) {
    final OperationUpdate operationUpdate = new OperationUpdate();

    operationUpdate.operationId(operationCreateOrUpdate.getOperationId());
    operationUpdate.name(operationCreateOrUpdate.getName());
    operationUpdate.operatorConfiguration(operationCreateOrUpdate.getOperatorConfiguration());

    return operationUpdate;
  }

  @VisibleForTesting
  protected static ConnectionCreate toConnectionCreate(final WebBackendConnectionCreate webBackendConnectionCreate, final List<UUID> operationIds) {
    final ConnectionCreate connectionCreate = new ConnectionCreate();

    connectionCreate.name(webBackendConnectionCreate.getName());
    connectionCreate.namespaceDefinition(webBackendConnectionCreate.getNamespaceDefinition());
    connectionCreate.namespaceFormat(webBackendConnectionCreate.getNamespaceFormat());
    connectionCreate.prefix(webBackendConnectionCreate.getPrefix());
    connectionCreate.sourceId(webBackendConnectionCreate.getSourceId());
    connectionCreate.destinationId(webBackendConnectionCreate.getDestinationId());
    connectionCreate.operationIds(operationIds);
    connectionCreate.syncCatalog(webBackendConnectionCreate.getSyncCatalog());
    connectionCreate.schedule(webBackendConnectionCreate.getSchedule());
    connectionCreate.scheduleType(webBackendConnectionCreate.getScheduleType());
    connectionCreate.scheduleData(webBackendConnectionCreate.getScheduleData());
    connectionCreate.status(webBackendConnectionCreate.getStatus());
    connectionCreate.resourceRequirements(webBackendConnectionCreate.getResourceRequirements());
    connectionCreate.sourceCatalogId(webBackendConnectionCreate.getSourceCatalogId());
    connectionCreate.geography(webBackendConnectionCreate.getGeography());
    connectionCreate.nonBreakingChangesPreference(webBackendConnectionCreate.getNonBreakingChangesPreference());

    return connectionCreate;
  }

  /**
   * Take in a WebBackendConnectionUpdate and convert it into a ConnectionUpdate. OperationIds are
   * handled as a special case because the WebBackendConnectionUpdate handler allows for on-the-fly
   * creation of new operations. So, the brand-new IDs are passed in because they aren't present in
   * the WebBackendConnectionUpdate itself.
   *
   * The return value is used as a patch -- a field set to null means that it should not be modified.
   */
  @VisibleForTesting
  protected static ConnectionUpdate toConnectionPatch(final WebBackendConnectionUpdate webBackendConnectionPatch,
                                                      final List<UUID> finalOperationIds,
                                                      boolean breakingChange) {
    final ConnectionUpdate connectionPatch = new ConnectionUpdate();

    connectionPatch.connectionId(webBackendConnectionPatch.getConnectionId());
    connectionPatch.namespaceDefinition(webBackendConnectionPatch.getNamespaceDefinition());
    connectionPatch.namespaceFormat(webBackendConnectionPatch.getNamespaceFormat());
    connectionPatch.prefix(webBackendConnectionPatch.getPrefix());
    connectionPatch.name(webBackendConnectionPatch.getName());
    connectionPatch.syncCatalog(webBackendConnectionPatch.getSyncCatalog());
    connectionPatch.schedule(webBackendConnectionPatch.getSchedule());
    connectionPatch.scheduleType(webBackendConnectionPatch.getScheduleType());
    connectionPatch.scheduleData(webBackendConnectionPatch.getScheduleData());
    connectionPatch.status(webBackendConnectionPatch.getStatus());
    connectionPatch.resourceRequirements(webBackendConnectionPatch.getResourceRequirements());
    connectionPatch.sourceCatalogId(webBackendConnectionPatch.getSourceCatalogId());
    connectionPatch.geography(webBackendConnectionPatch.getGeography());
    connectionPatch.notifySchemaChanges(webBackendConnectionPatch.getNotifySchemaChanges());
    connectionPatch.nonBreakingChangesPreference(webBackendConnectionPatch.getNonBreakingChangesPreference());
    connectionPatch.breakingChange(breakingChange);

    connectionPatch.operationIds(finalOperationIds);

    return connectionPatch;
  }

  @VisibleForTesting
  static List<StreamDescriptor> getStreamsToReset(final CatalogDiff catalogDiff) {
    return catalogDiff.getTransforms().stream().map(StreamTransform::getStreamDescriptor).toList();
  }

  /**
   * Equivalent to {@see io.airbyte.integrations.base.AirbyteStreamNameNamespacePair}. Intentionally
   * not using that class because it doesn't make sense for airbyte-server to depend on
   * base-java-integration.
   */
  private record Stream(String name, String namespace) {

  }

  private boolean containsBreakingChange(final CatalogDiff diff) {
    for (final StreamTransform streamTransform : diff.getTransforms()) {
      if (streamTransform.getTransformType() != TransformTypeEnum.UPDATE_STREAM) {
        continue;
      }

      final boolean anyBreakingFieldTransforms = streamTransform.getUpdateStream().stream().anyMatch(FieldTransform::getBreaking);
      if (anyBreakingFieldTransforms) {
        return true;
      }
    }

    return false;
  }

}
