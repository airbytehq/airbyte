/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
  public StreamCopier create(String configuredSchema,
                             DatabricksDestinationConfig databricksConfig,
                             String stagingFolder,
                             ConfiguredAirbyteStream configuredStream,
                             ExtendedNameTransformer nameTransformer,
                             JdbcDatabase database,
                             SqlOperations sqlOperations) {
    try {
      AirbyteStream stream = configuredStream.getStream();
      String schema = StreamCopierFactory.getSchema(stream.getNamespace(), configuredSchema, nameTransformer);
      AmazonS3 s3Client = databricksConfig.getS3DestinationConfig().getS3Client();
      S3WriterFactory writerFactory = new ProductionWriterFactory();
      Timestamp uploadTimestamp = new Timestamp(System.currentTimeMillis());

      return new DatabricksStreamCopier(stagingFolder, schema, configuredStream, s3Client, database,
          databricksConfig, nameTransformer, sqlOperations, writerFactory, uploadTimestamp);
    } catch (Exception e) {
      throw new RuntimeException(e);
    }

  }

}
