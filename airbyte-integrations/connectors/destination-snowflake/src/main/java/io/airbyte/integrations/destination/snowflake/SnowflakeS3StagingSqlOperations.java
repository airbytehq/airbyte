/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.sentry.AirbyteSentry;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3StorageOperations;
import io.airbyte.integrations.destination.s3.credential.S3AccessKeyCredentialConfig;
import io.airbyte.integrations.destination.staging.StagingOperations;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.joda.time.DateTime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeS3StagingSqlOperations extends SnowflakeSqlOperations implements StagingOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSqlOperations.class);
  private static final String COPY_QUERY = "COPY INTO %s.%s FROM '%s' "
      + "CREDENTIALS=(aws_key_id='%s' aws_secret_key='%s') "
      + "file_format = (type = csv compression = auto field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"')";

  private final NamingConventionTransformer nameTransformer;
  private final S3StorageOperations s3StorageOperations;
  private final S3DestinationConfig s3Config;

  public SnowflakeS3StagingSqlOperations(final NamingConventionTransformer nameTransformer,
                                         final AmazonS3 s3Client,
                                         final S3DestinationConfig s3Config) {
    this.nameTransformer = nameTransformer;
    this.s3StorageOperations = new S3StorageOperations(nameTransformer, s3Client, s3Config);
    this.s3Config = s3Config;
  }

  @Override
  public String getStageName(final String namespace, final String streamName) {
    return nameTransformer.applyDefaultCase(String.join("_",
        nameTransformer.convertStreamName(namespace),
        nameTransformer.convertStreamName(streamName)));
  }

  @Override
  public String getStagingPath(final UUID connectionId, final String namespace, final String streamName, final DateTime writeDatetime) {
    // see https://docs.snowflake.com/en/user-guide/data-load-considerations-stage.html
    return nameTransformer.applyDefaultCase(String.format("%s/%s/%02d/%02d/%02d/%s/",
        getStageName(namespace, streamName),
        writeDatetime.year().get(),
        writeDatetime.monthOfYear().get(),
        writeDatetime.dayOfMonth().get(),
        writeDatetime.hourOfDay().get(),
        connectionId));
  }

  @Override
  public String uploadRecordsToStage(final JdbcDatabase database,
                                     final SerializableBuffer recordsData,
                                     final String schemaName,
                                     final String stageName,
                                     final String stagingPath) {
    return AirbyteSentry.queryWithTracing("UploadRecordsToStage",
        () -> s3StorageOperations.uploadRecordsToBucket(recordsData, schemaName, stageName, stagingPath),
        Map.of("stage", stageName, "path", stagingPath));
  }

  @Override
  public void createStageIfNotExists(final JdbcDatabase database, final String stageName) {
    AirbyteSentry.executeWithTracing("CreateStageIfNotExists",
        () -> s3StorageOperations.createBucketObjectIfNotExists(stageName),
        Map.of("stage", stageName));
  }

  @Override
  public void copyIntoTmpTableFromStage(final JdbcDatabase database,
                                        final String stageName,
                                        final String stagingPath,
                                        final List<String> stagedFiles,
                                        final String dstTableName,
                                        final String schemaName) {
    LOGGER.info("Starting copy to tmp table from stage: {} in destination from stage: {}, schema: {}, .", dstTableName, stagingPath, schemaName);
    // Print actual SQL query if user needs to manually force reload from staging
    AirbyteSentry.executeWithTracing("CopyIntoTableFromStage",
        () -> Exceptions.toRuntime(() -> database.execute(getCopyQuery(stageName, stagingPath, stagedFiles, dstTableName, schemaName))),
        Map.of("schema", schemaName, "path", stagingPath, "table", dstTableName));
    LOGGER.info("Copy to tmp table {}.{} in destination complete.", schemaName, dstTableName);
  }

  protected String getCopyQuery(final String stageName,
                                final String stagingPath,
                                final List<String> stagedFiles,
                                final String dstTableName,
                                final String schemaName) {
    final S3AccessKeyCredentialConfig credentialConfig = (S3AccessKeyCredentialConfig) s3Config.getS3CredentialConfig();
    return String.format(COPY_QUERY + generateFilesList(stagedFiles) + ";",
        schemaName,
        dstTableName,
        generateBucketPath(stageName, stagingPath),
        credentialConfig.getAccessKeyId(),
        credentialConfig.getSecretAccessKey());
  }

  private String generateBucketPath(final String stageName, final String stagingPath) {
    return "s3://" + s3Config.getBucketName() + "/" + stagingPath;
  }

  @Override
  public void dropStageIfExists(final JdbcDatabase database, final String stageName) {
    AirbyteSentry.executeWithTracing("DropStageIfExists",
        () -> s3StorageOperations.dropBucketObject(stageName),
        Map.of("stage", stageName));
  }

  @Override
  public void cleanUpStage(final JdbcDatabase database, final String stageName, final List<String> stagedFiles) {
    AirbyteSentry.executeWithTracing("CleanStage",
        () -> s3StorageOperations.cleanUpBucketObject(stageName, stagedFiles),
        Map.of("stage", stageName));
  }

}
