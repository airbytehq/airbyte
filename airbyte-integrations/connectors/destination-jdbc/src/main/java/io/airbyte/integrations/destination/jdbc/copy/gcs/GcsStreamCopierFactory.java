/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.copy.gcs;

import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.io.ByteArrayInputStream;
import java.io.InputStream;

public abstract class GcsStreamCopierFactory implements StreamCopierFactory<GcsConfig> {

  /**
   * Used by the copy consumer.
   */
  @Override
  public StreamCopier create(String configuredSchema,
                             GcsConfig gcsConfig,
                             String stagingFolder,
                             ConfiguredAirbyteStream configuredStream,
                             ExtendedNameTransformer nameTransformer,
                             JdbcDatabase db,
                             SqlOperations sqlOperations) {
    try {
      AirbyteStream stream = configuredStream.getStream();
      DestinationSyncMode syncMode = configuredStream.getDestinationSyncMode();
      String schema = StreamCopierFactory.getSchema(stream.getNamespace(), configuredSchema, nameTransformer);

      InputStream credentialsInputStream = new ByteArrayInputStream(gcsConfig.getCredentialsJson().getBytes());
      GoogleCredentials credentials = GoogleCredentials.fromStream(credentialsInputStream);
      Storage storageClient = StorageOptions.newBuilder()
          .setCredentials(credentials)
          .setProjectId(gcsConfig.getProjectId())
          .build()
          .getService();

      return create(stagingFolder, syncMode, schema, stream.getName(), storageClient, db, gcsConfig, nameTransformer, sqlOperations);
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
                                      Storage storageClient,
                                      JdbcDatabase db,
                                      GcsConfig gcsConfig,
                                      ExtendedNameTransformer nameTransformer,
                                      SqlOperations sqlOperations)
      throws Exception;

}
