package io.dataline.server.handlers;

import io.dataline.api.model.*;
import io.dataline.config.*;
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

  private StandardSync.Status toPersistenceStatus(ConnectionStatus apiStatus) {
    switch (apiStatus) {
      case ACTIVE:
        return StandardSync.Status.ACTIVE;
      case INACTIVE:
        return StandardSync.Status.INACTIVE;
      case DEPRECATED:
        return StandardSync.Status.DEPRECATED;
      default:
        throw new RuntimeException(
            String.format(
                "No conversion from StandardSync.Status to StandardSync.Status for %s.",
                apiStatus));
    }
  }

  private ConnectionRead.SyncModeEnum toApiSyncMode(StandardSync.SyncMode persistenceStatus) {
    switch (persistenceStatus) {
      case FULL_REFRESH:
        return ConnectionRead.SyncModeEnum.FULL_REFRESH;
      case APPEND:
        return ConnectionRead.SyncModeEnum.APPEND;
      default:
        throw new RuntimeException(
            String.format(
                "No conversion from ConnectionRead.SyncModeEnum to StandardSync.SyncMode for %s.",
                persistenceStatus));
    }
  }

  private ConnectionStatus toApiStatus(StandardSync.Status status) {
    switch (status) {
      case ACTIVE:
        return ConnectionStatus.ACTIVE;
      case INACTIVE:
        return ConnectionStatus.INACTIVE;
      case DEPRECATED:
        return ConnectionStatus.DEPRECATED;
      default:
        throw new RuntimeException(
            String.format(
                "No conversion from StandardSync.Status to StandardSync.Status for %s.", status));
    }
  }

  private Schedule.TimeUnit toPersistenceTimeUnit(ConnectionSchedule.TimeUnitEnum apiTimeUnit) {
    switch (apiTimeUnit) {
      case MINUTES:
        return Schedule.TimeUnit.MINUTES;
      case HOURS:
        return Schedule.TimeUnit.HOURS;
      case DAYS:
        return Schedule.TimeUnit.DAYS;
      case WEEKS:
        return Schedule.TimeUnit.WEEKS;
      case MONTHS:
        return Schedule.TimeUnit.MONTHS;
      default:
        throw new RuntimeException(
            String.format(
                "No conversion from ConnectionSchedule.TimeUnitEnum to StandardSyncSchedule.TimeUnit for %s.",
                apiTimeUnit));
    }
  }

  private ConnectionSchedule.TimeUnitEnum toApiTimeUnit(Schedule.TimeUnit apiTimeUnit) {
    switch (apiTimeUnit) {
      case MINUTES:
        return ConnectionSchedule.TimeUnitEnum.MINUTES;
      case HOURS:
        return ConnectionSchedule.TimeUnitEnum.HOURS;
      case DAYS:
        return ConnectionSchedule.TimeUnitEnum.DAYS;
      case WEEKS:
        return ConnectionSchedule.TimeUnitEnum.WEEKS;
      case MONTHS:
        return ConnectionSchedule.TimeUnitEnum.MONTHS;
      default:
        throw new RuntimeException(
            String.format(
                "No conversion from StandardSyncSchedule.TimeUnit to ConnectionSchedule.TimeUnitEnum for %s.",
                apiTimeUnit));
    }
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

  // todo: figure out why the generator is namespacing the DataType enum by Column.
  private Column.DataType toPersistenceDataType(SourceSchemaColumn.DataTypeEnum apiDataType) {
    switch (apiDataType) {
      case STRING:
        return Column.DataType.STRING;
      case NUMBER:
        return Column.DataType.NUMBER;
      case BOOLEAN:
        return Column.DataType.BOOLEAN;
      default:
        throw new RuntimeException(
            String.format(
                "No conversion from SourceSchemaColumn.DataTypeEnum to Column.DataType for %s.",
                apiDataType));
    }
  }

  private SourceSchemaColumn.DataTypeEnum toApiDataType(Column.DataType persistenceDataType) {
    switch (persistenceDataType) {
      case STRING:
        return SourceSchemaColumn.DataTypeEnum.STRING;
      case NUMBER:
        return SourceSchemaColumn.DataTypeEnum.NUMBER;
      case BOOLEAN:
        return SourceSchemaColumn.DataTypeEnum.BOOLEAN;
      default:
        throw new RuntimeException(
            String.format(
                "No conversion from Column.DataType to SourceSchemaColumn.DataTypeEnum for %s.",
                persistenceDataType));
    }
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
}
