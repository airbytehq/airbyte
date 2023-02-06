/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.copiers;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3CopyConfig;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopierFactory;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;

/**
 * Very similar to the {@link S3StreamCopierFactory}, but we need some additional
 */
public class RedshiftStreamCopierFactory extends S3StreamCopierFactory {

  @Override
  public StreamCopier create(final String stagingFolder,
                             final String schema,
                             final AmazonS3 s3Client,
                             final JdbcDatabase db,
                             final S3CopyConfig config,
                             final ExtendedNameTransformer nameTransformer,
                             final SqlOperations sqlOperations,
                             final ConfiguredAirbyteStream configuredStream) {
    return new RedshiftStreamCopier(stagingFolder, schema, s3Client, db, config, nameTransformer, sqlOperations, configuredStream);
  }

}
