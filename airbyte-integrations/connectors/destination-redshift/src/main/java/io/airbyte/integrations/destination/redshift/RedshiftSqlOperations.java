/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.SqlOperationsUtils;
import io.airbyte.integrations.destination.redshift.enums.RedshiftDataTmpTableMode;
import io.airbyte.protocol.models.AirbyteRecordMessage;

import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.List;
import java.util.Optional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftSqlOperations extends JdbcSqlOperations implements SqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftSqlOperations.class);
  protected static final int REDSHIFT_VARCHAR_MAX_BYTE_SIZE = 65535;

  private final RedshiftDataTmpTableMode redshiftDataTmpTableMode;

  public RedshiftSqlOperations(final RedshiftDataTmpTableMode redshiftDataTmpTableMode) {
    this.redshiftDataTmpTableMode = redshiftDataTmpTableMode;
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    if (tableName.contains("raw") && updateDataColumnToSuperIfRequired(database, schemaName, tableName)) {
      // To keep the previous data, we need to add next columns: _airbyte_data, _airbyte_emitted_at
      // We do such workflow because we can't directly CAST VARCHAR to SUPER column. _airbyte_emitted_at column recreated to keep
      // the COLUMN order. This order is required to INSERT the values in correct way.
      return String.format("""
              ALTER TABLE %1$s.%2$s ADD COLUMN %3$s_super super;
              ALTER TABLE %1$s.%2$s ADD COLUMN %4$s_reserve TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
              UPDATE %1$s.%2$s SET %3$s_super = JSON_PARSE(%3$s);
              UPDATE %1$s.%2$s SET %4$s_reserve = %4$s;
              ALTER TABLE %1$s.%2$s DROP COLUMN %3$s;
              ALTER TABLE %1$s.%2$s DROP COLUMN %4$s;
              ALTER TABLE %1$s.%2$s RENAME %3$s_super to %3$s;
              ALTER TABLE %1$s.%2$s RENAME %4$s_reserve to %4$s;
              """,
          schemaName,
          tableName,
          JavaBaseConstants.COLUMN_NAME_DATA,
          JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    }
    LOGGER.info("Creating new table...");
    return redshiftDataTmpTableMode.getTmpTableSqlStatement(schemaName, tableName);
  }

  @Override
  public void insertRecordsInternal(final JdbcDatabase database,
      final List<AirbyteRecordMessage> records,
      final String schemaName,
      final String tmpTableName)
      throws SQLException {
    LOGGER.info("actual size of batch: {}", records.size());

    // query syntax:
    // INSERT INTO public.users (ab_id, data, emitted_at) VALUES
    // (?, ?::jsonb, ?),
    // ...
    final String insertQueryComponent = String.format(
        "INSERT INTO %s.%s (%s, %s, %s) VALUES\n",
        schemaName,
        tmpTableName,
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    final String recordQueryComponent = redshiftDataTmpTableMode.getInsertRowMode();
    SqlOperationsUtils.insertRawRecordsInSingleQuery(insertQueryComponent, recordQueryComponent, database, records);
  }

  @Override
  public boolean isValidData(final JsonNode data) {
    final String stringData = Jsons.serialize(data);
    final int dataSize = stringData.getBytes().length;
    return dataSize <= REDSHIFT_VARCHAR_MAX_BYTE_SIZE;
  }


  /**
   * @param database   - Database object for interacting with a JDBC connection.
   * @param schemaName - schema to update.
   * @param streamName - streamName.
   * @return true - if _airbyte_raw_users._airbyte_data should be updated to SUPER, else false.
   */
  private boolean updateDataColumnToSuperIfRequired(final JdbcDatabase database,
      final String schemaName,
      final String streamName) {
    try {
      final Optional<ResultSetMetaData> resultSetMetaData = Optional.ofNullable(database.queryMetadata(
          String.format("select top 1 _airbyte_data from %s.%s",
              schemaName,
              streamName)));
      if (resultSetMetaData.isPresent()) {
        return !resultSetMetaData.get()
            .getColumnTypeName(1)
            .trim()
            .contains("super");
      } else {
        return false;
      }
    } catch (SQLException e) {
      LOGGER.error("Some error appears during selection of _airbyte_data datatype:", e);
      return false;
    }
  }
}
