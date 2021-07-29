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

package io.airbyte.integrations.destination.snowflake;

import com.google.cloud.storage.Storage;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsConfig;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsStreamCopier;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.sql.SQLException;

public class SnowflakeGcsStreamCopier extends GcsStreamCopier {

  public SnowflakeGcsStreamCopier(String stagingFolder,
                                  DestinationSyncMode destSyncMode,
                                  String schema,
                                  String streamName,
                                  Storage storageClient,
                                  JdbcDatabase db,
                                  GcsConfig gcsConfig,
                                  ExtendedNameTransformer nameTransformer,
                                  SqlOperations sqlOperations) {
    super(stagingFolder, destSyncMode, schema, streamName, storageClient, db, gcsConfig, nameTransformer, sqlOperations);
  }

  @Override
  public void copyGcsCsvFileIntoTable(JdbcDatabase database,
                                      String gcsFileLocation,
                                      String schema,
                                      String tableName,
                                      GcsConfig gcsConfig)
      throws SQLException {
    final var copyQuery = String.format(
        "COPY INTO %s.%s FROM '%s' storage_integration = gcs_airbyte_integration file_format = (type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"');",
        schema,
        tableName,
        gcsFileLocation);

    database.execute(copyQuery);
  }

}
