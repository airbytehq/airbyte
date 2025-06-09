/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore.jdbc;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.jdbc.ColumnDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.commons.exceptions.SQLRuntimeException;
import io.airbyte.integrations.base.destination.typing_deduping.*;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.*;
import java.util.stream.Collectors;
import org.jetbrains.annotations.NotNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingleStoreDestinationHandler implements DestinationHandler<MinimumDestinationState.Impl> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingleStoreDestinationHandler.class);
  private final JdbcDatabase jdbcDatabase;
  private boolean isLocalFileEnabled = false;

  public SingleStoreDestinationHandler(JdbcDatabase jdbcDatabase) {
    this.jdbcDatabase = jdbcDatabase;
  }

  @Override
  public void commitDestinationStates(@NotNull Map<StreamId, ? extends MinimumDestinationState.Impl> destinationStates) {}

  @Override
  public void execute(@NotNull Sql sql) throws Exception {
    var transactions = sql.transactions();
    var queryId = UUID.randomUUID();
    for (var transaction : transactions) {
      var transactionId = UUID.randomUUID();
      LOGGER.info("Executing sql {}-{}: {}", queryId, transactionId, String.join("\n", transaction));
      var startTime = System.currentTimeMillis();
      try {
        jdbcDatabase.executeWithinTransaction(transaction);
      } catch (SQLException e) {
        LOGGER.error("Sql {}-{} failed in {} ms", queryId, transactionId, System.currentTimeMillis() - startTime);
        throw e;
      }
      LOGGER.info("Sql {}-{} completed in {} ms", queryId, transactionId, System.currentTimeMillis() - startTime);
    }
  }

  @NotNull
  @Override
  public List<DestinationInitialStatus<MinimumDestinationState.Impl>> gatherInitialState(@NotNull List<StreamConfig> streamConfigs) {
    var streamIds = streamConfigs.stream().map(StreamConfig::getId).collect(Collectors.toList());
    var existingTables = findExistingTable(streamIds);
    List<DestinationInitialStatus<MinimumDestinationState.Impl>> list = new ArrayList<>();
    for (StreamConfig config : streamConfigs) {
      var namespace = config.getId().getFinalNamespace();
      var name = config.getId().getFinalName();
      InitialRawTableStatus initialRawTableStatus;
      if (config.getDestinationSyncMode() == DestinationSyncMode.OVERWRITE) {
        initialRawTableStatus = new InitialRawTableStatus(false, false, Optional.empty());
      } else {
        try {
          initialRawTableStatus = getInitialRawTableState(config.getId());
        } catch (SQLException e) {
          throw new SQLRuntimeException(e);
        }
      }
      if (existingTables.containsKey(namespace) && existingTables.get(namespace).containsKey(name)) {
        list.add(new DestinationInitialStatus<>(config, true, initialRawTableStatus, !isSchemaMatch(config, existingTables.get(namespace).get(name)),
            isFinalTableEmpty(config.getId()), new MinimumDestinationState.Impl(false)));
      } else {
        list.add(new DestinationInitialStatus<>(config, false, initialRawTableStatus, false, true, new MinimumDestinationState.Impl(false)));
      }
    }
    return list;
  }

  private InitialRawTableStatus getInitialRawTableState(StreamId id) throws SQLException {
    var rawTableExists = jdbcDatabase.executeMetadataQuery(metadata -> {
      try {
        var resultSet = metadata.getTables(null, id.getRawNamespace(), id.getRawName(), null);
        return resultSet.next();
      } catch (SQLException e) {
        throw new SQLRuntimeException(e);
      }
    });
    if (!rawTableExists) {
      return new InitialRawTableStatus(false, false, Optional.empty());
    }
    var minExtractedAtLoadedNotNullQuery = String.format("SELECT min(%s) as last_loaded_at FROM %s WHERE %s IS NULL",
        JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT, id.rawTableId(SingleStoreSqlGenerator.QUOTE), JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT);
    var maxExtractedAtQuery = String.format("SELECT max(%s) as last_loaded_at FROM %s", JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
        id.rawTableId(SingleStoreSqlGenerator.QUOTE));
    var minLastLoadedAt = findLastLoadedTs(minExtractedAtLoadedNotNullQuery).map(it -> it.minusSeconds(1));
    if (minLastLoadedAt.isPresent()) {
      return new InitialRawTableStatus(true, true, minLastLoadedAt);
    }
    var maxLastLoadedAt = findLastLoadedTs(maxExtractedAtQuery);
    return new InitialRawTableStatus(true, false, maxLastLoadedAt);
  }

  private Optional<Instant> findLastLoadedTs(String query) throws SQLException {
    var value = jdbcDatabase.bufferedResultSetQuery(connection -> connection.createStatement().executeQuery(query), input -> {
      LocalDateTime dateTime = input.getObject("last_loaded_at", LocalDateTime.class);
      if (dateTime != null) {
        return dateTime.toInstant(ZoneOffset.UTC);
      }
      return null;
    });
    return value.isEmpty() || value.getFirst() == null ? Optional.empty() : Optional.of(value.getFirst());
  }

  private boolean isSchemaMatch(StreamConfig streamConfig, TableDefinition tableDefinition) {
    var isAbRawIdMatch = tableDefinition.columns().containsKey(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID)
        && "VARCHAR".equalsIgnoreCase(tableDefinition.columns().get(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID).getType());
    var isAbExtractedAtMatch = tableDefinition.columns().containsKey(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT)
        && "TIMESTAMP".equalsIgnoreCase(tableDefinition.columns().get(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT).getType());
    var isAbMetaMatch = tableDefinition.columns().containsKey(JavaBaseConstants.COLUMN_NAME_AB_META)
        && "JSON".equalsIgnoreCase(tableDefinition.columns().get(JavaBaseConstants.COLUMN_NAME_AB_META).getType());
    if (!isAbRawIdMatch || !isAbExtractedAtMatch || !isAbMetaMatch) {
      return false;
    }
    var expectedColumns = streamConfig.getColumns().entrySet().stream()
        .collect(Collectors.toMap(e -> e.getKey().getName(), e -> SingleStoreSqlGenerator.toDialectType(e.getValue()).getTypeName()));
    var actualColumns = tableDefinition.columns().entrySet().stream()
        .filter(it -> !JavaBaseConstants.V2_FINAL_TABLE_METADATA_COLUMNS.contains(it.getKey()))
        .collect(Collectors.toMap(Map.Entry::getKey,
            e -> "bit".equalsIgnoreCase(e.getValue().getType()) ? "boolean" : e.getValue().getType().toLowerCase()));
    return Objects.equals(actualColumns, expectedColumns);
  }

  private boolean isFinalTableEmpty(StreamId id) {
    try {
      return !jdbcDatabase.queryBoolean(String.format("SELECT EXISTS (SELECT 1 from %s)", id.finalTableId(SingleStoreSqlGenerator.QUOTE)));
    } catch (SQLException e) {
      throw new RuntimeException(e);
    }
  }

  private Map<String, LinkedHashMap<String, TableDefinition>> findExistingTable(List<StreamId> streamIds) {
    Map<String, LinkedHashMap<String, TableDefinition>> map = new HashMap<>();
    for (StreamId id : streamIds) {
      findExistingTable(id).ifPresent(d -> {
        var defMap = map.computeIfAbsent(id.getFinalNamespace(), k -> new LinkedHashMap<>());
        defMap.put(id.getFinalName(), d);
      });
    }
    return map;
  }

  protected Optional<TableDefinition> findExistingTable(@NotNull StreamId id) {
    final var databaseName = id.getFinalNamespace();
    final var tableName = id.getFinalName();
    LinkedHashMap<String, ColumnDefinition> retrievedColumnDefns = null;
    try {
      retrievedColumnDefns = jdbcDatabase.executeMetadataQuery(dbMetadata -> {
        var columnDefinitions = new LinkedHashMap<String, ColumnDefinition>();
        LOGGER.info("Retrieving existing columns for {}.{}", databaseName, tableName);
        try {
          ResultSet rs = dbMetadata.getColumns(databaseName, null, tableName, null);
          while (rs.next()) {
            var columnName = rs.getString("COLUMN_NAME");
            var typeName = rs.getString("TYPE_NAME");
            var columnSize = rs.getInt("COLUMN_SIZE");
            var isNullable = rs.getString("IS_NULLABLE");
            columnDefinitions.put(columnName, new ColumnDefinition(columnName, typeName, columnSize, "YES".equalsIgnoreCase(isNullable)));
          }
        } catch (SQLException e) {
          LOGGER.error("Failed to retrieve column info for {}.{}", databaseName, tableName, e);
          throw new SQLRuntimeException(e);
        }
        return columnDefinitions;
      });
    } catch (SQLException e) {
      throw new RuntimeException(e);
    }
    if (retrievedColumnDefns.isEmpty()) {
      return Optional.empty();
    }
    return Optional.of(new TableDefinition(retrievedColumnDefns));
  }

  @Override
  public void createNamespaces(@NotNull Set<String> databases) {
    databases.forEach(d -> {
      try {
        jdbcDatabase.execute(String.format("CREATE DATABASE IF NOT EXISTS %s", d));
      } catch (SQLException e) {
        LOGGER.warn("Failed to create destination database", e);
        throw new RuntimeException(e);
      }
    });
  }

  public void verifyLocalFileEnabled() throws SQLException {
    final boolean localFileEnabled = isLocalFileEnabled || checkIfLocalFileIsEnabled();
    if (!localFileEnabled) {
      tryEnableLocalFile();
    }
    isLocalFileEnabled = true;
  }

  private void tryEnableLocalFile() throws SQLException {
    jdbcDatabase.execute(connection -> {
      try (final Statement statement = connection.createStatement()) {
        statement.execute("set global local_infile=true");
      } catch (final Exception e) {
        throw new RuntimeException(
            "The DB user provided to airbyte was unable to switch on the local_infile attribute on the SingleStore server. As an root user, you will need to run \"SET GLOBAL local_infile = true\" before syncing data with Airbyte.",
            e);
      }
    });
  }

  private boolean checkIfLocalFileIsEnabled() throws SQLException {
    final List<String> localFiles =
        jdbcDatabase.queryStrings(connection -> connection.createStatement().executeQuery("SHOW GLOBAL VARIABLES LIKE 'local_infile'"),
            resultSet -> resultSet.getString("Value"));
    return localFiles.get(0).equalsIgnoreCase("on");
  }

}
