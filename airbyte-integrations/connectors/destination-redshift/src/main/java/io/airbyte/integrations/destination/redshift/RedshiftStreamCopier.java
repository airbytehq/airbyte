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
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftStreamCopier extends S3StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftStreamCopier.class);
  private static final int FILE_PREFIX_LENGTH = 5;

  private final ObjectMapper objectMapper;
  private String manifestFilePath = null;

  public RedshiftStreamCopier(String stagingFolder,
                              DestinationSyncMode destSyncMode,
                              String schema,
                              String streamName,
                              AmazonS3 client,
                              JdbcDatabase db,
                              S3Config s3Config,
                              ExtendedNameTransformer nameTransformer,
                              SqlOperations sqlOperations) {
    super(stagingFolder, destSyncMode, schema, streamName, Strings.addRandomSuffix("", "", FILE_PREFIX_LENGTH) + "_" + streamName,
        client, db, s3Config, nameTransformer, sqlOperations);
    objectMapper = new ObjectMapper();
  }

  @Override
  public void copyStagingFileToTemporaryTable() {
    var possibleManifest = Optional.ofNullable(createManifest());
    LOGGER.info("Starting copy to tmp table: {} in destination for stream: {}, schema: {}, .", tmpTableName, streamName, schemaName);
    possibleManifest.stream()
        .map(this::putManifest)
        .forEach(this::executeCopy);
    LOGGER.info("Copy to tmp table {} in destination for stream {} complete.", tmpTableName, streamName);
  }

  @Override
  public void copyS3CsvFileIntoTable(JdbcDatabase database, String s3FileLocation, String schema, String tableName, S3Config s3Config) {
    throw new RuntimeException("Redshift Stream Copier should not copy individual files without use of a manifest");
  }

  @Override
  public void removeFileAndDropTmpTable() throws Exception {
    super.removeFileAndDropTmpTable();
    if (manifestFilePath != null) {
      LOGGER.info("Begin cleaning s3 manifest file {}.", manifestFilePath);
      if (s3Client.doesObjectExist(s3Config.getBucketName(), manifestFilePath)) {
        s3Client.deleteObject(s3Config.getBucketName(), manifestFilePath);
      }
      LOGGER.info("S3 manifest file {} cleaned.", manifestFilePath);
    }
  }

  /**
   * Creates the contents of a manifest file given the `s3StagingFiles`. There must be at least one
   * entry in a manifest file otherwise it is not considered valid for the COPY command.
   *
   * @return null if no stagingFiles exist otherwise the manifest body String
   */
  private String createManifest() {
    if (s3StagingFiles.isEmpty()) {
      return null;
    }

    final var s3FileEntries = s3StagingFiles.stream()
        .map(filePath -> new Entry(getFullS3Path(s3Config.getBucketName(), filePath)))
        .collect(Collectors.toList());
    final var manifest = new Manifest(s3FileEntries);

    return Exceptions.toRuntime(() -> objectMapper.writeValueAsString(manifest));
  }

  /**
   * Upload the supplied manifest file to S3
   *
   * @param manifestContents the manifest contents, never null
   * @return the path where the manifest file was placed in S3
   */
  private String putManifest(String manifestContents) {
    manifestFilePath =
        String.join("/", stagingFolder, schemaName, String.format("%s.manifest", UUID.randomUUID()));

    s3Client.putObject(s3Config.getBucketName(), manifestFilePath, manifestContents);

    return manifestFilePath;
  }

  /**
   * Run Redshift COPY command with the given manifest file
   *
   * @param manifestPath the path in S3 to the manifest file
   */
  private void executeCopy(String manifestPath) {
    final var copyQuery = String.format(
        "COPY %s.%s FROM '%s'\n"
            + "CREDENTIALS 'aws_access_key_id=%s;aws_secret_access_key=%s'\n"
            + "CSV REGION '%s' TIMEFORMAT 'auto'\n"
            + "STATUPDATE OFF\n"
            + "MANIFEST;",
        schemaName,
        tmpTableName,
        getFullS3Path(s3Config.getBucketName(), manifestPath),
        s3Config.getAccessKeyId(),
        s3Config.getSecretAccessKey(),
        s3Config.getRegion());

    Exceptions.toRuntime(() -> db.execute(copyQuery));
  }

}
