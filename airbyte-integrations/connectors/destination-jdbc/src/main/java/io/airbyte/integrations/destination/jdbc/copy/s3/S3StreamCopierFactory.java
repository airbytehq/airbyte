/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.s3;

import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopierFactory.Config;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;

public abstract class S3StreamCopierFactory implements StreamCopierFactory<Config> {

  /**
   * Used by the copy consumer.
   */
  @Override
  public StreamCopier create(final String configuredSchema,
                             final Config config,
                             final String stagingFolder,
                             final ConfiguredAirbyteStream configuredStream,
                             final ExtendedNameTransformer nameTransformer,
                             final JdbcDatabase db,
                             final SqlOperations sqlOperations) {
    try {
      final AirbyteStream stream = configuredStream.getStream();
      final String schema = StreamCopierFactory.getSchema(stream.getNamespace(), configuredSchema, nameTransformer);
      final AmazonS3 s3Client = config.s3Config.getS3Client();

      return create(stagingFolder, schema, s3Client, db, config, nameTransformer, sqlOperations, configuredStream);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * For specific copier suppliers to implement.
   */
  protected abstract StreamCopier create(String stagingFolder,
                                         String schema,
                                         AmazonS3 s3Client,
                                         JdbcDatabase db,
                                         Config config,
                                         ExtendedNameTransformer nameTransformer,
                                         SqlOperations sqlOperations,
                                         ConfiguredAirbyteStream configuredStream)
      throws Exception;

  /**
   * S3 copy destinations need an S3DestinationConfig to configure the basic upload behavior. We also
   * want additional flags to configure behavior that only applies to the copy-to-S3 +
   * load-into-warehouse portion. Currently this is just purgeStagingData, but this may expand.
   */
  public record Config(boolean purgeStagingData, S3DestinationConfig s3Config) {

    public static boolean shouldPurgeStagingData(final JsonNode config) {
      if (config.get("purge_staging_data") == null) {
        return true;
      } else {
        return config.get("purge_staging_data").asBoolean();
      }
    }

  }

}
