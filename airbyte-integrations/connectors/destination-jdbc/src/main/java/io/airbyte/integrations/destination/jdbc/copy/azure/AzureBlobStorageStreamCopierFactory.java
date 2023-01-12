/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.azure;

import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;

public abstract class AzureBlobStorageStreamCopierFactory implements StreamCopierFactory<AzureBlobStorageConfig> {

  @Override
  public StreamCopier create(String configuredSchema,
                             AzureBlobStorageConfig azureBlobConfig,
                             String stagingFolder,
                             ConfiguredAirbyteStream configuredStream,
                             ExtendedNameTransformer nameTransformer,
                             JdbcDatabase db,
                             SqlOperations sqlOperations) {
    try {
      AirbyteStream stream = configuredStream.getStream();
      DestinationSyncMode syncMode = configuredStream.getDestinationSyncMode();
      String schema = StreamCopierFactory.getSchema(stream.getNamespace(), configuredSchema, nameTransformer);
      String streamName = stream.getName();

      final SpecializedBlobClientBuilder specializedBlobClientBuilder = new SpecializedBlobClientBuilder()
          .endpoint(azureBlobConfig.getEndpointUrl())
          .sasToken(azureBlobConfig.getSasToken())
          .containerName(azureBlobConfig.getContainerName());

      return create(stagingFolder, syncMode, schema, streamName, specializedBlobClientBuilder, db, azureBlobConfig, nameTransformer, sqlOperations);
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  public abstract StreamCopier create(String stagingFolder,
                                      DestinationSyncMode syncMode,
                                      String schema,
                                      String streamName,
                                      SpecializedBlobClientBuilder specializedBlobClientBuilder,
                                      JdbcDatabase db,
                                      AzureBlobStorageConfig azureBlobConfig,
                                      ExtendedNameTransformer nameTransformer,
                                      SqlOperations sqlOperations)
      throws Exception;

}
