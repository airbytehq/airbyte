/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopierFactory;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.protocol.models.DestinationSyncMode;

public class SnowflakeS3StreamCopierFactory extends S3StreamCopierFactory {

  @Override
  public StreamCopier create(final String stagingFolder,
      final DestinationSyncMode syncMode,
      final String schema,
      final String streamName,
      final AmazonS3 s3Client,
      final JdbcDatabase db,
      final S3DestinationConfig s3Config,
      final ExtendedNameTransformer nameTransformer,
      final SqlOperations sqlOperations)
      throws Exception {
    return new SnowflakeS3StreamCopier(stagingFolder, syncMode, schema, streamName, s3Client, db, s3Config, nameTransformer, sqlOperations);
  }

}
