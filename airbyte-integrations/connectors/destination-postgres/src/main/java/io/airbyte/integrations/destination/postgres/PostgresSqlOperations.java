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

package io.airbyte.integrations.destination.postgres;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.jdbc.DataAdapter;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Files;
import java.sql.SQLException;
import java.util.List;
import org.postgresql.copy.CopyManager;
import org.postgresql.core.BaseConnection;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresSqlOperations extends JdbcSqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresSqlOperations.class);

  @Override
  public void insertRecordsInternal(JdbcDatabase database, List<AirbyteRecordMessage> records, String schemaName, String tmpTableName)
      throws SQLException {
    if (records.isEmpty()) {
      return;
    }

    database.execute(connection -> {
      File tmpFile = null;
      try {
        tmpFile = Files.createTempFile(tmpTableName + "-", ".tmp").toFile();
        writeBatchToFile(tmpFile, records);

        var copyManager = new CopyManager(connection.unwrap(BaseConnection.class));
        var sql = String.format("COPY %s.%s FROM stdin DELIMITER ',' CSV", schemaName, tmpTableName);
        var bufferedReader = new BufferedReader(new FileReader(tmpFile));
        copyManager.copyIn(sql, bufferedReader);
      } catch (Exception e) {
        throw new RuntimeException(e);
      } finally {
        try {
          if (tmpFile != null) {
            Files.delete(tmpFile.toPath());
          }
        } catch (IOException e) {
          throw new RuntimeException(e);
        }
      }
    });
  }

  @Override
  protected DataAdapter getDataAdapter() {
    return new PostgresDataAdapter();
  }

}
