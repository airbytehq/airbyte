package io.airbyte.integrations.destination.databricks;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3Config;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopier;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetWriter;
import io.airbyte.integrations.destination.s3.writer.ProductionWriterFactory;
import io.airbyte.integrations.destination.s3.writer.S3WriterFactory;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.sql.Timestamp;

public class DatabricksStreamCopierFactory implements StreamCopierFactory<S3Config> {

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
      String schema = StreamCopierFactory.getSchema(stream, configuredSchema, nameTransformer);
      AmazonS3 s3Client = S3StreamCopier.getAmazonS3(s3Config);
      S3WriterFactory writerFactory = new ProductionWriterFactory();
      Timestamp uploadTimestamp = new Timestamp(System.currentTimeMillis());

      return new DatabricksStreamCopier(
          stagingFolder, syncMode, schema, configuredStream, stream.getName(), s3Client, db, s3Config, nameTransformer, sqlOperations, writerFactory, uploadTimestamp);
    } catch (Exception e) {
      throw new RuntimeException(e);
    }

  }

}
