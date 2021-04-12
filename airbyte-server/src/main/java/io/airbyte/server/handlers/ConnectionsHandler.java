/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.server.handlers;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import com.google.common.collect.Lists;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.api.model.ConnectionCreate;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionReadList;
import io.airbyte.api.model.ConnectionSchedule;
import io.airbyte.api.model.ConnectionStatus;
import io.airbyte.api.model.ConnectionUpdate;
import io.airbyte.api.model.SyncMode;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.Schedule;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncSchedule;
import io.airbyte.config.helpers.ScheduleHelpers;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.server.converters.CatalogConverter;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Collections;
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

  @VisibleForTesting
  ConnectionsHandler(final ConfigRepository configRepository, final Supplier<UUID> uuidGenerator) {
    this.configRepository = configRepository;
    this.uuidGenerator = uuidGenerator;
  }

  public ConnectionsHandler(final ConfigRepository configRepository) {
    this(configRepository, UUID::randomUUID);
  }

  public ConnectionRead createConnection(ConnectionCreate connectionCreate) throws JsonValidationException, IOException, ConfigNotFoundException {
    final UUID connectionId = uuidGenerator.get();

    // persist sync
    final StandardSync standardSync = new StandardSync()
        .withConnectionId(connectionId)
        .withName(connectionCreate.getName() != null ? connectionCreate.getName() : "default")
        .withPrefix(connectionCreate.getPrefix())
        .withSourceId(connectionCreate.getSourceId())
        .withDestinationId(connectionCreate.getDestinationId())
        .withStatus(toPersistenceStatus(connectionCreate.getStatus()));

    // TODO Undesirable behavior: sending a null configured catalog should not be valid?
    if (connectionCreate.getSyncCatalog() != null) {
      standardSync.withCatalog(CatalogConverter.toProtocol(connectionCreate.getSyncCatalog()));
    } else {
      standardSync.withCatalog(new ConfiguredAirbyteCatalog().withStreams(Collections.emptyList()));
    }

    configRepository.writeStandardSync(standardSync);

    // persist schedule
    final StandardSyncSchedule standardSyncSchedule = new StandardSyncSchedule().withConnectionId(connectionId);
    if (connectionCreate.getSchedule() != null) {
      final Schedule schedule = new Schedule()
          .withTimeUnit(toPersistenceTimeUnit(connectionCreate.getSchedule().getTimeUnit()))
          .withUnits(connectionCreate.getSchedule().getUnits());
      standardSyncSchedule
          .withManual(false)
          .withSchedule(schedule);
    } else {
      standardSyncSchedule.withManual(true);
    }

    configRepository.writeStandardSchedule(standardSyncSchedule);

    trackNewConnection(standardSync, standardSyncSchedule);

    return buildConnectionRead(connectionId);
  }

  private void trackNewConnection(final StandardSync standardSync, final StandardSyncSchedule standardSyncSchedule) {
    try {
      final Builder<String, Object> metadataBuilder = generateMetadata(standardSync, standardSyncSchedule);
      TrackingClientSingleton.get().track("New Connection - Backend", metadataBuilder.build());
    } catch (Exception e) {
      LOGGER.error("failed while reporting usage.", e);
    }
  }

  private Builder<String, Object> generateMetadata(final StandardSync standardSync, final StandardSyncSchedule standardSyncSchedule) {
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
    if (standardSyncSchedule.getManual()) {
      frequencyString = "manual";
    } else {
      final long intervalInMinutes = TimeUnit.SECONDS.toMinutes(ScheduleHelpers.getIntervalInSecond(standardSyncSchedule.getSchedule()));
      frequencyString = intervalInMinutes + " min";
    }
    metadata.put("frequency", frequencyString);
    return metadata;
  }

  public ConnectionRead updateConnection(ConnectionUpdate connectionUpdate) throws ConfigNotFoundException, IOException, JsonValidationException {
    // retrieve sync
    final StandardSync persistedSync = configRepository.getStandardSync(connectionUpdate.getConnectionId())
        .withPrefix(connectionUpdate.getPrefix())
        .withCatalog(CatalogConverter.toProtocol(connectionUpdate.getSyncCatalog()))
        .withStatus(toPersistenceStatus(connectionUpdate.getStatus()));

    return updateConnection(connectionUpdate, persistedSync);
  }

  public ConnectionRead updateConnection(ConnectionUpdate connectionUpdate, StandardSync persistedSync)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID connectionId = connectionUpdate.getConnectionId();

    // retrieve schedule
    final StandardSyncSchedule persistedSchedule = configRepository.getStandardSyncSchedule(connectionId);
    if (connectionUpdate.getSchedule() != null) {
      final Schedule schedule = new Schedule()
          .withTimeUnit(toPersistenceTimeUnit(connectionUpdate.getSchedule().getTimeUnit()))
          .withUnits(connectionUpdate.getSchedule().getUnits());

      persistedSchedule
          .withSchedule(schedule)
          .withManual(false);
    } else {
      persistedSchedule
          .withSchedule(null)
          .withManual(true);
    }

    configRepository.writeStandardSync(persistedSync);
    configRepository.writeStandardSchedule(persistedSchedule);

    return buildConnectionRead(connectionId);
  }

  public ConnectionReadList listConnectionsForWorkspace(WorkspaceIdRequestBody workspaceIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final List<ConnectionRead> connectionReads = Lists.newArrayList();

    for (StandardSync standardSync : configRepository.listStandardSyncs()) {
      if (standardSync.getStatus() == StandardSync.Status.DEPRECATED) {
        continue;
      }
      if (!isStandardSyncInWorkspace(workspaceIdRequestBody.getWorkspaceId(), standardSync)) {
        continue;
      }

      connectionReads.add(buildConnectionRead(standardSync.getConnectionId()));
    }

    return new ConnectionReadList().connections(connectionReads);
  }

  public ConnectionRead getConnection(ConnectionIdRequestBody connectionIdRequestBody)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    return buildConnectionRead(connectionIdRequestBody.getConnectionId());
  }

  public void deleteConnection(ConnectionIdRequestBody connectionIdRequestBody) throws ConfigNotFoundException, IOException, JsonValidationException {
    final ConnectionRead connectionRead = getConnection(connectionIdRequestBody);
    deleteConnection(connectionRead);
  }

  public void deleteConnection(ConnectionRead connectionRead) throws ConfigNotFoundException, IOException, JsonValidationException {
    final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
        .prefix(connectionRead.getPrefix())
        .connectionId(connectionRead.getConnectionId())
        .syncCatalog(connectionRead.getSyncCatalog())
        .schedule(connectionRead.getSchedule())
        .status(ConnectionStatus.DEPRECATED);

    updateConnection(connectionUpdate);
  }

  private boolean isStandardSyncInWorkspace(final UUID workspaceId,
                                            final StandardSync standardSync)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return configRepository.getSourceConnection(standardSync.getSourceId()).getWorkspaceId().equals(workspaceId);
  }

  private ConnectionRead buildConnectionRead(UUID connectionId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // read sync from db
    final StandardSync standardSync = configRepository.getStandardSync(connectionId);

    // read schedule from db
    final StandardSyncSchedule standardSyncSchedule = configRepository.getStandardSyncSchedule(connectionId);
    return buildConnectionRead(standardSync, standardSyncSchedule);
  }

  private ConnectionRead buildConnectionRead(final StandardSync standardSync,
                                             final StandardSyncSchedule standardSyncSchedule) {
    ConnectionSchedule apiSchedule = null;

    if (!standardSyncSchedule.getManual()) {
      apiSchedule = new ConnectionSchedule()
          .timeUnit(toApiTimeUnit(standardSyncSchedule.getSchedule().getTimeUnit()))
          .units(standardSyncSchedule.getSchedule().getUnits());
    }

    return new ConnectionRead()
        .connectionId(standardSync.getConnectionId())
        .sourceId(standardSync.getSourceId())
        .destinationId(standardSync.getDestinationId())
        .status(toApiStatus(standardSync.getStatus()))
        .schedule(apiSchedule)
        .name(standardSync.getName())
        .prefix(standardSync.getPrefix())
        .syncCatalog(CatalogConverter.toApi(standardSync.getCatalog()));
  }

  private StandardSync.Status toPersistenceStatus(ConnectionStatus apiStatus) {
    return Enums.convertTo(apiStatus, StandardSync.Status.class);
  }

  private SyncMode toApiSyncMode(io.airbyte.config.SyncMode persistenceStatus) {
    return Enums.convertTo(persistenceStatus, SyncMode.class);
  }

  private ConnectionStatus toApiStatus(StandardSync.Status status) {
    return Enums.convertTo(status, ConnectionStatus.class);
  }

  private Schedule.TimeUnit toPersistenceTimeUnit(ConnectionSchedule.TimeUnitEnum apiTimeUnit) {
    return Enums.convertTo(apiTimeUnit, Schedule.TimeUnit.class);
  }

  private ConnectionSchedule.TimeUnitEnum toApiTimeUnit(Schedule.TimeUnit apiTimeUnit) {
    return Enums.convertTo(apiTimeUnit, ConnectionSchedule.TimeUnitEnum.class);
  }

}
