/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc.typing_deduping;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.jdbc.ColumnDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.CustomSqlType;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.sql.DatabaseMetaData;
import java.sql.JDBCType;
import java.sql.ResultSet;
import java.sql.SQLType;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Optional;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class JdbcDestinationHandler implements DestinationHandler<TableDefinition> {

  private final String databaseName;
  private final JdbcDatabase jdbcDatabase;
  public JdbcDestinationHandler(final String databaseName,
                                final JdbcDatabase jdbcDatabase) {
    this.databaseName = databaseName;
    this.jdbcDatabase = jdbcDatabase;
  }

  @Override
  public Optional<TableDefinition> findExistingTable(StreamId id) throws Exception {

    DatabaseMetaData metaData = jdbcDatabase.getMetaData();
    //TODO: normalize namespace and finalName strings to quoted-lowercase
    final LinkedHashMap<String, ColumnDefinition> columnDefinitions = new LinkedHashMap<>();
    try(ResultSet columns = metaData.getColumns(databaseName, id.finalNamespace(), id.finalName(), null)){
      while(columns.next()) {
        String columnName = columns.getString("COLUMN_NAME");
        String typeName = columns.getString("TYPE_NAME");
        int columnSize = columns.getInt("COLUMN_SIZE");
        int datatype = columns.getInt("DATA_TYPE");
        SQLType sqlType;
        try {
          sqlType = JDBCType.valueOf(datatype);
        } catch (IllegalArgumentException e) {
          // Unknown jdbcType convert to customSqlType
          sqlType = new CustomSqlType("Unknown", "Unknown", datatype);
        }
        columnDefinitions.put(columnName, new ColumnDefinition(columnName, typeName, sqlType, columnSize));
      }
    } catch (Exception e) {
      log.error("Failed to retrieve columns from Database metadata for {}, {}, {}", databaseName, id.finalNamespace(), id.finalName());
      return Optional.empty();
    }
    // Guard to fail fast
    if (columnDefinitions.isEmpty()) {
      return Optional.empty();
    }

    return Optional.of(new TableDefinition(columnDefinitions));
  }

  @Override
  public boolean isFinalTableEmpty(StreamId id) throws Exception {
    return false;
  }

  @Override
  public Optional<Instant> getMinTimestampForSync(StreamId id) throws Exception {
    return Optional.empty();
  }

  @Override
  public void execute(String sql) throws Exception {

  }

}
