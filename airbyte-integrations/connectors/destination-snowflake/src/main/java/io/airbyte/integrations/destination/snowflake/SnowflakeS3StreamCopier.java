/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.amazonaws.services.s3.AmazonS3;
import com.google.common.annotations.VisibleForTesting;
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

public class SnowflakeS3StreamCopier extends S3StreamCopier {

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
  public void copyS3CsvFileIntoTable(final JdbcDatabase database,
                                     final String s3FileLocation,
                                     final String schema,
                                     final String tableName,
                                     final S3DestinationConfig s3Config)
      throws SQLException {
    final var copyQuery = String.format(
        "COPY INTO %s.%s FROM '%s' "
            + "CREDENTIALS=(aws_key_id='%s' aws_secret_key='%s') "
            + "file_format = (type = csv field_delimiter = ',' skip_header = 0 FIELD_OPTIONALLY_ENCLOSED_BY = '\"');",
        schema,
        tableName,
        s3FileLocation,
        s3Config.getAccessKeyId(),
        s3Config.getSecretAccessKey());

    database.execute(copyQuery);
  }

}
