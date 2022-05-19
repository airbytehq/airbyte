/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.operations;

import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.sentry.AirbyteSentry;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.redshift.enums.RedshiftDataTmpTableMode;
import io.airbyte.integrations.destination.redshift.manifest.Entry;
import io.airbyte.integrations.destination.redshift.manifest.Manifest;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3StorageOperations;
import io.airbyte.integrations.destination.s3.credential.S3AccessKeyCredentialConfig;
import io.airbyte.integrations.destination.staging.StagingOperations;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import org.joda.time.DateTime;

public class RedshiftS3StagingSqlOperations extends RedshiftSqlOperations implements StagingOperations {

  private final NamingConventionTransformer nameTransformer;
  private final S3StorageOperations s3StorageOperations;
  private final S3DestinationConfig s3Config;
  private final ObjectMapper objectMapper;

  public RedshiftS3StagingSqlOperations(NamingConventionTransformer nameTransformer,
                                        AmazonS3 s3Client,
                                        S3DestinationConfig s3Config,
                                        RedshiftDataTmpTableMode redshiftDataTmpTableMode) {
    super(redshiftDataTmpTableMode);
    this.nameTransformer = nameTransformer;
    this.s3StorageOperations = new S3StorageOperations(nameTransformer, s3Client, s3Config);
    this.s3Config = s3Config;
    this.objectMapper = new ObjectMapper();
  }

  @Override
  public String getStageName(String namespace, String streamName) {
    return nameTransformer.applyDefaultCase(String.join("_",
        nameTransformer.convertStreamName(namespace),
        nameTransformer.convertStreamName(streamName)));
  }

  @Override
  public String getStagingPath(UUID connectionId, String namespace, String streamName, DateTime writeDatetime) {
    return nameTransformer.applyDefaultCase(String.format("%s/%s_%02d_%02d_%02d_%s/",
        getStageName(namespace, streamName),
        writeDatetime.year().get(),
        writeDatetime.monthOfYear().get(),
        writeDatetime.dayOfMonth().get(),
        writeDatetime.hourOfDay().get(),
        connectionId));
  }

  @Override
  public void createStageIfNotExists(JdbcDatabase database, String stageName) throws Exception {
    AirbyteSentry.executeWithTracing("CreateStageIfNotExists",
        () -> s3StorageOperations.createBucketObjectIfNotExists(stageName),
        Map.of("stage", stageName));
  }

  @Override
  public String uploadRecordsToStage(JdbcDatabase database, SerializableBuffer recordsData, String schemaName, String stageName, String stagingPath)
      throws Exception {
    return s3StorageOperations.uploadRecordsToBucket(recordsData, schemaName, stageName, stagingPath);
  }

  private String putManifest(final String manifestContents, String stagingPath) {
    String manifestFilePath = stagingPath + String.format("%s.manifest", UUID.randomUUID());
    AirbyteSentry.executeWithTracing("CreateStageIfNotExists",
        () -> s3StorageOperations.uploadManifest(s3Config.getBucketName(), manifestFilePath, manifestContents),
        Map.of("stagingPath", stagingPath, "manifestPath", manifestFilePath));
    return manifestFilePath;
  }

  @Override
  public void copyIntoTmpTableFromStage(JdbcDatabase database,
                                        String stageName,
                                        String stagingPath,
                                        List<String> stagedFiles,
                                        String dstTableName,
                                        String schemaName)
      throws Exception {
    LOGGER.info("Starting copy to tmp table from stage: {} in destination from stage: {}, schema: {}, .", dstTableName, stagingPath, schemaName);
    final var possibleManifest = Optional.ofNullable(createManifest(stagedFiles, stagingPath));
    AirbyteSentry.executeWithTracing("CopyIntoTableFromStage",
        () -> Exceptions.toRuntime(() -> possibleManifest.stream()
            .map(manifestContent -> putManifest(manifestContent, stagingPath))
            .forEach(manifestPath -> executeCopy(manifestPath, database, schemaName, dstTableName))),
        Map.of("schema", schemaName, "path", stagingPath, "table", dstTableName));
    LOGGER.info("Copy to tmp table {}.{} in destination complete.", schemaName, dstTableName);
  }

  private void executeCopy(final String manifestPath, JdbcDatabase db, String schemaName, String tmpTableName) {
    final S3AccessKeyCredentialConfig credentialConfig = (S3AccessKeyCredentialConfig) s3Config.getS3CredentialConfig();
    final var copyQuery = String.format(
        """
        COPY %s.%s FROM '%s'
        CREDENTIALS 'aws_access_key_id=%s;aws_secret_access_key=%s'
        CSV GZIP
        REGION '%s' TIMEFORMAT 'auto'
        STATUPDATE OFF
        MANIFEST;""",
        schemaName,
        tmpTableName,
        getFullS3Path(s3Config.getBucketName(), manifestPath),
        credentialConfig.getAccessKeyId(),
        credentialConfig.getSecretAccessKey(),
        s3Config.getBucketRegion());

    Exceptions.toRuntime(() -> db.execute(copyQuery));
  }

  private String createManifest(List<String> stagedFiles, String stagingPath) {
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
  public void cleanUpStage(JdbcDatabase database, String stageName, List<String> stagedFiles) throws Exception {
    AirbyteSentry.executeWithTracing("CleanStage",
        () -> s3StorageOperations.cleanUpBucketObject(stageName, stagedFiles),
        Map.of("stage", stageName));
  }

  @Override
  public void dropStageIfExists(JdbcDatabase database, String stageName) throws Exception {
    AirbyteSentry.executeWithTracing("DropStageIfExists",
        () -> s3StorageOperations.dropBucketObject(stageName),
        Map.of("stage", stageName));
  }

}
