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

import io.dataline.api.model.ConnectionCreate;
import io.dataline.api.model.ConnectionIdRequestBody;
import io.dataline.api.model.ConnectionRead;
import io.dataline.api.model.ConnectionReadList;
import io.dataline.api.model.ConnectionSchedule;
import io.dataline.api.model.ConnectionStatus;
import io.dataline.api.model.ConnectionUpdate;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.commons.enums.Enums;
import io.dataline.config.ConfigSchema;
import io.dataline.config.Schedule;
import io.dataline.config.Schema;
import io.dataline.config.StandardSync;
import io.dataline.config.StandardSyncSchedule;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.server.converters.SchemaConverter;
import io.dataline.server.helpers.ConfigFetchers;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;

public class ConnectionsHandler {

  private final ConfigPersistence configPersistence;
  private final Supplier<UUID> uuidGenerator;

  public ConnectionsHandler(ConfigPersistence configPersistence, Supplier<UUID> uuidGenerator) {
    this.configPersistence = configPersistence;
    this.uuidGenerator = uuidGenerator;
  }

  public ConnectionsHandler(ConfigPersistence configPersistence) {
    this(configPersistence, UUID::randomUUID);
  }

  public ConnectionRead createConnection(ConnectionCreate connectionCreate) {
    final UUID connectionId = uuidGenerator.get();

    // persist sync
    final StandardSync standardSync = new StandardSync()
        .withConnectionId(connectionId)
        .withSourceImplementationId(connectionCreate.getSourceImplementationId())
        .withDestinationImplementationId(connectionCreate.getDestinationImplementationId())
        // todo (cgardens): for MVP we only support append.
        .withSyncMode(StandardSync.SyncMode.APPEND);
    if (connectionCreate.getSyncSchema() != null) {
      standardSync.withSchema(SchemaConverter.toPersistenceSchema(connectionCreate.getSyncSchema()));
    } else {
      standardSync.withSchema(new Schema().withTables(Collections.emptyList()));
    }
    standardSync
        .withName(connectionCreate.getName() != null ? connectionCreate.getName() : "default")
        .withStatus(toPersistenceStatus(connectionCreate.getStatus()));

    writeStandardSync(standardSync);

    // persist schedule
    final StandardSyncSchedule standardSyncSchedule = new StandardSyncSchedule()
        .withConnectionId(connectionId);
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

    writeSchedule(standardSyncSchedule);

    return getConnectionInternal(connectionId);
  }

  private void writeStandardSync(StandardSync standardSync) {
    ConfigFetchers.writeConfig(
        configPersistence,
        ConfigSchema.STANDARD_SYNC,
        standardSync.getConnectionId().toString(),
        standardSync);
  }

  // todo (cgardens) - stored on sync id (there is no schedule id concept). this is non-intuitive.
  private void writeSchedule(StandardSyncSchedule schedule) {
    ConfigFetchers.writeConfig(
        configPersistence,
        ConfigSchema.STANDARD_SYNC_SCHEDULE,
        schedule.getConnectionId().toString(),
        schedule);
  }

  public ConnectionRead updateConnection(ConnectionUpdate connectionUpdate) {
    final UUID connectionId = connectionUpdate.getConnectionId();

    // get existing sync
    final StandardSync persistedSync = getStandardSync(connectionId)
        .withSchema(SchemaConverter.toPersistenceSchema(connectionUpdate.getSyncSchema()))
        .withStatus(toPersistenceStatus(connectionUpdate.getStatus()));

    // get existing schedule
    final StandardSyncSchedule persistedSchedule = getSyncSchedule(connectionId);
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

    // persist sync
    writeStandardSync(persistedSync);

    // persist schedule
    writeSchedule(persistedSchedule);

    return getConnectionInternal(connectionId);
  }

  // todo (cgardens) - this is a disaster without a relational db.
  public ConnectionReadList listConnectionsForWorkspace(WorkspaceIdRequestBody workspaceIdRequestBody) {

    final List<ConnectionRead> reads =
        // read all connections.
        ConfigFetchers.getStandardSyncs(configPersistence).stream()
            // filter out connections attached to source implementations NOT associated with the
            // workspace
            .filter(
                standardSync -> ConfigFetchers.getSourceConnectionImplementation(
                    configPersistence, standardSync.getSourceImplementationId())
                    .getWorkspaceId()
                    .equals(workspaceIdRequestBody.getWorkspaceId()))
            // filter out deprecated connections
            .filter(standardSync -> !standardSync.getStatus().equals(StandardSync.Status.DEPRECATED))
            // pull the sync schedule
            // convert to api format
            .map(
                standardSync -> {
                  final StandardSyncSchedule syncSchedule =
                      getSyncSchedule(standardSync.getConnectionId());
                  return toConnectionRead(standardSync, syncSchedule);
                })
            .collect(Collectors.toList());

    final ConnectionReadList connectionReadList = new ConnectionReadList();
    connectionReadList.setConnections(reads);
    return connectionReadList;
  }

  public ConnectionRead getConnection(ConnectionIdRequestBody connectionIdRequestBody) {
    return getConnectionInternal(connectionIdRequestBody.getConnectionId());
  }

  private ConnectionRead getConnectionInternal(UUID connectionId) {
    // read sync from db
    final StandardSync standardSync = getStandardSync(connectionId);

    // read schedule from db
    final StandardSyncSchedule standardSyncSchedule = getSyncSchedule(connectionId);
    return toConnectionRead(standardSync, standardSyncSchedule);
  }

  private StandardSync getStandardSync(UUID connectionId) {
    return ConfigFetchers.getStandardSync(configPersistence, connectionId);
  }

  private StandardSyncSchedule getSyncSchedule(UUID connectionId) {
    return ConfigFetchers.getStandardSyncSchedule(configPersistence, connectionId);
  }

  private ConnectionRead toConnectionRead(StandardSync standardSync,
                                          StandardSyncSchedule standardSyncSchedule) {
    ConnectionSchedule apiSchedule = null;

    if (!standardSyncSchedule.getManual()) {
      apiSchedule = new ConnectionSchedule()
          .timeUnit(toApiTimeUnit(standardSyncSchedule.getSchedule().getTimeUnit()))
          .units(standardSyncSchedule.getSchedule().getUnits());
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
