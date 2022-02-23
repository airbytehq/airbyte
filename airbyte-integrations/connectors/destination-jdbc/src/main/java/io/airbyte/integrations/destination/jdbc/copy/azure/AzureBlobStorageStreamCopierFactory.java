/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.azure;

import com.azure.storage.blob.specialized.AppendBlobClient;
import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder;
import com.azure.storage.common.StorageSharedKeyCredential;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;

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
//      AppendBlobClient appendBlobClient = AzureBlobStorageStreamCopier.getAppendBlobClient(azureBlobConfig, streamName);
      // Init the client itself here
//      StorageSharedKeyCredential credential = new StorageSharedKeyCredential(
//          azureBlobConfig.getAccountName(),
//          azureBlobConfig.getAccountKey()
//      );

      AppendBlobClient appendBlobClient = new SpecializedBlobClientBuilder()
          .endpoint(azureBlobConfig.getEndpointUrl())
          .sasToken(azureBlobConfig.getSasToken())
//          .credential(credential)
          .containerName(azureBlobConfig.getContainerName())
          .blobName(streamName)
          .buildAppendBlobClient();

      appendBlobClient.create(true); // overwrite if exists
      return create(stagingFolder, syncMode, schema, streamName, appendBlobClient, db, azureBlobConfig, nameTransformer, sqlOperations);
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
      AppendBlobClient appendBlobClient,
      JdbcDatabase db,
      AzureBlobStorageConfig azureBlobConfig,
      ExtendedNameTransformer nameTransformer,
      SqlOperations sqlOperations)
      throws Exception;

}

