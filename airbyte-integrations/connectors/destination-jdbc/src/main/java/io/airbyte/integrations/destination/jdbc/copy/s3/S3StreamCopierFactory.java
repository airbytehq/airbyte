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
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;

public abstract class S3StreamCopierFactory implements StreamCopierFactory<S3Config> {

  /**
   * Used by the copy consumer.
   */
  @Override
  public StreamCopier create(String configuredSchema,
                             S3Config s3Config,
                             String stagingFolder,
                             ConfiguredAirbyteStream configuredStream,
                             ExtendedNameTransformer nameTransformer,
                             JdbcDatabase db,
                             SqlOperations sqlOperations) {
    try {
      AirbyteStream stream = configuredStream.getStream();
      DestinationSyncMode syncMode = configuredStream.getDestinationSyncMode();
      String schema = StreamCopierFactory.getSchema(stream.getNamespace(), configuredSchema, nameTransformer);
      AmazonS3 s3Client = S3StreamCopier.getAmazonS3(s3Config);

      return create(stagingFolder, syncMode, schema, stream.getName(), s3Client, db, s3Config, nameTransformer, sqlOperations);
    } catch (Exception e) {
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
                                      S3Config s3Config,
                                      ExtendedNameTransformer nameTransformer,
                                      SqlOperations sqlOperations)
      throws Exception;

}
