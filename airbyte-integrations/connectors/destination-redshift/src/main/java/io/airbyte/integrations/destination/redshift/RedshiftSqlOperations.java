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

package io.airbyte.integrations.destination.redshift;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.DefaultSqlOperations;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.SqlOperationsUtils;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftSqlOperations extends DefaultSqlOperations implements SqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftSqlOperations.class);

  @Override
  public String createTableQuery(String schemaName, String tableName) {
    return String.format(
        "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
            + "%s VARCHAR PRIMARY KEY,\n"
            + "%s VARCHAR(max),\n"
            + "%s TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP\n"
            + ");\n",
        schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  }

  @Override
  public void insertRecords(JdbcDatabase database, Stream<AirbyteRecordMessage> recordsStream, String schemaName, String tmpTableName)
      throws SQLException {
    final List<AirbyteRecordMessage> records = recordsStream.collect(Collectors.toList());
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

  public void copyS3CsvFileIntoTable(JdbcDatabase database,
                                     String s3FileLocation,
                                     String schema,
                                     String tableName,
                                     String s3KeyId,
                                     String s3Key,
                                     String s3Region)
      throws SQLException {
    final var copyQuery = String.format(
        "COPY %s.%s FROM '%s'\n"
            + "CREDENTIALS 'aws_access_key_id=%s;aws_secret_access_key=%s'\n"
            + "CSV REGION '%s' TIMEFORMAT 'auto';\n",
        schema, tableName,
        s3FileLocation,
        s3KeyId, s3Key,
        s3Region);

    database.execute(copyQuery);
  }

}
