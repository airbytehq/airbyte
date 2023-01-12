/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.copiers;

import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3CopyConfig;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopier;
import io.airbyte.integrations.destination.redshift.manifest.Entry;
import io.airbyte.integrations.destination.redshift.manifest.Manifest;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.credential.S3AccessKeyCredentialConfig;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftStreamCopier extends S3StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftStreamCopier.class);
  // From https://docs.aws.amazon.com/redshift/latest/dg/t_loading-tables-from-s3.html
  // "Split your load data files so that the files are about equal size, between 1 MB and 1 GB after
  // compression"
  public static final int MAX_PARTS_PER_FILE = 4;

  private final ObjectMapper objectMapper;
  private String manifestFilePath = null;

  public RedshiftStreamCopier(final String stagingFolder,
                              final String schema,
                              final AmazonS3 client,
                              final JdbcDatabase db,
                              final S3CopyConfig config,
                              final ExtendedNameTransformer nameTransformer,
                              final SqlOperations sqlOperations,
                              final ConfiguredAirbyteStream configuredAirbyteStream) {
    this(
        stagingFolder,
        schema,
        client,
        db,
        config,
        nameTransformer,
        sqlOperations,
        Timestamp.from(Instant.now()),
        configuredAirbyteStream);
  }

  @VisibleForTesting
  RedshiftStreamCopier(final String stagingFolder,
                       final String schema,
                       final AmazonS3 client,
                       final JdbcDatabase db,
                       final S3CopyConfig config,
                       final ExtendedNameTransformer nameTransformer,
                       final SqlOperations sqlOperations,
                       final Timestamp uploadTime,
                       final ConfiguredAirbyteStream configuredAirbyteStream) {
    super(stagingFolder,
        schema,
        client,
        db,
        config,
        nameTransformer,
        sqlOperations,
        configuredAirbyteStream,
        uploadTime,
        MAX_PARTS_PER_FILE);
    objectMapper = new ObjectMapper();
  }

  @Override
  public void copyStagingFileToTemporaryTable() {
    final var possibleManifest = Optional.ofNullable(createManifest());
    LOGGER.info("Starting copy to tmp table: {} in destination for stream: {}, schema: {}, .", tmpTableName, streamName, schemaName);
    possibleManifest.stream()
        .map(this::putManifest)
        .forEach(this::executeCopy);
    LOGGER.info("Copy to tmp table {} in destination for stream {} complete.", tmpTableName, streamName);
  }

  @Override
  public void copyS3CsvFileIntoTable(final JdbcDatabase database,
                                     final String s3FileLocation,
                                     final String schema,
                                     final String tableName,
                                     final S3DestinationConfig s3Config) {
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
    if (getStagingFiles().isEmpty()) {
      return null;
    }

    final var s3FileEntries = getStagingFiles().stream()
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
  private String putManifest(final String manifestContents) {
    manifestFilePath =
        String.join("/", s3Config.getBucketPath(), stagingFolder, schemaName, String.format("%s.manifest", UUID.randomUUID()));

    s3Client.putObject(s3Config.getBucketName(), manifestFilePath, manifestContents);

    return manifestFilePath;
  }

  /**
   * Run Redshift COPY command with the given manifest file
   *
   * @param manifestPath the path in S3 to the manifest file
   */
  private void executeCopy(final String manifestPath) {
    final S3AccessKeyCredentialConfig credentialConfig = (S3AccessKeyCredentialConfig) s3Config.getS3CredentialConfig();
    final var copyQuery = String.format(
        "COPY %s.%s FROM '%s'\n"
            + "CREDENTIALS 'aws_access_key_id=%s;aws_secret_access_key=%s'\n"
            + "CSV REGION '%s' TIMEFORMAT 'auto'\n"
            + "STATUPDATE OFF\n"
            + "MANIFEST;",
        schemaName,
        tmpTableName,
        getFullS3Path(s3Config.getBucketName(), manifestPath),
        credentialConfig.getAccessKeyId(),
        credentialConfig.getSecretAccessKey(),
        s3Config.getBucketRegion());

    Exceptions.toRuntime(() -> db.execute(copyQuery));
  }

}
