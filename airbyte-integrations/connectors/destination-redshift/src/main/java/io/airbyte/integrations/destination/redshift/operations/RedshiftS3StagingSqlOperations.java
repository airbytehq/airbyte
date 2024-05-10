/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.operations;

import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.cdk.integrations.destination.s3.AesCbcEnvelopeEncryption;
import io.airbyte.cdk.integrations.destination.s3.AesCbcEnvelopeEncryptionBlobDecorator;
import io.airbyte.cdk.integrations.destination.s3.EncryptionConfig;
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.cdk.integrations.destination.s3.S3StorageOperations;
import io.airbyte.cdk.integrations.destination.s3.credential.S3AccessKeyCredentialConfig;
import io.airbyte.cdk.integrations.destination.staging.StagingOperations;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.integrations.destination.redshift.manifest.Entry;
import io.airbyte.integrations.destination.redshift.manifest.Manifest;
import java.time.Instant;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.util.Base64;
import java.util.Base64.Encoder;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftS3StagingSqlOperations extends RedshiftSqlOperations implements StagingOperations {

  private static final Encoder BASE64_ENCODER = Base64.getEncoder();
  private final NamingConventionTransformer nameTransformer;
  private final S3StorageOperations s3StorageOperations;
  private final S3DestinationConfig s3Config;
  private final ObjectMapper objectMapper;
  private final byte[] keyEncryptingKey;

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftS3StagingSqlOperations.class);

  public RedshiftS3StagingSqlOperations(final NamingConventionTransformer nameTransformer,
                                        final AmazonS3 s3Client,
                                        final S3DestinationConfig s3Config,
                                        final EncryptionConfig encryptionConfig) {
    this.nameTransformer = nameTransformer;
    this.s3StorageOperations = new S3StorageOperations(nameTransformer, s3Client, s3Config);
    this.s3Config = s3Config;
    this.objectMapper = new ObjectMapper();
    if (encryptionConfig instanceof final AesCbcEnvelopeEncryption e) {
      this.s3StorageOperations.addBlobDecorator(new AesCbcEnvelopeEncryptionBlobDecorator(e.key()));
      this.keyEncryptingKey = e.key();
    } else {
      this.keyEncryptingKey = null;
    }
  }

  @Override
  public String getStagingPath(final UUID connectionId,
                               final String namespace,
                               final String streamName,
                               final String outputTableName,
                               final Instant writeDatetime) {
    final String bucketPath = s3Config.getBucketPath();
    final String prefix = bucketPath.isEmpty() ? "" : bucketPath + (bucketPath.endsWith("/") ? "" : "/");
    final ZonedDateTime zdt = writeDatetime.atZone(ZoneOffset.UTC);
    return nameTransformer.applyDefaultCase(String.format("%s%s/%s_%02d_%02d_%02d_%s/",
        prefix,
        nameTransformer.applyDefaultCase(nameTransformer.convertStreamName(outputTableName)),
        zdt.getYear(),
        zdt.getMonthValue(),
        zdt.getDayOfMonth(),
        zdt.getHour(),
        connectionId));
  }

  @Override
  public String getStageName(final String namespace, final String streamName) {
    return "garbage-unused";
  }

  @Override
  public void createStageIfNotExists(final JdbcDatabase database, final String stageName) throws Exception {
    s3StorageOperations.createBucketIfNotExists();
  }

  @Override
  public String uploadRecordsToStage(final JdbcDatabase database,
                                     final SerializableBuffer recordsData,
                                     final String schemaName,
                                     final String stageName,
                                     final String stagingPath)
      throws Exception {
    return s3StorageOperations.uploadRecordsToBucket(recordsData, schemaName, stagingPath);
  }

  private String putManifest(final String manifestContents, final String stagingPath) {
    final String manifestFilePath = stagingPath + String.format("%s.manifest", UUID.randomUUID());
    s3StorageOperations.uploadManifest(manifestFilePath, manifestContents);
    return manifestFilePath;
  }

  @Override
  public void copyIntoTableFromStage(final JdbcDatabase database,
                                     final String stageName,
                                     final String stagingPath,
                                     final List<String> stagedFiles,
                                     final String tableName,
                                     final String schemaName)
      throws Exception {
    LOGGER.info("Starting copy to target table from stage: {} in destination from stage: {}, schema: {}, .",
        tableName, stagingPath, schemaName);
    final var possibleManifest = Optional.ofNullable(createManifest(stagedFiles, stagingPath));
    Exceptions.toRuntime(() -> possibleManifest.stream()
        .map(manifestContent -> putManifest(manifestContent, stagingPath))
        .forEach(manifestPath -> executeCopy(manifestPath, database, schemaName, tableName)));
    LOGGER.info("Copy to target table {}.{} in destination complete.", schemaName, tableName);
  }

  /**
   * Generates the COPY data from staging files into target table
   */
  private void executeCopy(final String manifestPath, final JdbcDatabase db, final String schemaName, final String tableName) {
    final S3AccessKeyCredentialConfig credentialConfig = (S3AccessKeyCredentialConfig) s3Config.getS3CredentialConfig();
    final String encryptionClause;
    if (keyEncryptingKey == null) {
      encryptionClause = "";
    } else {
      encryptionClause = String.format(" encryption = (type = 'aws_cse' master_key = '%s')", BASE64_ENCODER.encodeToString(keyEncryptingKey));
    }

    final var copyQuery = String.format(
        """
        COPY %s.%s FROM '%s'
        CREDENTIALS 'aws_access_key_id=%s;aws_secret_access_key=%s'
        %s
        CSV GZIP
        REGION '%s' TIMEFORMAT 'auto'
        STATUPDATE OFF
        MANIFEST;""",
        schemaName,
        tableName,
        getFullS3Path(s3Config.getBucketName(), manifestPath),
        credentialConfig.getAccessKeyId(),
        credentialConfig.getSecretAccessKey(),
        encryptionClause,
        s3Config.getBucketRegion());

    Exceptions.toRuntime(() -> db.execute(copyQuery));
  }

  private String createManifest(final List<String> stagedFiles, final String stagingPath) {
    if (stagedFiles.isEmpty()) {
      return null;
    }

    final var s3FileEntries = stagedFiles.stream()
        .map(file -> new Entry(getManifestPath(s3Config.getBucketName(), file, stagingPath)))
        .collect(Collectors.toList());
    final var manifest = new Manifest(s3FileEntries);

    return Exceptions.toRuntime(() -> objectMapper.writeValueAsString(manifest));
  }

  private static String getFullS3Path(final String s3BucketName, final String s3StagingFile) {
    return String.join("/", "s3:/", s3BucketName, s3StagingFile);
  }

  private static String getManifestPath(final String s3BucketName, final String s3StagingFile, final String stagingPath) {
    return "s3://" + s3BucketName + "/" + stagingPath + s3StagingFile;
  }

  @Override
  public void dropStageIfExists(final JdbcDatabase database, final String stageName, final String stagingPath) throws Exception {
    // stageName is unused here but used in Snowflake. This interface needs to be fixed.
    s3StorageOperations.dropBucketObject(stagingPath);
  }

}
