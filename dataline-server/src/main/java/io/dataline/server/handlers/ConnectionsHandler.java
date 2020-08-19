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
import io.dataline.api.model.SourceSchema;
import io.dataline.api.model.SourceSchemaColumn;
import io.dataline.api.model.SourceSchemaTable;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.commons.enums.Enums;
import io.dataline.config.Column;
import io.dataline.config.Schedule;
import io.dataline.config.Schema;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSync;
import io.dataline.config.StandardSyncSchedule;
import io.dataline.config.Table;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.errors.KnownException;
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
    final StandardSync standardSync = new StandardSync();
    standardSync.setConnectionId(connectionId);
    standardSync.setSourceImplementationId(connectionCreate.getSourceImplementationId());
    standardSync.setDestinationImplementationId(connectionCreate.getDestinationImplementationId());
    standardSync.setSyncMode(StandardSync.SyncMode.APPEND); // todo: for MVP we only support append.
    standardSync.setSchema(toPersistenceSchema(connectionCreate.getSyncSchema()));
    standardSync.setName(
        connectionCreate.getName() != null ? connectionCreate.getName() : "default");
    standardSync.setStatus(toPersistenceStatus(connectionCreate.getStatus()));
    writeStandardSync(standardSync);

    // persist schedule
    final StandardSyncSchedule standardSyncSchedule = new StandardSyncSchedule();
    standardSyncSchedule.setConnectionId(connectionId);
    if (connectionCreate.getSchedule() != null) {
      final Schedule schedule = new Schedule();
      schedule.setTimeUnit(toPersistenceTimeUnit(connectionCreate.getSchedule().getTimeUnit()));
      schedule.setUnits(connectionCreate.getSchedule().getUnits());
      standardSyncSchedule.setManual(false);
      standardSyncSchedule.setSchedule(schedule);
    } else {
      standardSyncSchedule.setManual(true);
    }

    writeSchedule(standardSyncSchedule);

    return getConnectionInternal(connectionId);
  }

  private void writeStandardSync(StandardSync standardSync) {
    configPersistence.writeConfig(
        PersistenceConfigType.STANDARD_SYNC,
        standardSync.getConnectionId().toString(),
        standardSync);
  }

  // todo (cgardens) - stored on sync id (there is know schedule id concept). this is non-intuitive.
  private void writeSchedule(StandardSyncSchedule schedule) {
    configPersistence.writeConfig(
        PersistenceConfigType.STANDARD_SYNC_SCHEDULE,
        schedule.getConnectionId().toString(),
        schedule);
  }

  public ConnectionRead updateConnection(ConnectionUpdate connectionUpdate) {
    final UUID connectionId = connectionUpdate.getConnectionId();

    // get existing sync
    final StandardSync persistedSync = getStandardSync(connectionId);
    persistedSync.setSchema(toPersistenceSchema(connectionUpdate.getSyncSchema()));
    persistedSync.setStatus(toPersistenceStatus(connectionUpdate.getStatus()));

    // get existing schedule
    final StandardSyncSchedule persistedSchedule = getSyncSchedule(connectionId);
    if (connectionUpdate.getSchedule() != null) {
      final Schedule schedule = new Schedule();
      schedule.setTimeUnit(toPersistenceTimeUnit(connectionUpdate.getSchedule().getTimeUnit()));
      schedule.setUnits(connectionUpdate.getSchedule().getUnits());

      persistedSchedule.setSchedule(schedule);

      persistedSchedule.setManual(false);
    } else {
      persistedSchedule.setSchedule(null);
      persistedSchedule.setManual(true);
    }

    // persist sync
    writeStandardSync(persistedSync);

    // persist schedule
    writeSchedule(persistedSchedule);

    return getConnectionInternal(connectionId);
  }

  // todo (cgardens) - this is a disaster without a relational db.
  public ConnectionReadList listConnectionsForWorkspace(
      WorkspaceIdRequestBody workspaceIdRequestBody) {
    try {

      final List<ConnectionRead> reads =
          configPersistence
              // read all connections.
              .getConfigs(PersistenceConfigType.STANDARD_SYNC, StandardSync.class)
              .stream()
              // filter out connections attached to source implementations NOT associated with the
              // workspace
              .filter(
                  standardSync -> {
                    try {
                      return configPersistence
                          .getConfig(
                              PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
                              standardSync.getSourceImplementationId().toString(),
                              SourceConnectionImplementation.class)
                          .getWorkspaceId()
                          .equals(workspaceIdRequestBody.getWorkspaceId());
                    } catch (JsonValidationException e) {
                      throw new KnownException(
                          422,
                          String.format(
                              "The provided configuration does not fulfill the specification. Errors: %s",
                              e.getMessage()));
                    } catch (ConfigNotFoundException e) {
                      throw new KnownException(
                          422,
                          String.format(
                              "Could not find source connection implementation for source implementation: %s.",
                              standardSync.getSourceImplementationId()));
                    }
                  })
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
    } catch (JsonValidationException e) {
      throw new KnownException(
          422,
          String.format(
              "Attempted to retrieve a configuration does not fulfill the specification. Errors: %s",
              e.getMessage()));
    }
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
    try {
      return configPersistence.getConfig(
          PersistenceConfigType.STANDARD_SYNC, connectionId.toString(), StandardSync.class);
    } catch (JsonValidationException e) {
      throw new KnownException(
          422,
          String.format(
              "The provided configuration does not fulfill the specification. Errors: %s",
              e.getMessage()));
    } catch (ConfigNotFoundException e) {
      throw new KnownException(
          422,
          String.format("Could not find sync configuration for connection: %s.", connectionId));
    }
  }

  private StandardSyncSchedule getSyncSchedule(UUID connectionId) {
    try {
      return configPersistence.getConfig(
          PersistenceConfigType.STANDARD_SYNC_SCHEDULE,
          connectionId.toString(),
          StandardSyncSchedule.class);
    } catch (JsonValidationException e) {
      throw new KnownException(
          422,
          String.format(
              "The provided configuration does not fulfill the specification. Errors: %s",
              e.getMessage()));
    } catch (ConfigNotFoundException e) {
      throw new KnownException(
          422, String.format("Could not find sync schedule for connection: %s.", connectionId));
    }
  }

  private ConnectionRead toConnectionRead(
      StandardSync standardSync, StandardSyncSchedule standardSyncSchedule) {
    final ConnectionSchedule apiSchedule;

    standardSyncSchedule.setConnectionId(standardSyncSchedule.getConnectionId());
    if (!standardSyncSchedule.getManual()) {
      apiSchedule = new ConnectionSchedule();
      apiSchedule.setTimeUnit(toApiTimeUnit(standardSyncSchedule.getSchedule().getTimeUnit()));
      apiSchedule.setUnits(standardSyncSchedule.getSchedule().getUnits());
    } else {
      apiSchedule = null;
    }

    final ConnectionRead connectionRead = new ConnectionRead();
    connectionRead.setConnectionId(standardSync.getConnectionId());
    connectionRead.setSourceImplementationId(standardSync.getSourceImplementationId());
    connectionRead.setDestinationImplementationId(standardSync.getDestinationImplementationId());
    connectionRead.setStatus(toApiStatus(standardSync.getStatus()));
    connectionRead.setSchedule(apiSchedule);
    connectionRead.setSyncMode(toApiSyncMode(standardSync.getSyncMode()));
    connectionRead.setName(standardSync.getName());
    connectionRead.setSyncSchema(toApiSchema(standardSync.getSchema()));

    return connectionRead;
  }

  private Schema toPersistenceSchema(SourceSchema api) {
    final List<Table> persistenceTables =
        api.getTables().stream()
            .map(
                apiTable -> {
                  final List<Column> persistenceColumns =
                      apiTable.getColumns().stream()
                          .map(
                              apiColumn -> {
                                final Column persistenceColumn = new Column();
                                persistenceColumn.setName(apiColumn.getName());
                                persistenceColumn.setDataType(
                                    toPersistenceDataType(apiColumn.getDataType()));
                                return persistenceColumn;
                              })
                          .collect(Collectors.toList());

                  final Table persistenceTable = new Table();
                  persistenceTable.setName(apiTable.getName());
                  persistenceTable.setColumns(persistenceColumns);

                  return persistenceTable;
                })
            .collect(Collectors.toList());

    final Schema persistenceSchema = new Schema();
    persistenceSchema.setTables(persistenceTables);
    return persistenceSchema;
  }

  private SourceSchema toApiSchema(Schema persistenceSchema) {

    final List<SourceSchemaTable> persistenceTables =
        persistenceSchema.getTables().stream()
            .map(
                persistenceTable -> {
                  final List<SourceSchemaColumn> apiColumns =
                      persistenceTable.getColumns().stream()
                          .map(
                              persistenceColumn -> {
                                final SourceSchemaColumn apiColumn = new SourceSchemaColumn();
                                apiColumn.setName(persistenceColumn.getName());
                                apiColumn.setDataType(
                                    toApiDataType(persistenceColumn.getDataType()));
                                return apiColumn;
                              })
                          .collect(Collectors.toList());

                  final SourceSchemaTable apiTable = new SourceSchemaTable();
                  apiTable.setName(persistenceTable.getName());
                  apiTable.setColumns(apiColumns);

                  return apiTable;
                })
            .collect(Collectors.toList());

    final SourceSchema apiSchema = new SourceSchema();
    apiSchema.setTables(persistenceTables);
    return apiSchema;
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

  // todo: figure out why the generator is namespacing the DataType enum by Column.
  private Column.DataType toPersistenceDataType(SourceSchemaColumn.DataTypeEnum apiDataType) {
    return Enums.convertTo(apiDataType, Column.DataType.class);
  }

  private SourceSchemaColumn.DataTypeEnum toApiDataType(Column.DataType persistenceDataType) {
    return Enums.convertTo(persistenceDataType, SourceSchemaColumn.DataTypeEnum.class);
  }
}
