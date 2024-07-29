/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static java.util.stream.Collectors.toMap;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.api.model.generated.*;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.MoreBooleans;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.scheduler.client.EventRunner;
import io.airbyte.server.converters.ApiPojoConverters;
import io.airbyte.server.handlers.helpers.CatalogConverter;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.helper.ProtocolConverters;
import io.airbyte.workers.temporal.TemporalClient.ManualOperationResult;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.ObjectUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@AllArgsConstructor
@Slf4j
public class WebBackendConnectionsHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConnectionsHandler.class);

  private static final Set<JobStatus> TERMINAL_STATUSES = Sets.newHashSet(JobStatus.FAILED, JobStatus.SUCCEEDED, JobStatus.CANCELLED);

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

  public WebBackendConnectionReadList webBackendListConnectionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {

    final List<WebBackendConnectionRead> reads = Lists.newArrayList();
    for (final ConnectionRead connection : connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody).getConnections()) {
      reads.add(buildWebBackendConnectionRead(connection));
    }
    return new WebBackendConnectionReadList().connections(reads);
  }

  public WebBackendConnectionPageReadList webBackendPageConnectionsForWorkspace(WorkspaceIdPageRequestBody workspaceIdPageRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<WebBackendConnectionRead> reads = Lists.newArrayList();
    if (workspaceIdPageRequestBody.getPageSize() == null || workspaceIdPageRequestBody.getPageSize() == 0) {
      workspaceIdPageRequestBody.setPageSize(10);
    }
    if (workspaceIdPageRequestBody.getPageCurrent() == null || workspaceIdPageRequestBody.getPageCurrent() == 0) {
      workspaceIdPageRequestBody.setPageCurrent(1);
    }
    for (final ConnectionRead connection : connectionsHandler.pageConnectionsForWorkspace(workspaceIdPageRequestBody).getConnections()) {
      reads.add(buildWebBackendConnectionRead(connection));
    }
    return new WebBackendConnectionPageReadList().connections(reads)
        .total(connectionsHandler.pageConnectionsForWorkspaceCount(workspaceIdPageRequestBody))
        .pageCurrent(workspaceIdPageRequestBody.getPageCurrent()).pageSize(workspaceIdPageRequestBody.getPageSize());
  }

  public WebBackendConnectionsPageReadList webBackendConnectionsPageForWorkspace(WorkspaceIdPageRequestBody workspaceIdPageRequestBody)
      throws IOException {
    final List<WebBackendConnectionPageRead> reads = Lists.newArrayList();
    if (workspaceIdPageRequestBody.getPageSize() == null || workspaceIdPageRequestBody.getPageSize() == 0) {
      workspaceIdPageRequestBody.setPageSize(10);
    }
    if (workspaceIdPageRequestBody.getPageCurrent() == null || workspaceIdPageRequestBody.getPageCurrent() == 0) {
      workspaceIdPageRequestBody.setPageCurrent(1);
    }
    long startTime = System.nanoTime();
    for (final ConnectionRead connection : connectionsHandler.connectionPageReadList(workspaceIdPageRequestBody).getConnections()) {
      reads.add(buildWebBackendConnectionPageRead(connection));
    }
    long elapsedTimeInNano = System.nanoTime() - startTime;
    double elapsedTimeInMilli = (double) elapsedTimeInNano / 1_000_000;
    LOGGER.info("webBackendConnectionsPageForWorkspace spends {} milliseconds", elapsedTimeInMilli);

    return new WebBackendConnectionsPageReadList().connections(reads)
        .total(connectionsHandler.pageConnectionsForWorkspaceCount(workspaceIdPageRequestBody))
        .pageCurrent(workspaceIdPageRequestBody.getPageCurrent()).pageSize(workspaceIdPageRequestBody.getPageSize());
  }

  public WebBackendConnectionStatusReadList webBackendConnectionStatusForWorkspace(ConnectionIdListRequestBody connectionIdListRequestBody)
      throws IOException {
    List<String> connectionIds = connectionIdListRequestBody.getConnectionIds().stream()
        .map(UUID::toString).collect(Collectors.toList());
    List<JobRead> jobReads = jobHistoryHandler.latestJobListFor(connectionIds);
    List<WebBackendConnectionStatusRead> connectionStatusList = new ArrayList<>();
    for (JobRead data : jobReads) {
      connectionStatusList.add(new WebBackendConnectionStatusRead().connectionId(UUID.fromString(data.getConfigId()))
          .latestSyncJobStatus(data.getStatus()).latestSyncJobCreatedAt(data.getCreatedAt()));
    }
    return new WebBackendConnectionStatusReadList().connectionStatusList(connectionStatusList);
  }

  public WebBackendConnectionFilterParam webBackendConnectionsFilterParam(final WorkspaceIdRequestBody workspaceIdRequestBody)
      throws IOException {
    return new WebBackendConnectionFilterParam()
        .status(connectionsHandler.listStatus())
        .sources(sourceHandler.listFilterParam(workspaceIdRequestBody.getWorkspaceId()))
        .destinations(destinationHandler.listFilterParam(workspaceIdRequestBody.getWorkspaceId()));
  }

  public WebBackendConnectionReadList webBackendListAllConnectionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {

    final List<WebBackendConnectionRead> reads = Lists.newArrayList();
    for (final ConnectionRead connection : connectionsHandler.listAllConnectionsForWorkspace(workspaceIdRequestBody).getConnections()) {
      reads.add(buildWebBackendConnectionRead(connection));
    }
    return new WebBackendConnectionReadList().connections(reads);
  }

  private WebBackendConnectionRead buildWebBackendConnectionRead(final ConnectionRead connectionRead)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final SourceRead source = getSourceRead(connectionRead);
    final DestinationRead destination = getDestinationRead(connectionRead);
    final OperationReadList operations = getOperationReadList(connectionRead);
    final JobReadList syncJobReadList = getSyncJobs(connectionRead);

    final WebBackendConnectionRead webBackendConnectionRead = getWebBackendConnectionRead(connectionRead, source, destination, operations)
        .catalogId(connectionRead.getSourceCatalogId())
        .isSyncing(syncJobReadList.getJobs()
            .stream()
            .map(JobWithAttemptsRead::getJob)
            .anyMatch(WebBackendConnectionsHandler::isRunningJob));
    setLatestSyncJobProperties(webBackendConnectionRead, syncJobReadList);
    return webBackendConnectionRead;
  }

  private WebBackendConnectionPageRead buildWebBackendConnectionPageRead(final ConnectionRead connectionRead)
      throws IOException {
    long startTime = System.nanoTime();
    StandardDestinationDefinition destinationDefinition =
        configRepository.getStandardDestinationDefinationByDestinationId(connectionRead.getDestinationId());
    StandardDestinationDefinition sourceDefinition = configRepository.getStandardSourceDefinationBySourceId(connectionRead.getSourceId());

    long elapsedTimeInNano = System.nanoTime() - startTime;
    double elapsedTimeInMilli = (double) elapsedTimeInNano / 1_000_000;
    LOGGER.info("buildWebBackendConnectionPageRead part 0 spends {} milliseconds", elapsedTimeInMilli);

    startTime = System.nanoTime();
    WebBackendConnectionPageRead webBackendConnectionPageRead = new WebBackendConnectionPageRead().connectionId(connectionRead.getConnectionId())
        .name(connectionRead.getName()).status(connectionRead.getStatus()).entityName(destinationDefinition.getName())
        .connectorName(sourceDefinition.getName());

    elapsedTimeInNano = System.nanoTime() - startTime;
    elapsedTimeInMilli = (double) elapsedTimeInNano / 1_000_000;
    LOGGER.info("buildWebBackendConnectionPageRead part 2 spends {} milliseconds", elapsedTimeInMilli);

    return webBackendConnectionPageRead;
  }

  public WebBackendConnectionList listConnectionsPageWithoutOperation(final UUID workspaceId,
                                                                      UUID sourceId,
                                                                      UUID destinationId,
                                                                      final Integer pageSize,
                                                                      final Integer pageCurrent)
      throws IOException {
    final List<ConnectionRead> connectionReads = Lists.newArrayList();
    if (!ObjectUtils.isEmpty(sourceId)) {
      for (final StandardSync standardSync : configRepository.listSourceStandardSyncsWithoutOperations(workspaceId, sourceId, pageSize,
          pageCurrent)) {
        connectionReads.add(ApiPojoConverters.internalToConnectionPageRead(standardSync));
      }
    } else if (!ObjectUtils.isEmpty(destinationId)) {
      for (final StandardSync standardSync : configRepository.listDestinationStandardSyncsWithoutOperations(workspaceId, destinationId, pageSize,
          pageCurrent)) {
        connectionReads.add(ApiPojoConverters.internalToConnectionPageRead(standardSync));
      }
    }
    final List<WebBackendConnectionPageRead> reads = Lists.newArrayList();
    for (final ConnectionRead connection : connectionReads) {
      reads.add(buildWebBackendConnectionPageRead(connection));
    }
    return new WebBackendConnectionList().connections(reads);
  }

  private static boolean isRunningJob(final JobRead job) {
    return !TERMINAL_STATUSES.contains(job.getStatus());
  }

  private SourceRead getSourceRead(final ConnectionRead connectionRead) throws JsonValidationException, IOException, ConfigNotFoundException {
    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody().sourceId(connectionRead.getSourceId());
    return sourceHandler.getSource(sourceIdRequestBody);
  }

  private DestinationRead getDestinationRead(final ConnectionRead connectionRead)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final DestinationIdRequestBody destinationIdRequestBody = new DestinationIdRequestBody().destinationId(connectionRead.getDestinationId());
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
        .advanceSetting(connectionRead.getAdvanceSetting())
        .resourceRequirements(connectionRead.getResourceRequirements());
  }

  private JobReadList getSyncJobs(final ConnectionRead connectionRead) throws IOException {
    final JobListRequestBody jobListRequestBody = new JobListRequestBody()
        .configId(connectionRead.getConnectionId().toString())
        .configTypes(Collections.singletonList(JobConfigType.SYNC));
    return jobHistoryHandler.listJobsFor(jobListRequestBody);
  }

  private static void setLatestSyncJobProperties(final WebBackendConnectionRead WebBackendConnectionRead, final JobReadList syncJobReadList) {
    syncJobReadList.getJobs().stream().map(JobWithAttemptsRead::getJob).findFirst()
        .ifPresent(job -> {
          WebBackendConnectionRead.setLatestSyncJobCreatedAt(job.getCreatedAt());
          WebBackendConnectionRead.setLatestSyncJobStatus(job.getStatus());
        });
  }

  public WebBackendConnectionReadList webBackendSearchConnections(final WebBackendConnectionSearch webBackendConnectionSearch)
      throws ConfigNotFoundException, IOException, JsonValidationException {

    final List<WebBackendConnectionRead> reads = Lists.newArrayList();
    for (final ConnectionRead connectionRead : connectionsHandler.listConnections().getConnections()) {
      if (connectionsHandler.matchSearch(toConnectionSearch(webBackendConnectionSearch), connectionRead)) {
        reads.add(buildWebBackendConnectionRead(connectionRead));
      }
    }

    return new WebBackendConnectionReadList().connections(reads);
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
      refreshedCatalog = getRefreshedSchema(connection.getSourceId());
    } else {
      refreshedCatalog = Optional.empty();
    }

    final CatalogDiff diff;
    final AirbyteCatalog syncCatalog;
    if (refreshedCatalog.isPresent()) {
      connection.setSourceCatalogId(refreshedCatalog.get().getCatalogId());
      /*
       * constructs a full picture of all existing configured + all new / updated streams in the newest
       * catalog.
       */
      syncCatalog = updateSchemaWithDiscovery(configuredCatalog, refreshedCatalog.get().getCatalog());
      /*
       * Diffing the catalog used to make the configured catalog gives us the clearest diff between the
       * schema when the configured catalog was made and now. In the case where we do not have the
       * original catalog used to make the configured catalog, we make due, but using the configured
       * catalog itself. The drawback is that any stream that was not selected in the configured catalog
       * but was present at time of configuration will appear in the diff as an added stream which is
       * confusing. We need to figure out why source_catalog_id is not always populated in the db.
       */
      diff = connectionsHandler.getDiff(catalogUsedToMakeConfiguredCatalog.orElse(configuredCatalog), refreshedCatalog.get().getCatalog());
    } else if (catalogUsedToMakeConfiguredCatalog.isPresent()) {
      // reconstructs a full picture of the full schema at the time the catalog was configured.
      syncCatalog = updateSchemaWithDiscovery(configuredCatalog, catalogUsedToMakeConfiguredCatalog.get());
      // diff not relevant if there was no refresh.
      diff = null;
    } else {
      // fallback. over time this should be rarely used because source_catalog_id should always be set.
      syncCatalog = configuredCatalog;
      // diff not relevant if there was no refresh.
      diff = null;
    }

    connection.setSyncCatalog(syncCatalog);
    return buildWebBackendConnectionRead(connection).catalogDiff(diff);
  }

  private Optional<SourceDiscoverSchemaRead> getRefreshedSchema(final UUID sourceId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final SourceDiscoverSchemaRequestBody discoverSchemaReadReq = new SourceDiscoverSchemaRequestBody()
        .sourceId(sourceId)
        .disableCache(true);
    return Optional.ofNullable(schedulerHandler.discoverSchemaForSourceFromSourceId(discoverSchemaReadReq));
  }

  /**
   * Applies existing configurations to a newly discovered catalog. For example, if the users stream
   * is in the old and new catalog, any configuration that was previously set for users, we add to the
   * new catalog.
   *
   * @param original fully configured, original catalog
   * @param discovered newly discovered catalog, no configurations set
   * @return merged catalog, most up-to-date schema with most up-to-date configurations from old
   *         catalog
   */
  @VisibleForTesting
  protected static AirbyteCatalog updateSchemaWithDiscovery(final AirbyteCatalog original, final AirbyteCatalog discovered) {
    /*
     * We can't directly use s.getStream() as the key, because it contains a bunch of other fields, so
     * we just define a quick-and-dirty record class.
     */
    final Map<Stream, AirbyteStreamAndConfiguration> streamDescriptorToOriginalStream = original.getStreams()
        .stream()
        .collect(toMap(s -> new Stream(s.getStream().getName(), s.getStream().getNamespace()), s -> s));

    final List<AirbyteStreamAndConfiguration> streams = new ArrayList<>();

    for (final AirbyteStreamAndConfiguration discoveredStream : discovered.getStreams()) {
      final AirbyteStream stream = discoveredStream.getStream();
      final AirbyteStreamAndConfiguration originalStream = streamDescriptorToOriginalStream.get(new Stream(stream.getName(), stream.getNamespace()));
      final AirbyteStreamConfiguration outputStreamConfig;

      if (originalStream != null) {
        final AirbyteStreamConfiguration originalStreamConfig = originalStream.getConfig();
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
        outputStreamConfig.setSelected(originalStream.getConfig().getSelected());
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
    return buildWebBackendConnectionRead(connectionsHandler.createConnection(connectionCreate));
  }

  public WebBackendConnectionRead webBackendUpdateConnection(final WebBackendConnectionUpdate webBackendConnectionUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<UUID> operationIds = updateOperations(webBackendConnectionUpdate);
    final ConnectionUpdate connectionUpdate = toConnectionUpdate(webBackendConnectionUpdate, operationIds);
    final UUID connectionId = webBackendConnectionUpdate.getConnectionId();
    final ConfiguredAirbyteCatalog existingConfiguredCatalog =
        configRepository.getConfiguredCatalogForConnection(connectionId);
    ConnectionRead connectionRead;
    connectionRead = connectionsHandler.updateConnection(connectionUpdate);

    final Boolean skipReset = webBackendConnectionUpdate.getSkipReset() != null ? webBackendConnectionUpdate.getSkipReset() : false;
    if (!skipReset) {
      final AirbyteCatalog apiExistingCatalog = CatalogConverter.toApi(existingConfiguredCatalog);
      final AirbyteCatalog newAirbyteCatalog = webBackendConnectionUpdate.getSyncCatalog();
      newAirbyteCatalog
          .setStreams(newAirbyteCatalog.getStreams().stream().filter(streamAndConfig -> streamAndConfig.getConfig().getSelected()).toList());
      final CatalogDiff catalogDiff = connectionsHandler.getDiff(apiExistingCatalog, newAirbyteCatalog);
      final List<StreamDescriptor> apiStreamsToReset = getStreamsToReset(catalogDiff);
      final Set<StreamDescriptor> changedConfigStreamDescriptors = connectionsHandler.getConfigurationDiff(apiExistingCatalog, newAirbyteCatalog);
      final Set<StreamDescriptor> allStreamToReset = new HashSet<>();
      allStreamToReset.addAll(apiStreamsToReset);
      allStreamToReset.addAll(changedConfigStreamDescriptors);
      List<io.airbyte.protocol.models.StreamDescriptor> streamsToReset =
          allStreamToReset.stream().map(ProtocolConverters::streamDescriptorToProtocol).toList();

      if (!streamsToReset.isEmpty()) {
        final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody().connectionId(connectionId);
        final ConnectionStateType stateType = getStateType(connectionIdRequestBody);

        if (stateType == ConnectionStateType.LEGACY) {
          streamsToReset = configRepository.getAllStreamsForConnection(connectionId);
        }
        ManualOperationResult manualOperationResult = eventRunner.synchronousResetConnection(
            webBackendConnectionUpdate.getConnectionId(),
            streamsToReset);
        verifyManualOperationResult(manualOperationResult);
        manualOperationResult = eventRunner.startNewManualSync(webBackendConnectionUpdate.getConnectionId());
        verifyManualOperationResult(manualOperationResult);
        connectionRead = connectionsHandler.getConnection(connectionUpdate.getConnectionId());
      }
    }

    /*
     * This catalog represents the full catalog that was used to create the configured catalog. It will
     * have all streams that were present at the time. It will have no configuration set.
     */
    final Optional<AirbyteCatalog> catalogUsedToMakeConfiguredCatalog = connectionsHandler
        .getConnectionAirbyteCatalog(connectionId);
    if (catalogUsedToMakeConfiguredCatalog.isPresent()) {
      // Update the Catalog returned to include all streams, including disabled ones
      final AirbyteCatalog syncCatalog = updateSchemaWithDiscovery(connectionRead.getSyncCatalog(), catalogUsedToMakeConfiguredCatalog.get());
      connectionRead.setSyncCatalog(syncCatalog);
    }

    return buildWebBackendConnectionRead(connectionRead);
  }

  private void verifyManualOperationResult(final ManualOperationResult manualOperationResult) throws IllegalStateException {
    if (manualOperationResult.getFailingReason().isPresent()) {
      throw new IllegalStateException(manualOperationResult.getFailingReason().get());
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

  private List<UUID> updateOperations(final WebBackendConnectionUpdate webBackendConnectionUpdate)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final ConnectionRead connectionRead = connectionsHandler
        .getConnection(webBackendConnectionUpdate.getConnectionId());

    // wrap operationIds in a new ArrayList so that it is modifiable below, when calling .removeAll
    final List<UUID> originalOperationIds =
        connectionRead.getOperationIds() == null ? new ArrayList<>() : new ArrayList<>(connectionRead.getOperationIds());

    final List<WebBackendOperationCreateOrUpdate> updatedOperations =
        webBackendConnectionUpdate.getOperations() == null ? new ArrayList<>() : webBackendConnectionUpdate.getOperations();

    final List<UUID> operationIds = new ArrayList<>();

    for (final var operationCreateOrUpdate : updatedOperations) {
      if (operationCreateOrUpdate.getOperationId() == null || !originalOperationIds.contains(operationCreateOrUpdate.getOperationId())) {
        final OperationCreate operationCreate = toOperationCreate(operationCreateOrUpdate);
        operationIds.add(operationsHandler.createOperation(operationCreate).getOperationId());
      } else {
        final OperationUpdate operationUpdate = toOperationUpdate(operationCreateOrUpdate);
        operationIds.add(operationsHandler.updateOperation(operationUpdate).getOperationId());
      }
    }

    originalOperationIds.removeAll(operationIds);
    operationsHandler.deleteOperationsForConnection(connectionRead.getConnectionId(), originalOperationIds);
    return operationIds;
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
    connectionCreate.advanceSetting(webBackendConnectionCreate.getAdvanceSetting());
    return connectionCreate;
  }

  @VisibleForTesting
  protected static ConnectionUpdate toConnectionUpdate(final WebBackendConnectionUpdate webBackendConnectionUpdate, final List<UUID> operationIds) {
    final ConnectionUpdate connectionUpdate = new ConnectionUpdate();

    connectionUpdate.connectionId(webBackendConnectionUpdate.getConnectionId());
    connectionUpdate.namespaceDefinition(webBackendConnectionUpdate.getNamespaceDefinition());
    connectionUpdate.namespaceFormat(webBackendConnectionUpdate.getNamespaceFormat());
    connectionUpdate.prefix(webBackendConnectionUpdate.getPrefix());
    connectionUpdate.name(webBackendConnectionUpdate.getName());
    connectionUpdate.operationIds(operationIds);
    connectionUpdate.syncCatalog(webBackendConnectionUpdate.getSyncCatalog());
    connectionUpdate.schedule(webBackendConnectionUpdate.getSchedule());
    connectionUpdate.scheduleType(webBackendConnectionUpdate.getScheduleType());
    connectionUpdate.scheduleData(webBackendConnectionUpdate.getScheduleData());
    connectionUpdate.status(webBackendConnectionUpdate.getStatus());
    connectionUpdate.resourceRequirements(webBackendConnectionUpdate.getResourceRequirements());
    connectionUpdate.sourceCatalogId(webBackendConnectionUpdate.getSourceCatalogId());
    connectionUpdate.setAdvanceSetting(webBackendConnectionUpdate.getAdvanceSetting());
    return connectionUpdate;
  }

  @VisibleForTesting
  protected static ConnectionSearch toConnectionSearch(final WebBackendConnectionSearch webBackendConnectionSearch) {
    return new ConnectionSearch()
        .name(webBackendConnectionSearch.getName())
        .connectionId(webBackendConnectionSearch.getConnectionId())
        .source(webBackendConnectionSearch.getSource())
        .sourceId(webBackendConnectionSearch.getSourceId())
        .destination(webBackendConnectionSearch.getDestination())
        .destinationId(webBackendConnectionSearch.getDestinationId())
        .namespaceDefinition(webBackendConnectionSearch.getNamespaceDefinition())
        .namespaceFormat(webBackendConnectionSearch.getNamespaceFormat())
        .prefix(webBackendConnectionSearch.getPrefix())
        .schedule(webBackendConnectionSearch.getSchedule())
        .scheduleType(webBackendConnectionSearch.getScheduleType())
        .scheduleData(webBackendConnectionSearch.getScheduleData())
        .status(webBackendConnectionSearch.getStatus());
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

}
