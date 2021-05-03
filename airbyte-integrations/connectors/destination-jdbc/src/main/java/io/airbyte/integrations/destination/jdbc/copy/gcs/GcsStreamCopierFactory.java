package io.airbyte.integrations.destination.jdbc.copy.gcs;

import com.amazonaws.services.s3.AmazonS3;
import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopier;
import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3Config;
import io.airbyte.integrations.destination.jdbc.copy.s3.S3StreamCopier;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import org.apache.http.auth.Credentials;

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
                               DestinationSyncMode syncMode,
                               AirbyteStream stream,
                               ExtendedNameTransformer nameTransformer,
                               JdbcDatabase db,
                               SqlOperations sqlOperations) {
        try {
            var pair = AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream);
            var schema = getSchema(stream, configuredSchema, nameTransformer);

            InputStream credentialsInputStream = new ByteArrayInputStream(gcsConfig.getCredentialsJson().getBytes());
            GoogleCredentials credentials = GoogleCredentials.fromStream(credentialsInputStream);
            Storage storageClient = StorageOptions.newBuilder()
                    .setCredentials(credentials)
                    .setProjectId(gcsConfig.getProjectId())
                    .build()
                    .getService();

            return create(stagingFolder, syncMode, schema, pair.getName(), storageClient, db, gcsConfig, nameTransformer, sqlOperations);
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

    private String getSchema(AirbyteStream stream, String configuredSchema, ExtendedNameTransformer nameTransformer) {
        if (stream.getNamespace() != null) {
            return nameTransformer.convertStreamName(stream.getNamespace());
        } else {
            return nameTransformer.convertStreamName(configuredSchema);
        }
    }

}
