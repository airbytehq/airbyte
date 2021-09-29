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
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.sql.SQLException;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftSqlOperations extends JdbcSqlOperations implements SqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftSqlOperations.class);
  protected static final int REDSHIFT_VARCHAR_MAX_BYTE_SIZE = 65535;

  @Override
  public String createTableQuery(JdbcDatabase database, String schemaName, String tableName) {
    return String.format(
        "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
            + "%s VARCHAR PRIMARY KEY,\n"
            + "%s VARCHAR(max),\n"
            + "%s TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP\n"
            + ");\n",
        schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  }

  @Override
  public void insertRecordsInternal(JdbcDatabase database, List<AirbyteRecordMessage> records, String schemaName, String tmpTableName)
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
    final String recordQueryComponent = "(?, ?, ?),\n";
    SqlOperationsUtils.insertRawRecordsInSingleQuery(insertQueryComponent, recordQueryComponent, database, records);
  }

  @Override
  public boolean isValidData(final JsonNode data) {
    String stringData = Jsons.serialize(data);
    final int dataSize = stringData.getBytes().length;
    return dataSize <= REDSHIFT_VARCHAR_MAX_BYTE_SIZE;
  }

}
