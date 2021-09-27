/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3Config;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopier;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.sql.SQLException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeS3StreamCopier extends S3StreamCopier {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeS3StreamCopier.class);

  public SnowflakeS3StreamCopier(String stagingFolder,
                                 DestinationSyncMode destSyncMode,
                                 String schema,
                                 String streamName,
                                 AmazonS3 client,
                                 JdbcDatabase db,
                                 S3Config s3Config,
                                 ExtendedNameTransformer nameTransformer,
                                 SqlOperations sqlOperations) {
    super(stagingFolder, destSyncMode, schema, streamName, Strings.addRandomSuffix("", "", 3) + "_" + streamName, client, db, s3Config,
        nameTransformer, sqlOperations);
  }

  @Override
  public void copyS3CsvFileIntoTable(JdbcDatabase database, String s3FileLocation, String schema, String tableName, S3Config s3Config)
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
