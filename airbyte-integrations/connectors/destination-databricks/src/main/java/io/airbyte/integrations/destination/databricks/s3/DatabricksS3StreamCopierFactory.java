/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.s3;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.databricks.DatabricksDestinationConfig;
import io.airbyte.integrations.destination.databricks.DatabricksStreamCopierFactory;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.writer.ProductionWriterFactory;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.Timestamp;

public class DatabricksS3StreamCopierFactory implements DatabricksStreamCopierFactory {

  @Override
  public StreamCopier create(final String configuredSchema,
                             final DatabricksDestinationConfig databricksConfig,
                             final String stagingFolder,
                             final ConfiguredAirbyteStream configuredStream,
                             final StandardNameTransformer nameTransformer,
                             final JdbcDatabase database,
                             final SqlOperations sqlOperations) {
    try {
      final AirbyteStream stream = configuredStream.getStream();
      final String catalogName = databricksConfig.catalog();
      final String schema = StreamCopierFactory.getSchema(stream.getNamespace(), configuredSchema, nameTransformer);

      S3DestinationConfig s3Config = databricksConfig.storageConfig().getS3DestinationConfigOrThrow();
      final AmazonS3 s3Client = s3Config.getS3Client();
      final ProductionWriterFactory writerFactory = new ProductionWriterFactory();
      final Timestamp uploadTimestamp = new Timestamp(System.currentTimeMillis());
      return new DatabricksS3StreamCopier(stagingFolder, catalogName, schema, configuredStream, s3Client, database,
          databricksConfig, nameTransformer, sqlOperations, writerFactory, uploadTimestamp);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

}
