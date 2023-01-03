/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.google.cloud.storage.Storage;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.StagingFilenameGenerator;
import io.airbyte.integrations.destination.jdbc.constants.GlobalDataSizeConstants;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsConfig;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsStreamCopierFactory;
import io.airbyte.protocol.models.v0.DestinationSyncMode;

public class SnowflakeGcsStreamCopierFactory extends GcsStreamCopierFactory {

  @Override
  public StreamCopier create(final String stagingFolder,
                             final DestinationSyncMode syncMode,
                             final String schema,
                             final String streamName,
                             final Storage storageClient,
                             final JdbcDatabase db,
                             final GcsConfig gcsConfig,
                             final ExtendedNameTransformer nameTransformer,
                             final SqlOperations sqlOperations)
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
        sqlOperations,
        new StagingFilenameGenerator(streamName, GlobalDataSizeConstants.DEFAULT_MAX_BATCH_SIZE_BYTES));
  }

}
