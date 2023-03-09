/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.s3.AesCbcEnvelopeEncryption;
import io.airbyte.integrations.destination.s3.AesCbcEnvelopeEncryptionBlobDecorator;
import io.airbyte.integrations.destination.s3.EncryptionConfig;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3StorageOperations;
import io.airbyte.integrations.destination.s3.credential.S3AccessKeyCredentialConfig;
import io.airbyte.integrations.destination.staging.StagingOperations;
import java.util.Base64;
import java.util.Base64.Encoder;
import java.util.List;
import java.util.UUID;
import org.joda.time.DateTime;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeS3StagingSqlOperations extends SnowflakeSqlOperations implements StagingOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSqlOperations.class);
  private static final Encoder BASE64_ENCODER = Base64.getEncoder();
  private static final String COPY_QUERY = "COPY INTO %s.%s FROM '%s' "
      + "CREDENTIALS=(aws_key_id='%s' aws_secret_key='%s') "
      + "file_format = (type = csv compression = auto field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"')";

  private final NamingConventionTransformer nameTransformer;
  private final S3StorageOperations s3StorageOperations;
  private final S3DestinationConfig s3Config;
  private final byte[] keyEncryptingKey;

  public SnowflakeS3StagingSqlOperations(final NamingConventionTransformer nameTransformer,
                                         final AmazonS3 s3Client,
                                         final S3DestinationConfig s3Config,
                                         final EncryptionConfig encryptionConfig) {
    this.nameTransformer = nameTransformer;
    this.s3StorageOperations = new S3StorageOperations(nameTransformer, s3Client, s3Config);
    this.s3Config = s3Config;
    if (encryptionConfig instanceof AesCbcEnvelopeEncryption e) {
      this.s3StorageOperations.addBlobDecorator(new AesCbcEnvelopeEncryptionBlobDecorator(e.key()));
      this.keyEncryptingKey = e.key();
    } else {
      this.keyEncryptingKey = null;
    }
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
    return s3StorageOperations.uploadRecordsToBucket(recordsData, schemaName, stageName, stagingPath);
  }

  @Override
  public void createStageIfNotExists(final JdbcDatabase database, final String stageName) {
    s3StorageOperations.createBucketIfNotExists();
  }

  @Override
  public void copyIntoTableFromStage(final JdbcDatabase database,
                                        final String stageName,
                                        final String stagingPath,
                                        final List<String> stagedFiles,
                                        final String tableName,
                                        final String schemaName) {
    LOGGER.info("Starting copy to target table from stage: {} in destination from stage: {}, schema: {}, .",
        tableName, stagingPath, schemaName);
    // Print actual SQL query if user needs to manually force reload from staging
    Exceptions.toRuntime(() -> database.execute(getCopyQuery(stagingPath, stagedFiles,
        tableName, schemaName)));
    LOGGER.info("Copy to target table {}.{} in destination complete.", schemaName, tableName);
  }

  protected String getCopyQuery(final String stagingPath,
                                final List<String> stagedFiles,
                                final String dstTableName,
                                final String schemaName) {
    final S3AccessKeyCredentialConfig credentialConfig = (S3AccessKeyCredentialConfig) s3Config.getS3CredentialConfig();
    final String encryptionClause;
    if (keyEncryptingKey == null) {
      encryptionClause = "";
    } else {
      encryptionClause = String.format(" encryption = (type = 'aws_cse' master_key = '%s')", BASE64_ENCODER.encodeToString(keyEncryptingKey));
    }
    return String.format(COPY_QUERY + generateFilesList(stagedFiles) + encryptionClause + ";",
        schemaName,
        dstTableName,
        generateBucketPath(stagingPath),
        credentialConfig.getAccessKeyId(),
        credentialConfig.getSecretAccessKey());
  }

  private String generateBucketPath(final String stagingPath) {
    return "s3://" + s3Config.getBucketName() + "/" + stagingPath;
  }

  @Override
  public void dropStageIfExists(final JdbcDatabase database, final String stageName) {
    s3StorageOperations.dropBucketObject(stageName);
  }

  @Override
  public void cleanUpStage(final JdbcDatabase database, final String stageName, final List<String> stagedFiles) {
    s3StorageOperations.cleanUpBucketObject(stageName, stagedFiles);
  }

}
