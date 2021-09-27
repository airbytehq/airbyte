/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
