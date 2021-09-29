/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3Config;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopier;
import io.airbyte.integrations.destination.redshift.manifest.Entry;
import io.airbyte.integrations.destination.redshift.manifest.Manifest;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.util.UUID;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftStreamCopier extends S3StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftStreamCopier.class);

  private final ObjectMapper objectMapper;

  public RedshiftStreamCopier(String stagingFolder,
                              DestinationSyncMode destSyncMode,
                              String schema,
                              String streamName,
                              AmazonS3 client,
                              JdbcDatabase db,
                              S3Config s3Config,
                              ExtendedNameTransformer nameTransformer,
                              SqlOperations sqlOperations) {
    super(stagingFolder, destSyncMode, schema, streamName, Strings.addRandomSuffix("", "", 3) + "_" + streamName, client, db, s3Config,
        nameTransformer, sqlOperations);
    objectMapper = new ObjectMapper();
  }

  @Override
  public void copyStagingFileToTemporaryTable() throws Exception {
    final var manifestFullS3Path = createManifest();

    LOGGER.info("Starting copy to tmp table: {} in destination for stream: {}, schema: {}, .", tmpTableName, streamName, schemaName);
    final var copyQuery = String.format(
        "COPY %s.%s FROM '%s'\n"
            + "CREDENTIALS 'aws_access_key_id=%s;aws_secret_access_key=%s'\n"
            + "CSV REGION '%s' TIMEFORMAT 'auto'\n"
            + "STATUPDATE OFF\n"
            + "MANIFEST;",
        schemaName,
        tmpTableName,
        manifestFullS3Path,
        s3Config.getAccessKeyId(),
        s3Config.getSecretAccessKey(),
        s3Config.getRegion());

    db.execute(copyQuery);
    LOGGER.info("Copy to tmp table {} in destination for stream {} complete.", tmpTableName, streamName);
  }

  @Override
  public void copyS3CsvFileIntoTable(JdbcDatabase database, String s3FileLocation, String schema, String tableName, S3Config s3Config) {
    throw new RuntimeException("Redshift Stream Copier should not be copying individual files without use of a manifest");
  }

  /**
   * Creates a manifest file and uploads the file to s3. Note: Using a manifest to COPY a set of s3
   * files into Redshift, which is in accordance AWS Redshift best practices.
   *
   * @return the full s3 path of the newly created manifest file
   */
  public String createManifest() {
    final var manifestFilePath =
        String.join("/", stagingFolder, schemaName, String.format("%s.manifest", UUID.randomUUID()));

    final var s3FilesFullPath = s3StagingFiles.stream()
        .map(filePath -> new Entry(getFullS3Path(s3Config.getBucketName(), filePath)))
        .collect(Collectors.toList());

    final var manifest = new Manifest(s3FilesFullPath);

    final String manifestContents = Exceptions.toRuntime(() -> objectMapper.writeValueAsString(manifest));
    s3Client.putObject(s3Config.getBucketName(), manifestFilePath, manifestContents);

    return getFullS3Path(s3Config.getBucketName(), manifestFilePath);
  }

}
