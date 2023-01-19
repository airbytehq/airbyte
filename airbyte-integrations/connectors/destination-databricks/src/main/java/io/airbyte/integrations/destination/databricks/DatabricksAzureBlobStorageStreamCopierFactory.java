/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.integrations.destination.jdbc.copy.azure.AzureBlobStorageConfig;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;

public class DatabricksAzureBlobStorageStreamCopierFactory implements DatabricksStreamCopierFactory {

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

      final AzureBlobStorageConfig azureConfig = databricksConfig.getStorageConfig().getAzureBlobStorageConfigOrThrow();
      final SpecializedBlobClientBuilder specializedBlobClientBuilder = new SpecializedBlobClientBuilder()
          .endpoint(azureConfig.getEndpointUrl())
          .sasToken(azureConfig.getSasToken())
          .containerName(azureConfig.getContainerName());
      return new DatabricksAzureBlobStorageStreamCopier(stagingFolder, schema, configuredStream, database,
          databricksConfig, nameTransformer, sqlOperations, specializedBlobClientBuilder, azureConfig);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

}
