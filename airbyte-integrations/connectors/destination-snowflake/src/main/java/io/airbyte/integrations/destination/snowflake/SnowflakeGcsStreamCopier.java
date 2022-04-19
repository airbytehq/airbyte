/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.google.cloud.storage.Storage;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.StagingFilenameGenerator;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsConfig;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsStreamCopier;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.sql.SQLException;

public class SnowflakeGcsStreamCopier extends GcsStreamCopier {

  public SnowflakeGcsStreamCopier(final String stagingFolder,
                                  final DestinationSyncMode destSyncMode,
                                  final String schema,
                                  final String streamName,
                                  final Storage storageClient,
                                  final JdbcDatabase db,
                                  final GcsConfig gcsConfig,
                                  final ExtendedNameTransformer nameTransformer,
                                  final SqlOperations sqlOperations,
                                  final StagingFilenameGenerator stagingFilenameGenerator) {
    super(stagingFolder, destSyncMode, schema, streamName, storageClient, db, gcsConfig, nameTransformer, sqlOperations);
    this.filenameGenerator = stagingFilenameGenerator;
  }

  @Override
  public void copyGcsCsvFileIntoTable(final JdbcDatabase database,
                                      final String gcsFileLocation,
                                      final String schema,
                                      final String tableName,
                                      final GcsConfig gcsConfig)
      throws SQLException {
    final var copyQuery = String.format(
        "COPY INTO %s.%s FROM '%s' storage_integration = gcs_airbyte_integration file_format = (type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"');",
        schema,
        tableName,
        gcsFileLocation);

    database.execute(copyQuery);
  }

}
