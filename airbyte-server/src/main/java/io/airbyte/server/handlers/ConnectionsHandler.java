/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import com.google.common.collect.Lists;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.api.model.ConnectionCreate;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionReadList;
import io.airbyte.api.model.ConnectionSchedule;
import io.airbyte.api.model.ConnectionSearch;
import io.airbyte.api.model.ConnectionStatus;
import io.airbyte.api.model.ConnectionUpdate;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.api.model.DestinationSearch;
import io.airbyte.api.model.SourceRead;
import io.airbyte.api.model.SourceSearch;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.Schedule;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.helpers.ScheduleHelpers;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.server.handlers.helpers.ConnectionMatcher;
import io.airbyte.server.handlers.helpers.DestinationMatcher;
import io.airbyte.server.handlers.helpers.SourceMatcher;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.helper.CatalogConverter;
import io.airbyte.workers.helper.ConnectionHelper;
import io.airbyte.workers.worker_run.TemporalWorkerRunFactory;
import java.io.IOException;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConnectionsHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConnectionsHandler.class);

  private final ConfigRepository configRepository;
  private final Supplier<UUID> uuidGenerator;
  private final WorkspaceHelper workspaceHelper;
  private final TrackingClient trackingClient;
  private final TemporalWorkerRunFactory temporalWorkerRunFactory;
  private final FeatureFlags featureFlags;
  private final ConnectionHelper connectionHelper;
  private final WorkerConfigs workerConfigs;

  @VisibleForTesting
  ConnectionsHandler(final ConfigRepository configRepository,
                     final Supplier<UUID> uuidGenerator,
                     final WorkspaceHelper workspaceHelper,
                     final TrackingClient trackingClient,
                     final TemporalWorkerRunFactory temporalWorkerRunFactory,
                     final FeatureFlags featureFlags,
                     final ConnectionHelper connectionHelper,
                     final WorkerConfigs workerConfigs) {
    this.configRepository = configRepository;
    this.uuidGenerator = uuidGenerator;
    this.workspaceHelper = workspaceHelper;
    this.trackingClient = trackingClient;
    this.temporalWorkerRunFactory = temporalWorkerRunFactory;
    this.featureFlags = featureFlags;
    this.connectionHelper = connectionHelper;
    this.workerConfigs = workerConfigs;
  }

  public ConnectionsHandler(
                            final ConfigRepository configRepository,
                            final WorkspaceHelper workspaceHelper,
                            final TrackingClient trackingClient,
                            final TemporalWorkerRunFactory temporalWorkerRunFactory,
                            final FeatureFlags featureFlags,
                            final ConnectionHelper connectionHelper,
                            final WorkerConfigs workerConfigs) {
    this(
        configRepository,
        UUID::randomUUID,
        workspaceHelper,
        trackingClient,
        temporalWorkerRunFactory,
        featureFlags,
        connectionHelper,
        workerConfigs);

  }

  public ConnectionRead createConnection(final ConnectionCreate connectionCreate)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    // Validate source and destination
    configRepository.getSourceConnection(connectionCreate.getSourceId());
    configRepository.getDestinationConnection(connectionCreate.getDestinationId());
    connectionHelper.validateWorkspace(connectionCreate.getSourceId(), connectionCreate.getDestinationId(),
        new HashSet<>(connectionCreate.getOperationIds()));

    final UUID connectionId = uuidGenerator.get();

    // persist sync
    final StandardSync standardSync = new StandardSync()
        .withConnectionId(connectionId)
        .withName(connectionCreate.getName() != null ? connectionCreate.getName() : "default")
        .withNamespaceDefinition(Enums.convertTo(connectionCreate.getNamespaceDefinition(), NamespaceDefinitionType.class))
        .withNamespaceFormat(connectionCreate.getNamespaceFormat())
        .withPrefix(connectionCreate.getPrefix())
        .withSourceId(connectionCreate.getSourceId())
        .withDestinationId(connectionCreate.getDestinationId())
        .withOperationIds(connectionCreate.getOperationIds())
        .withStatus(toPersistenceStatus(connectionCreate.getStatus()));
    if (connectionCreate.getResourceRequirements() != null) {
      standardSync.withResourceRequirements(new io.airbyte.config.ResourceRequirements()
          .withCpuRequest(connectionCreate.getResourceRequirements().getCpuRequest())
          .withCpuLimit(connectionCreate.getResourceRequirements().getCpuLimit())
          .withMemoryRequest(connectionCreate.getResourceRequirements().getMemoryRequest())
          .withMemoryLimit(connectionCreate.getResourceRequirements().getMemoryLimit()));
    } else {
      standardSync.withResourceRequirements(workerConfigs.getResourceRequirements());
    }

    // TODO Undesirable behavior: sending a null configured catalog should not be valid?
    if (connectionCreate.getSyncCatalog() != null) {
      standardSync.withCatalog(CatalogConverter.toProtocol(connectionCreate.getSyncCatalog()));
    } else {
      standardSync.withCatalog(new ConfiguredAirbyteCatalog().withStreams(Collections.emptyList()));
    }

    if (connectionCreate.getSchedule() != null) {
      final Schedule schedule = new Schedule()
          .withTimeUnit(toPersistenceTimeUnit(connectionCreate.getSchedule().getTimeUnit()))
          .withUnits(connectionCreate.getSchedule().getUnits());
      standardSync
          .withManual(false)
          .withSchedule(schedule);
    } else {
      standardSync.withManual(true);
    }

    configRepository.writeStandardSync(standardSync);

    trackNewConnection(standardSync);

    if (featureFlags.usesNewScheduler()) {
      try {
        LOGGER.info("Starting a connection using the new scheduler");
        temporalWorkerRunFactory.createNewSchedulerWorkflow(connectionId);
      } catch (final Exception e) {
        LOGGER.error("Start of the temporal connection manager workflow failed", e);
        configRepository.deleteStandardSyncDefinition(standardSync.getConnectionId());
        throw e;
      }
    }

    return connectionHelper.buildConnectionRead(connectionId);
  }

  private void trackNewConnection(final StandardSync standardSync) {
    try {
      final UUID workspaceId = workspaceHelper.getWorkspaceForConnectionIdIgnoreExceptions(standardSync.getConnectionId());
      final Builder<String, Object> metadataBuilder = generateMetadata(standardSync);
      trackingClient.track(workspaceId, "New Connection - Backend", metadataBuilder.build());
    } catch (final Exception e) {
      LOGGER.error("failed while reporting usage.", e);
    }
  }

  private Builder<String, Object> generateMetadata(final StandardSync standardSync) {
    final Builder<String, Object> metadata = ImmutableMap.builder();

    final UUID connectionId = standardSync.getConnectionId();
    final StandardSourceDefinition sourceDefinition = configRepository
        .getSourceDefinitionFromConnection(connectionId);
    final StandardDestinationDefinition destinationDefinition = configRepository
        .getDestinationDefinitionFromConnection(connectionId);

    metadata.put("connector_source", sourceDefinition.getName());
    metadata.put("connector_source_definition_id", sourceDefinition.getSourceDefinitionId());
    metadata.put("connector_destination", destinationDefinition.getName());
    metadata.put("connector_destination_definition_id", destinationDefinition.getDestinationDefinitionId());

    final String frequencyString;
    if (standardSync.getManual()) {
      frequencyString = "manual";
    } else {
      final long intervalInMinutes = TimeUnit.SECONDS.toMinutes(ScheduleHelpers.getIntervalInSecond(standardSync.getSchedule()));
      frequencyString = intervalInMinutes + " min";
    }
    metadata.put("frequency", frequencyString);
    return metadata;
  }

  public ConnectionRead updateConnection(final ConnectionUpdate connectionUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return updateConnection(connectionUpdate, false);
  }

  public ConnectionRead updateConnection(final ConnectionUpdate connectionUpdate, boolean isAReset)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    if (featureFlags.usesNewScheduler()) {
      connectionHelper.updateConnection(connectionUpdate);

      if (!isAReset) {
        temporalWorkerRunFactory.update(connectionUpdate);
      }

      return connectionHelper.buildConnectionRead(connectionUpdate.getConnectionId());
    }
    return connectionHelper.updateConnection(connectionUpdate);
  }

  public ConnectionReadList listConnectionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return listConnectionsForWorkspace(workspaceIdRequestBody, false);
  }

  public ConnectionReadList listAllConnectionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return listConnectionsForWorkspace(workspaceIdRequestBody, true);
  }

  public ConnectionReadList listConnectionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody, final boolean includeDeleted)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final List<ConnectionRead> connectionReads = Lists.newArrayList();

    for (final StandardSync standardSync : configRepository.listStandardSyncs()) {
      if (standardSync.getStatus() == StandardSync.Status.DEPRECATED && !includeDeleted) {
        continue;
      }
      if (!isStandardSyncInWorkspace(workspaceIdRequestBody.getWorkspaceId(), standardSync)) {
        continue;
      }

      connectionReads.add(connectionHelper.buildConnectionRead(standardSync.getConnectionId()));
    }

    return new ConnectionReadList().connections(connectionReads);
  }

  public ConnectionReadList listConnections() throws JsonValidationException, ConfigNotFoundException, IOException {
    final List<ConnectionRead> connectionReads = Lists.newArrayList();

    for (final StandardSync standardSync : configRepository.listStandardSyncs()) {
      if (standardSync.getStatus() == StandardSync.Status.DEPRECATED) {
        continue;
      }
      connectionReads.add(connectionHelper.buildConnectionRead(standardSync.getConnectionId()));
    }

    return new ConnectionReadList().connections(connectionReads);
  }

  public ConnectionRead getConnection(final UUID connectionId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return connectionHelper.buildConnectionRead(connectionId);
  }

  public ConnectionReadList searchConnections(final ConnectionSearch connectionSearch)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final List<ConnectionRead> reads = Lists.newArrayList();
    for (final StandardSync standardSync : configRepository.listStandardSyncs()) {
      if (standardSync.getStatus() != StandardSync.Status.DEPRECATED) {
        final ConnectionRead connectionRead = connectionHelper.buildConnectionRead(standardSync.getConnectionId());
        if (matchSearch(connectionSearch, connectionRead)) {
          reads.add(connectionRead);
        }
      }
    }

    return new ConnectionReadList().connections(reads);
  }

  public boolean matchSearch(final ConnectionSearch connectionSearch, final ConnectionRead connectionRead)
      throws JsonValidationException, ConfigNotFoundException, IOException {

    final SourceConnection sourceConnection = configRepository.getSourceConnection(connectionRead.getSourceId());
    final StandardSourceDefinition sourceDefinition =
        configRepository.getStandardSourceDefinition(sourceConnection.getSourceDefinitionId());
    final SourceRead sourceRead = SourceHandler.toSourceRead(sourceConnection, sourceDefinition);

    final DestinationConnection destinationConnection = configRepository.getDestinationConnection(connectionRead.getDestinationId());
    final StandardDestinationDefinition destinationDefinition =
        configRepository.getStandardDestinationDefinition(destinationConnection.getDestinationDefinitionId());
    final DestinationRead destinationRead = DestinationHandler.toDestinationRead(destinationConnection, destinationDefinition);

    final ConnectionMatcher connectionMatcher = new ConnectionMatcher(connectionSearch);
    final ConnectionRead connectionReadFromSearch = connectionMatcher.match(connectionRead);

    return (connectionReadFromSearch == null || connectionReadFromSearch.equals(connectionRead)) &&
        matchSearch(connectionSearch.getSource(), sourceRead) &&
        matchSearch(connectionSearch.getDestination(), destinationRead);
  }

  public boolean matchSearch(final SourceSearch sourceSearch, final SourceRead sourceRead) {
    final SourceMatcher sourceMatcher = new SourceMatcher(sourceSearch);
    final SourceRead sourceReadFromSearch = sourceMatcher.match(sourceRead);

    return (sourceReadFromSearch == null || sourceReadFromSearch.equals(sourceRead));
  }

  public boolean matchSearch(final DestinationSearch destinationSearch, final DestinationRead destinationRead) {
    final DestinationMatcher destinationMatcher = new DestinationMatcher(destinationSearch);
    final DestinationRead destinationReadFromSearch = destinationMatcher.match(destinationRead);

    return (destinationReadFromSearch == null || destinationReadFromSearch.equals(destinationRead));
  }

  public void deleteConnection(final UUID connectionId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    if (featureFlags.usesNewScheduler()) {
      temporalWorkerRunFactory.deleteConnection(connectionId);
    } else {
      final ConnectionRead connectionRead = getConnection(connectionId);
      deleteConnection(connectionRead);
    }
  }

  public void deleteConnection(final ConnectionRead connectionRead) throws ConfigNotFoundException, IOException, JsonValidationException {
    final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
        .namespaceDefinition(connectionRead.getNamespaceDefinition())
        .namespaceFormat(connectionRead.getNamespaceFormat())
        .prefix(connectionRead.getPrefix())
        .connectionId(connectionRead.getConnectionId())
        .operationIds(connectionRead.getOperationIds())
        .syncCatalog(connectionRead.getSyncCatalog())
        .schedule(connectionRead.getSchedule())
        .status(ConnectionStatus.DEPRECATED)
        .resourceRequirements(connectionRead.getResourceRequirements());

    updateConnection(connectionUpdate);
  }

  private boolean isStandardSyncInWorkspace(final UUID workspaceId,
                                            final StandardSync standardSync)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return configRepository.getSourceConnection(standardSync.getSourceId()).getWorkspaceId().equals(workspaceId);
  }

  private StandardSync.Status toPersistenceStatus(final ConnectionStatus apiStatus) {
    return Enums.convertTo(apiStatus, StandardSync.Status.class);
  }

  private Schedule.TimeUnit toPersistenceTimeUnit(final ConnectionSchedule.TimeUnitEnum apiTimeUnit) {
    return Enums.convertTo(apiTimeUnit, Schedule.TimeUnit.class);
  }

}
