/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.s3.LegacyS3StreamCopier;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.sql.SQLException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeS3StreamCopier extends LegacyS3StreamCopier {

  public SnowflakeS3StreamCopier(final String stagingFolder,
                                 final DestinationSyncMode destSyncMode,
                                 final String schema,
                                 final String streamName,
                                 final AmazonS3 client,
                                 final JdbcDatabase db,
                                 final S3DestinationConfig s3Config,
                                 final ExtendedNameTransformer nameTransformer,
                                 final SqlOperations sqlOperations) {
    super(stagingFolder, destSyncMode, schema, streamName, client, db, s3Config, nameTransformer, sqlOperations);
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
