/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.server.handlers;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import io.dataline.api.model.ConnectionCreate;
import io.dataline.api.model.ConnectionIdRequestBody;
import io.dataline.api.model.ConnectionRead;
import io.dataline.api.model.ConnectionReadList;
import io.dataline.api.model.ConnectionSchedule;
import io.dataline.api.model.ConnectionStatus;
import io.dataline.api.model.ConnectionUpdate;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.commons.enums.Enums;
import io.dataline.config.Schedule;
import io.dataline.config.Schema;
import io.dataline.config.StandardSync;
import io.dataline.config.StandardSyncSchedule;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigRepository;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.server.converters.SchemaConverter;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;

public class ConnectionsHandler {

  private final ConfigRepository configRepository;
  private final Supplier<UUID> uuidGenerator;

  @VisibleForTesting
  ConnectionsHandler(final ConfigRepository configRepository,
                     final Supplier<UUID> uuidGenerator) {
    this.configRepository = configRepository;
    this.uuidGenerator = uuidGenerator;
  }

  public ConnectionsHandler(final ConfigRepository configRepository) {
    this(configRepository, UUID::randomUUID);
  }

  public ConnectionRead createConnection(ConnectionCreate connectionCreate)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final UUID connectionId = uuidGenerator.get();

    // persist sync
    final StandardSync standardSync = new StandardSync()
        .withConnectionId(connectionId)
        .withName(connectionCreate.getName() != null ? connectionCreate.getName() : "default")
        .withSourceImplementationId(connectionCreate.getSourceImplementationId())
        .withDestinationImplementationId(connectionCreate.getDestinationImplementationId())
        .withSyncMode(StandardSync.SyncMode.APPEND) // todo (cgardens): for MVP we only support append.
        .withStatus(toPersistenceStatus(connectionCreate.getStatus()));

    if (connectionCreate.getSyncSchema() != null) {
      standardSync.withSchema(SchemaConverter.toPersistenceSchema(connectionCreate.getSyncSchema()));
    } else {
      standardSync.withSchema(new Schema().withTables(Collections.emptyList()));
    }

    standardSync.setSyncSchedule(new StandardSyncSchedule());
    if (connectionCreate.getSchedule() != null) {
      final Schedule schedule = new Schedule()
          .withTimeUnit(toPersistenceTimeUnit(connectionCreate.getSchedule().getTimeUnit()))
          .withUnits(connectionCreate.getSchedule().getUnits());
      standardSync.getSyncSchedule()
          .withManual(false)
          .withSchedule(schedule);
    } else {
      standardSync.getSyncSchedule().withManual(true);
    }

    configRepository.writeStandardSync(standardSync);

    return buildConnectionRead(connectionId);
  }

  public ConnectionRead updateConnection(ConnectionUpdate connectionUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID connectionId = connectionUpdate.getConnectionId();

    // retrieve existing sync
    final StandardSync persistedSync = configRepository.getStandardSync(connectionId)
        .withSchema(SchemaConverter.toPersistenceSchema(connectionUpdate.getSyncSchema()))
        .withStatus(toPersistenceStatus(connectionUpdate.getStatus()));

    final StandardSyncSchedule persistedSchedule = persistedSync.getSyncSchedule();
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

  private boolean isStandardSyncInWorkspace(final UUID workspaceId,
                                            final StandardSync standardSync)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return configRepository.getSourceConnectionImplementation(standardSync.getSourceImplementationId()).getWorkspaceId().equals(workspaceId);
  }

  private ConnectionRead buildConnectionRead(UUID connectionId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // read sync from db
    final StandardSync standardSync = configRepository.getStandardSync(connectionId);

    return buildConnectionRead(standardSync);
  }

  private ConnectionRead buildConnectionRead(final StandardSync standardSync) {
    ConnectionSchedule apiSchedule = null;

    if (!standardSync.getSyncSchedule().getManual()) {
      apiSchedule = new ConnectionSchedule()
          .timeUnit(toApiTimeUnit(standardSync.getSyncSchedule().getSchedule().getTimeUnit()))
          .units(standardSync.getSyncSchedule().getSchedule().getUnits());
    }

    return new ConnectionRead()
        .connectionId(standardSync.getConnectionId())
        .sourceImplementationId(standardSync.getSourceImplementationId())
        .destinationImplementationId(standardSync.getDestinationImplementationId())
        .status(toApiStatus(standardSync.getStatus()))
        .schedule(apiSchedule)
        .syncMode(toApiSyncMode(standardSync.getSyncMode()))
        .name(standardSync.getName())
        .syncSchema(SchemaConverter.toApiSchema(standardSync.getSchema()));
  }

  private StandardSync.Status toPersistenceStatus(ConnectionStatus apiStatus) {
    return Enums.convertTo(apiStatus, StandardSync.Status.class);
  }

  private ConnectionRead.SyncModeEnum toApiSyncMode(StandardSync.SyncMode persistenceStatus) {
    return Enums.convertTo(persistenceStatus, ConnectionRead.SyncModeEnum.class);
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
