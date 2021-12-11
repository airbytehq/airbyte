/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.s3;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;

public abstract class S3StreamCopierFactory implements StreamCopierFactory<S3DestinationConfig> {

  /**
   * Used by the copy consumer.
   */
  @Override
  public StreamCopier create(final String configuredSchema,
      final S3DestinationConfig s3Config,
      final String stagingFolder,
      final ConfiguredAirbyteStream configuredStream,
      final ExtendedNameTransformer nameTransformer,
      final JdbcDatabase db,
      final SqlOperations sqlOperations) {
    try {
      final AirbyteStream stream = configuredStream.getStream();
      final DestinationSyncMode syncMode = configuredStream.getDestinationSyncMode();
      final String schema = StreamCopierFactory.getSchema(stream.getNamespace(), configuredSchema, nameTransformer);
      final AmazonS3 s3Client = s3Config.getS3Client();

      return create(stagingFolder, syncMode, schema, stream.getName(), s3Client, db, s3Config, nameTransformer, sqlOperations);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * For specific copier suppliers to implement.
   */
  public abstract StreamCopier create(String stagingFolder,
      DestinationSyncMode syncMode,
      String schema,
      String streamName,
      AmazonS3 s3Client,
      JdbcDatabase db,
      S3DestinationConfig s3Config,
      ExtendedNameTransformer nameTransformer,
      SqlOperations sqlOperations)
      throws Exception;

}
