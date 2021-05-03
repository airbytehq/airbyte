package io.airbyte.integrations.destination.snowflake;

import com.google.cloud.storage.Storage;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsConfig;
import io.airbyte.integrations.destination.jdbc.copy.gcs.GcsStreamCopierFactory;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3Config;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopierFactory;
import io.airbyte.protocol.models.DestinationSyncMode;

public class SnowflakeGcsStreamCopierFactory extends GcsStreamCopierFactory {
    @Override
    public StreamCopier create(String stagingFolder, DestinationSyncMode syncMode, String schema, String streamName, Storage storageClient, JdbcDatabase db, GcsConfig gcsConfig, ExtendedNameTransformer nameTransformer, SqlOperations sqlOperations) throws Exception {
        return new SnowflakeGcsStreamCopier(
                stagingFolder,
                syncMode,
                schema,
                streamName,
                storageClient,
                db,
                gcsConfig,
                nameTransformer,
                sqlOperations
        );
    }
}
