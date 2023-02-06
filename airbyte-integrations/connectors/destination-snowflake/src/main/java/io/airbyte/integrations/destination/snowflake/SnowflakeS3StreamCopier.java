/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.amazonaws.services.s3.AmazonS3;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3CopyConfig;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopier;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.credential.S3AccessKeyCredentialConfig;
import io.airbyte.integrations.destination.s3.util.S3OutputPathHelper;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeS3StreamCopier extends S3StreamCopier implements SnowflakeParallelCopyStreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeS3StreamCopier.class);

  // From https://docs.aws.amazon.com/redshift/latest/dg/t_loading-tables-from-s3.html
  // "Split your load data files so that the files are about equal size, between 1 MB and 1 GB after
  // compression"
  public static final int MAX_PARTS_PER_FILE = 4;
  public static final int MAX_FILES_PER_COPY = 1000;

  public SnowflakeS3StreamCopier(final String stagingFolder,
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
  SnowflakeS3StreamCopier(final String stagingFolder,
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
  }

  @Override
  public void copyStagingFileToTemporaryTable() throws Exception {
    final List<List<String>> partitions = Lists.partition(new ArrayList<>(getStagingFiles()), MAX_FILES_PER_COPY);
    LOGGER.info("Starting parallel copy to tmp table: {} in destination for stream: {}, schema: {}. Chunks count {}", tmpTableName, streamName,
        schemaName, partitions.size());

    copyFilesInParallel(partitions);
    LOGGER.info("Copy to tmp table {} in destination for stream {} complete.", tmpTableName, streamName);
  }

  @Override
  public void copyIntoStage(final List<String> files) {
    final S3AccessKeyCredentialConfig credentialConfig = (S3AccessKeyCredentialConfig) s3Config.getS3CredentialConfig();
    final var copyQuery = String.format(
        "COPY INTO %s.%s FROM '%s' "
            + "CREDENTIALS=(aws_key_id='%s' aws_secret_key='%s') "
            + "file_format = (type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"') "
            + "files = (" + generateFilesList(files) + " );",
        schemaName,
        tmpTableName,
        generateBucketPath(),
        credentialConfig.getAccessKeyId(),
        credentialConfig.getSecretAccessKey());

    Exceptions.toRuntime(() -> db.execute(copyQuery));
  }

  @Override
  public String generateBucketPath() {
    return "s3://" + s3Config.getBucketName() + "/"
        + S3OutputPathHelper.getOutputPrefix(s3Config.getBucketPath(), configuredAirbyteStream.getStream()) + "/";
  }

  @Override
  public void copyS3CsvFileIntoTable(final JdbcDatabase database,
                                     final String s3FileLocation,
                                     final String schema,
                                     final String tableName,
                                     final S3DestinationConfig s3Config)
      throws SQLException {
    throw new RuntimeException("Snowflake Stream Copier should not copy individual files without use of a parallel copy");

  }

}
