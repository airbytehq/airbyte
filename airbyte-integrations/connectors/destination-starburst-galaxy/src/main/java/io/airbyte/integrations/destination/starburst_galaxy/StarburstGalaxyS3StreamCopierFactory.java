/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory.getSchema;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.Timestamp;

public class StarburstGalaxyS3StreamCopierFactory
    implements StarburstGalaxyStreamCopierFactory {

  @Override
  public StreamCopier create(final String configuredSchema,
                             final StarburstGalaxyDestinationConfig starburstGalaxyConfig,
                             final String stagingFolder,
                             final ConfiguredAirbyteStream configuredStream,
                             final StandardNameTransformer nameTransformer,
                             final JdbcDatabase database,
                             final SqlOperations sqlOperations) {
    try {
      final AirbyteStream stream = configuredStream.getStream();
      final String schema = getSchema(stream.getNamespace(), configuredSchema, nameTransformer);

      S3DestinationConfig s3Config = starburstGalaxyConfig.storageConfig().getS3DestinationConfigOrThrow();
      final AmazonS3 s3Client = s3Config.getS3Client();
      final Timestamp uploadTimestamp = new Timestamp(System.currentTimeMillis());
      return new StarburstGalaxyS3StreamCopier(stagingFolder, schema, configuredStream, s3Client, database,
          starburstGalaxyConfig, nameTransformer, sqlOperations, uploadTimestamp);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

}
