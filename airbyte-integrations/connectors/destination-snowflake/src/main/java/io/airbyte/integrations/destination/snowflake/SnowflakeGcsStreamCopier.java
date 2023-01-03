/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static io.airbyte.integrations.destination.snowflake.SnowflakeS3StreamCopier.MAX_FILES_PER_COPY;

import com.google.cloud.storage.Storage;
import com.google.common.collect.Lists;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.StagingFilenameGenerator;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsConfig;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsStreamCopier;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeGcsStreamCopier extends GcsStreamCopier implements SnowflakeParallelCopyStreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeGcsStreamCopier.class);

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
  public void copyStagingFileToTemporaryTable() throws Exception {
    List<List<String>> partitions = Lists.partition(new ArrayList<>(gcsStagingFiles), MAX_FILES_PER_COPY);
    LOGGER.info("Starting parallel copy to tmp table: {} in destination for stream: {}, schema: {}. Chunks count {}", tmpTableName, streamName,
        schemaName, partitions.size());

    copyFilesInParallel(partitions);
    LOGGER.info("Copy to tmp table {} in destination for stream {} complete.", tmpTableName, streamName);
  }

  @Override
  public void copyIntoStage(List<String> files) {

    final var copyQuery = String.format(
        "COPY INTO %s.%s FROM '%s' storage_integration = gcs_airbyte_integration "
            + " file_format = (type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"') "
            + "files = (" + generateFilesList(files) + " );",
        schemaName,
        tmpTableName,
        generateBucketPath());

    Exceptions.toRuntime(() -> db.execute(copyQuery));
  }

  @Override
  public String generateBucketPath() {
    return "gcs://" + gcsConfig.getBucketName() + "/" + stagingFolder + "/" + schemaName + "/";
  }

  @Override
  public void copyGcsCsvFileIntoTable(final JdbcDatabase database,
                                      final String gcsFileLocation,
                                      final String schema,
                                      final String tableName,
                                      final GcsConfig gcsConfig)
      throws SQLException {
    throw new RuntimeException("Snowflake GCS Stream Copier should not copy individual files without use of a parallel copy");

  }

}
