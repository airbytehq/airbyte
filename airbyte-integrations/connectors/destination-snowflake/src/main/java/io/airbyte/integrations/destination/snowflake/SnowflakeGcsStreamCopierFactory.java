/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.google.cloud.storage.Storage;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsConfig;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsStreamCopierFactory;
import io.airbyte.protocol.models.DestinationSyncMode;

public class SnowflakeGcsStreamCopierFactory extends GcsStreamCopierFactory {

  @Override
  public StreamCopier create(String stagingFolder,
                             DestinationSyncMode syncMode,
                             String schema,
                             String streamName,
                             Storage storageClient,
                             JdbcDatabase db,
                             GcsConfig gcsConfig,
                             ExtendedNameTransformer nameTransformer,
                             SqlOperations sqlOperations)
      throws Exception {
    return new SnowflakeGcsStreamCopier(
        stagingFolder,
        syncMode,
        schema,
        streamName,
        storageClient,
        db,
        gcsConfig,
        nameTransformer,
        sqlOperations);
  }

}
