/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3CopyConfig;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopierFactory;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;

public class SnowflakeS3StreamCopierFactory extends S3StreamCopierFactory {

  @Override
  protected StreamCopier create(String stagingFolder,
                                String schema,
                                AmazonS3 s3Client,
                                JdbcDatabase db,
                                S3CopyConfig config,
                                ExtendedNameTransformer nameTransformer,
                                SqlOperations sqlOperations,
                                ConfiguredAirbyteStream configuredStream)
      throws Exception {
    return new SnowflakeS3StreamCopier(stagingFolder, schema, s3Client, db, config, nameTransformer, sqlOperations, configuredStream);
  }

}
