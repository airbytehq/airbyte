/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import com.google.common.collect.Lists;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.api.model.generated.AirbyteCatalog;
import io.airbyte.api.model.generated.AirbyteStreamConfiguration;
import io.airbyte.api.model.generated.CatalogDiff;
import io.airbyte.api.model.generated.ConnectionCreate;
import io.airbyte.api.model.generated.ConnectionRead;
import io.airbyte.api.model.generated.ConnectionReadList;
import io.airbyte.api.model.generated.ConnectionSearch;
import io.airbyte.api.model.generated.ConnectionUpdate;
import io.airbyte.api.model.generated.DestinationRead;
import io.airbyte.api.model.generated.DestinationSearch;
import io.airbyte.api.model.generated.SourceRead;
import io.airbyte.api.model.generated.SourceSearch;
import io.airbyte.api.model.generated.StreamDescriptor;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ActorCatalog;
import io.airbyte.config.BasicSchedule;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.Schedule;
import io.airbyte.config.ScheduleData;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.ScheduleType;
import io.airbyte.config.helpers.ScheduleHelpers;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.scheduler.client.EventRunner;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.server.converters.ApiPojoConverters;
import io.airbyte.server.converters.CatalogDiffConverters;
import io.airbyte.server.handlers.helpers.CatalogConverter;
import io.airbyte.server.handlers.helpers.ConnectionMatcher;
import io.airbyte.server.handlers.helpers.ConnectionScheduleHelper;
import io.airbyte.server.handlers.helpers.DestinationMatcher;
import io.airbyte.server.handlers.helpers.SourceMatcher;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.helper.ConnectionHelper;
import java.io.IOException;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConnectionsHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConnectionsHandler.class);

  private final ConfigRepository configRepository;
  private final Supplier<UUID> uuidGenerator;
  private final WorkspaceHelper workspaceHelper;
  private final TrackingClient trackingClient;
  private final EventRunner eventRunner;

  @VisibleForTesting
  ConnectionsHandler(final ConfigRepository configRepository,
                     final Supplier<UUID> uuidGenerator,
                     final WorkspaceHelper workspaceHelper,
                     final TrackingClient trackingClient,
                     final EventRunner eventRunner) {
    this.configRepository = configRepository;
    this.uuidGenerator = uuidGenerator;
    this.workspaceHelper = workspaceHelper;
    this.trackingClient = trackingClient;
    this.eventRunner = eventRunner;
  }

  public ConnectionsHandler(final ConfigRepository configRepository,
                            final WorkspaceHelper workspaceHelper,
                            final TrackingClient trackingClient,
                            final EventRunner eventRunner) {
    this(configRepository,
        UUID::randomUUID,
        workspaceHelper,
        trackingClient,
        eventRunner);

  }

  public ConnectionRead createConnection(final ConnectionCreate connectionCreate)
      throws JsonValidationException, IOException, ConfigNotFoundException {

    // Validate source and destination
    final SourceConnection sourceConnection = configRepository.getSourceConnection(connectionCreate.getSourceId());
    final DestinationConnection destinationConnection = configRepository.getDestinationConnection(connectionCreate.getDestinationId());

    // Set this as default name if connectionCreate doesn't have it
    final String defaultName = sourceConnection.getName() + " <> " + destinationConnection.getName();

    final List<UUID> operationIds = connectionCreate.getOperationIds() != null ? connectionCreate.getOperationIds() : Collections.emptyList();

    ConnectionHelper.validateWorkspace(workspaceHelper,
        connectionCreate.getSourceId(),
        connectionCreate.getDestinationId(),
        new HashSet<>(operationIds));

    final UUID connectionId = uuidGenerator.get();

    // persist sync
    final StandardSync standardSync = new StandardSync()
        .withConnectionId(connectionId)
        .withName(connectionCreate.getName() != null ? connectionCreate.getName() : defaultName)
        .withNamespaceDefinition(Enums.convertTo(connectionCreate.getNamespaceDefinition(), NamespaceDefinitionType.class))
        .withNamespaceFormat(connectionCreate.getNamespaceFormat())
        .withPrefix(connectionCreate.getPrefix())
        .withSourceId(connectionCreate.getSourceId())
        .withDestinationId(connectionCreate.getDestinationId())
        .withOperationIds(operationIds)
        .withStatus(ApiPojoConverters.toPersistenceStatus(connectionCreate.getStatus()))
        .withSourceCatalogId(connectionCreate.getSourceCatalogId());
    if (connectionCreate.getResourceRequirements() != null) {
      standardSync.withResourceRequirements(ApiPojoConverters.resourceRequirementsToInternal(connectionCreate.getResourceRequirements()));
    }

    // TODO Undesirable behavior: sending a null configured catalog should not be valid?
    if (connectionCreate.getSyncCatalog() != null) {
      standardSync.withCatalog(CatalogConverter.toProtocol(connectionCreate.getSyncCatalog()));
    } else {
      standardSync.withCatalog(new ConfiguredAirbyteCatalog().withStreams(Collections.emptyList()));
    }

    if (connectionCreate.getSchedule() != null && connectionCreate.getScheduleType() != null) {
      throw new JsonValidationException("supply old or new schedule schema but not both");
    }

    if (connectionCreate.getScheduleType() != null) {
      ConnectionScheduleHelper.populateSyncFromScheduleTypeAndData(standardSync, connectionCreate.getScheduleType(),
          connectionCreate.getScheduleData());
    } else {
      populateSyncFromLegacySchedule(standardSync, connectionCreate);
    }

    configRepository.writeStandardSync(standardSync);

    trackNewConnection(standardSync);

    try {
      LOGGER.info("Starting a connection manager workflow");
      eventRunner.createConnectionManagerWorkflow(connectionId);
    } catch (final Exception e) {
      LOGGER.error("Start of the connection manager workflow failed", e);
      configRepository.deleteStandardSyncDefinition(standardSync.getConnectionId());
      throw e;
    }

    return buildConnectionRead(connectionId);
  }

  private void populateSyncFromLegacySchedule(final StandardSync standardSync, final ConnectionCreate connectionCreate) {
    if (connectionCreate.getSchedule() != null) {
      final Schedule schedule = new Schedule()
          .withTimeUnit(ApiPojoConverters.toPersistenceTimeUnit(connectionCreate.getSchedule().getTimeUnit()))
          .withUnits(connectionCreate.getSchedule().getUnits());
      // Populate the legacy field.
      // TODO(https://github.com/airbytehq/airbyte/issues/11432): remove.
      standardSync
          .withManual(false)
          .withSchedule(schedule);
      // Also write into the new field. This one will be consumed if populated.
      standardSync
          .withScheduleType(ScheduleType.BASIC_SCHEDULE);
      standardSync.withScheduleData(new ScheduleData().withBasicSchedule(
          new BasicSchedule().withTimeUnit(ApiPojoConverters.toBasicScheduleTimeUnit(connectionCreate.getSchedule().getTimeUnit()))
              .withUnits(connectionCreate.getSchedule().getUnits())));
    } else {
      standardSync.withManual(true);
      standardSync.withScheduleType(ScheduleType.MANUAL);
    }
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
    // retrieve and update sync
    final StandardSync persistedSync = configRepository.getStandardSync(connectionUpdate.getConnectionId());

    final StandardSync newConnection = ConnectionHelper.updateConnectionObject(
        workspaceHelper,
        persistedSync,
        ApiPojoConverters.connectionUpdateToInternal(connectionUpdate));
    ConnectionHelper.validateWorkspace(
        workspaceHelper,
        persistedSync.getSourceId(),
        persistedSync.getDestinationId(),
        new HashSet<>(connectionUpdate.getOperationIds()));

    configRepository.writeStandardSync(newConnection);

    eventRunner.update(connectionUpdate.getConnectionId());

    return buildConnectionRead(connectionUpdate.getConnectionId());
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

    for (final StandardSync standardSync : configRepository.listWorkspaceStandardSyncs(workspaceIdRequestBody.getWorkspaceId())) {
      if (standardSync.getStatus() == StandardSync.Status.DEPRECATED && !includeDeleted) {
        continue;
      }

      connectionReads.add(ApiPojoConverters.internalToConnectionRead(standardSync));
    }

    return new ConnectionReadList().connections(connectionReads);
  }

  public ConnectionReadList listConnections() throws JsonValidationException, ConfigNotFoundException, IOException {
    final List<ConnectionRead> connectionReads = Lists.newArrayList();

    for (final StandardSync standardSync : configRepository.listStandardSyncs()) {
      if (standardSync.getStatus() == StandardSync.Status.DEPRECATED) {
        continue;
      }
      connectionReads.add(ApiPojoConverters.internalToConnectionRead(standardSync));
    }

    return new ConnectionReadList().connections(connectionReads);
  }

  public ConnectionRead getConnection(final UUID connectionId)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return buildConnectionRead(connectionId);
  }

  public CatalogDiff getDiff(final AirbyteCatalog oldCatalog, final AirbyteCatalog newCatalog) {
    return new CatalogDiff().transforms(CatalogHelpers.getCatalogDiff(
        CatalogHelpers.configuredCatalogToCatalog(CatalogConverter.toProtocolKeepAllStreams(oldCatalog)),
        CatalogHelpers.configuredCatalogToCatalog(CatalogConverter.toProtocolKeepAllStreams(newCatalog)))
        .stream()
        .map(CatalogDiffConverters::streamTransformToApi)
        .toList());
  }

  /**
   * Returns the list of the streamDescriptor that have their config updated.
   *
   * @param oldCatalog the old catalog
   * @param newCatalog the new catalog
   * @return the list of StreamDescriptor that have their configuration changed
   */
  public Set<StreamDescriptor> getConfigurationDiff(final AirbyteCatalog oldCatalog, final AirbyteCatalog newCatalog) {
    final Map<StreamDescriptor, AirbyteStreamConfiguration> oldStreams = catalogToPerStreamConfiguration(oldCatalog);
    final Map<StreamDescriptor, AirbyteStreamConfiguration> newStreams = catalogToPerStreamConfiguration(newCatalog);

    final Set<StreamDescriptor> streamWithDifferentConf = new HashSet<>();

    newStreams.forEach(((streamDescriptor, airbyteStreamConfiguration) -> {
      final AirbyteStreamConfiguration oldConfig = oldStreams.get(streamDescriptor);

      if (oldConfig == null) {
        // The stream is a new one, the config has not change and it needs to be in the schema change list.
      } else {
        if (haveConfigChange(oldConfig, airbyteStreamConfiguration)) {
          streamWithDifferentConf.add(streamDescriptor);
        }
      }
    }));

    return streamWithDifferentConf;
  }

  private boolean haveConfigChange(final AirbyteStreamConfiguration oldConfig, final AirbyteStreamConfiguration newConfig) {
    final List<String> oldCursors = oldConfig.getCursorField();
    final List<String> newCursors = newConfig.getCursorField();
    final boolean hasCursorChanged = !(oldCursors.equals(newCursors));

    final boolean hasSyncModeChanged = !oldConfig.getSyncMode().equals(newConfig.getSyncMode());

    final boolean hasDestinationSyncModeChanged = !oldConfig.getDestinationSyncMode().equals(newConfig.getDestinationSyncMode());

    final Set<List<String>> convertedOldPrimaryKey = new HashSet<>(oldConfig.getPrimaryKey());
    final Set<List<String>> convertedNewPrimaryKey = new HashSet<>(newConfig.getPrimaryKey());
    final boolean hasPrimaryKeyChanged = !(convertedOldPrimaryKey.equals(convertedNewPrimaryKey));

    return hasCursorChanged || hasSyncModeChanged || hasDestinationSyncModeChanged || hasPrimaryKeyChanged;
  }

  private Map<StreamDescriptor, AirbyteStreamConfiguration> catalogToPerStreamConfiguration(final AirbyteCatalog catalog) {
    return catalog.getStreams().stream().collect(Collectors.toMap(stream -> new StreamDescriptor()
        .name(stream.getStream().getName())
        .namespace(stream.getStream().getNamespace()),
        stream -> stream.getConfig()));
  }

  public Optional<AirbyteCatalog> getConnectionAirbyteCatalog(final UUID connectionId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSync connection = configRepository.getStandardSync(connectionId);
    if (connection.getSourceCatalogId() == null) {
      return Optional.empty();
    }
    final ActorCatalog catalog = configRepository.getActorCatalogById(connection.getSourceCatalogId());
    return Optional.of(CatalogConverter.toApi(Jsons.object(catalog.getCatalog(),
        io.airbyte.protocol.models.AirbyteCatalog.class)));
  }

  public ConnectionReadList searchConnections(final ConnectionSearch connectionSearch)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final List<ConnectionRead> reads = Lists.newArrayList();
    for (final StandardSync standardSync : configRepository.listStandardSyncs()) {
      if (standardSync.getStatus() != StandardSync.Status.DEPRECATED) {
        final ConnectionRead connectionRead = ApiPojoConverters.internalToConnectionRead(standardSync);
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

  // todo (cgardens) - make this static. requires removing one bad dependency in SourceHandlerTest
  public boolean matchSearch(final SourceSearch sourceSearch, final SourceRead sourceRead) {
    final SourceMatcher sourceMatcher = new SourceMatcher(sourceSearch);
    final SourceRead sourceReadFromSearch = sourceMatcher.match(sourceRead);

    return (sourceReadFromSearch == null || sourceReadFromSearch.equals(sourceRead));
  }

  // todo (cgardens) - make this static. requires removing one bad dependency in
  // DestinationHandlerTest
  public boolean matchSearch(final DestinationSearch destinationSearch, final DestinationRead destinationRead) {
    final DestinationMatcher destinationMatcher = new DestinationMatcher(destinationSearch);
    final DestinationRead destinationReadFromSearch = destinationMatcher.match(destinationRead);

    return (destinationReadFromSearch == null || destinationReadFromSearch.equals(destinationRead));
  }

  public void deleteConnection(final UUID connectionId) {
    eventRunner.deleteConnection(connectionId);
  }

  private ConnectionRead buildConnectionRead(final UUID connectionId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSync standardSync = configRepository.getStandardSync(connectionId);
    return ApiPojoConverters.internalToConnectionRead(standardSync);
  }

}
