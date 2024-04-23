/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc.copy.gcs

import com.google.auth.oauth2.GoogleCredentials
import com.google.cloud.storage.Storage
import com.google.cloud.storage.StorageOptions
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperations
import io.airbyte.cdk.integrations.destination.jdbc.copy.StreamCopier
import io.airbyte.cdk.integrations.destination.jdbc.copy.StreamCopierFactory
import io.airbyte.cdk.integrations.destination.jdbc.copy.StreamCopierFactory.Companion.getSchema
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import java.io.ByteArrayInputStream
import java.io.InputStream
import java.nio.charset.StandardCharsets

abstract class GcsStreamCopierFactory : StreamCopierFactory<GcsConfig?> {
    /** Used by the copy consumer. */
    fun create(
        configuredSchema: String?,
        gcsConfig: GcsConfig,
        stagingFolder: String?,
        configuredStream: ConfiguredAirbyteStream?,
        nameTransformer: StandardNameTransformer?,
        db: JdbcDatabase?,
        sqlOperations: SqlOperations?
    ): StreamCopier {
        try {
            val stream = configuredStream!!.stream
            val syncMode = configuredStream.destinationSyncMode
            val schema = getSchema(stream.namespace, configuredSchema!!, nameTransformer!!)

            val credentialsInputStream: InputStream =
                ByteArrayInputStream(gcsConfig.credentialsJson.toByteArray(StandardCharsets.UTF_8))
            val credentials = GoogleCredentials.fromStream(credentialsInputStream)
            val storageClient =
                StorageOptions.newBuilder()
                    .setCredentials(credentials)
                    .setProjectId(gcsConfig.projectId)
                    .build()
                    .service

            return create(
                stagingFolder,
                syncMode,
                schema,
                stream.name,
                storageClient,
                db,
                gcsConfig,
                nameTransformer,
                sqlOperations
            )
        } catch (e: Exception) {
            throw RuntimeException(e)
        }
    }

    /** For specific copier suppliers to implement. */
    @Throws(Exception::class)
    abstract fun create(
        stagingFolder: String?,
        syncMode: DestinationSyncMode?,
        schema: String?,
        streamName: String?,
        storageClient: Storage?,
        db: JdbcDatabase?,
        gcsConfig: GcsConfig?,
        nameTransformer: StandardNameTransformer?,
        sqlOperations: SqlOperations?
    ): StreamCopier
}
