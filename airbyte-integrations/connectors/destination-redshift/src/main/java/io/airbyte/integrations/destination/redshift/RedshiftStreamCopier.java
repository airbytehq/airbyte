/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3Config;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopier;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.sql.SQLException;

public class RedshiftStreamCopier extends S3StreamCopier {

  public RedshiftStreamCopier(String stagingFolder,
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
        "COPY %s.%s FROM '%s'\n"
            + "CREDENTIALS 'aws_access_key_id=%s;aws_secret_access_key=%s'\n"
            + "CSV REGION '%s' TIMEFORMAT 'auto'\n"
            + "STATUPDATE OFF;\n",
        schema,
        tableName,
        s3FileLocation,
        s3Config.getAccessKeyId(),
        s3Config.getSecretAccessKey(),
        s3Config.getRegion());

    database.execute(copyQuery);
  }

}
