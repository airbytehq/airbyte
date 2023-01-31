/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.integrations.destination.s3.writer.ProductionWriterFactory;
import io.airbyte.integrations.destination.s3.writer.S3WriterFactory;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.sql.Timestamp;

public class DatabricksStreamCopierFactory implements StreamCopierFactory<DatabricksDestinationConfig> {

  @Override
  public StreamCopier create(final String configuredSchema,
                             final DatabricksDestinationConfig databricksConfig,
                             final String stagingFolder,
                             final ConfiguredAirbyteStream configuredStream,
                             final ExtendedNameTransformer nameTransformer,
                             final JdbcDatabase database,
                             final SqlOperations sqlOperations) {
    try {
      final AirbyteStream stream = configuredStream.getStream();
      final String schema = StreamCopierFactory.getSchema(stream.getNamespace(), configuredSchema, nameTransformer);
      final AmazonS3 s3Client = databricksConfig.getS3DestinationConfig().getS3Client();
      final S3WriterFactory writerFactory = new ProductionWriterFactory();
      final Timestamp uploadTimestamp = new Timestamp(System.currentTimeMillis());

      return new DatabricksStreamCopier(stagingFolder, schema, configuredStream, s3Client, database,
          databricksConfig, nameTransformer, sqlOperations, writerFactory, uploadTimestamp);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }

  }

}
