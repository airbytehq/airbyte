/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static io.airbyte.integrations.destination.snowflake.SnowflakeS3StreamCopier.MAX_FILES_PER_COPY;

import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
import com.google.common.collect.Lists;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.StagingFilenameGenerator;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageConfig;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageStreamCopier;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeAzureBlobStorageStreamCopier extends AzureBlobStorageStreamCopier implements SnowflakeParallelCopyStreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeAzureBlobStorageStreamCopier.class);

  public SnowflakeAzureBlobStorageStreamCopier(final String stagingFolder,
                                               final DestinationSyncMode destSyncMode,
                                               final String schema,
                                               final String streamName,
                                               final SpecializedBlobClientBuilder specializedBlobClientBuilder,
                                               final JdbcDatabase db,
                                               final AzureBlobStorageConfig azureBlobConfig,
                                               final ExtendedNameTransformer nameTransformer,
                                               final SqlOperations sqlOperations,
                                               final StagingFilenameGenerator stagingFilenameGenerator) {
    super(stagingFolder, destSyncMode, schema, streamName, specializedBlobClientBuilder, db, azureBlobConfig, nameTransformer, sqlOperations);
    this.filenameGenerator = stagingFilenameGenerator;
  }

  @Override
  public void copyStagingFileToTemporaryTable() throws Exception {
    List<List<String>> partitions = Lists.partition(new ArrayList<>(azureStagingFiles), MAX_FILES_PER_COPY);
    LOGGER.info("Starting parallel copy to tmp table: {} in destination for stream: {}, schema: {}. Chunks count {}", tmpTableName, streamName,
        schemaName, partitions.size());

    copyFilesInParallel(partitions);
    LOGGER.info("Copy to tmp table {} in destination for stream {} complete.", tmpTableName, streamName);
  }

  @Override
  public void copyAzureBlobCsvFileIntoTable(
                                            JdbcDatabase database,
                                            String snowflakeAzureExternalStageName,
                                            String schema,
                                            String tableName,
                                            AzureBlobStorageConfig config)
      throws SQLException {
    throw new RuntimeException("Snowflake Azure Stream Copier should not copy individual files without use of a parallel copy");
  }

  @Override
  public void copyIntoStage(List<String> files) {

    final var copyQuery = String.format(
        "COPY INTO %s.%s FROM '%s'"
            + " credentials=(azure_sas_token='%s')"
            + " file_format = (type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"')"
            + " files = (" + generateFilesList(files) + " );",
        schemaName,
        tmpTableName,
        generateBucketPath(),
        azureBlobConfig.getSasToken());

    Exceptions.toRuntime(() -> db.execute(copyQuery));
  }

  @Override
  public String generateBucketPath() {
    return "azure://" + azureBlobConfig.getAccountName() + "." + azureBlobConfig.getEndpointDomainName()
        + "/" + azureBlobConfig.getContainerName() + "/" + stagingFolder + "/" + schemaName + "/";
  }

}
