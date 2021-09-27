/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3Config;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopierFactory;
import io.airbyte.protocol.models.DestinationSyncMode;

public class SnowflakeS3StreamCopierFactory extends S3StreamCopierFactory {

  @Override
  public StreamCopier create(String stagingFolder,
                             DestinationSyncMode syncMode,
                             String schema,
                             String streamName,
                             AmazonS3 s3Client,
                             JdbcDatabase db,
                             S3Config s3Config,
                             ExtendedNameTransformer nameTransformer,
                             SqlOperations sqlOperations)
      throws Exception {
    return new SnowflakeS3StreamCopier(stagingFolder, syncMode, schema, streamName, s3Client, db, s3Config, nameTransformer, sqlOperations);
  }

}
