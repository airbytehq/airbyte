/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.StringJoiner;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeS3StreamCopier extends S3StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeS3StreamCopier.class);

  // From https://docs.aws.amazon.com/redshift/latest/dg/t_loading-tables-from-s3.html
  // "Split your load data files so that the files are about equal size, between 1 MB and 1 GB after
  // compression"
  public static final int MAX_PARTS_PER_FILE = 4;

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
    List<List<String>> partition = Lists.partition(new ArrayList<>(stagingWritersByFile.keySet()), 10);
//    List<List<String>> partition = Lists.partition(new ArrayList<>(stagingWritersByFile.keySet()), 10);
    for (int i = 0; i < partition.size(); i++) {
      List<String> strings = partition.get(i);
      LOGGER.info("Starting copy chunk {} to tmp table: {} in destination for stream: {}, schema: {}. Chunks count {}", i, tmpTableName, streamName,
          schemaName, partition.size());
      executeCopy(strings);
    }
    LOGGER.info("Copy to tmp table {} in destination for stream {} complete.", tmpTableName, streamName);
  }

  private void executeCopy(List<String> files) throws SQLException {
    final var copyQuery = String.format(
        "COPY INTO %s.%s FROM '%s' "
            + "CREDENTIALS=(aws_key_id='%s' aws_secret_key='%s') "
            + "file_format = (type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"') "
            + "files = (" + generateFilesList(files) + " );",
        schemaName,
        tmpTableName,
        generateBucketPath(),
        s3Config.getAccessKeyId(),
        s3Config.getSecretAccessKey());

    Exceptions.toRuntime(() -> db.execute(copyQuery));
  }

  private String generateBucketPath() {
    return "s3://" + s3Config.getBucketName() + "/" + schemaName + "/" + streamName + "/";
  }

  private String generateFilesList(List<String> files) {
    StringJoiner joiner = new StringJoiner(",");
    files.forEach(filename -> joiner.add("'" + filename.substring(filename.lastIndexOf("/") + 1) + "'"));
    return joiner.toString();
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
