/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc.copy.azure

import com.azure.storage.blob.specialized.SpecializedBlobClientBuilder
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperations
import io.airbyte.cdk.integrations.destination.jdbc.copy.StreamCopier
import io.airbyte.cdk.integrations.destination.jdbc.copy.StreamCopierFactory
import io.airbyte.cdk.integrations.destination.jdbc.copy.StreamCopierFactory.Companion.getSchema
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode

abstract class AzureBlobStorageStreamCopierFactory : StreamCopierFactory<AzureBlobStorageConfig> {
    override fun create(
        configuredSchema: String?,
        config: AzureBlobStorageConfig,
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
            val streamName = stream.name

            val specializedBlobClientBuilder =
                SpecializedBlobClientBuilder()
                    .endpoint(config.endpointUrl)
                    .sasToken(config.sasToken)
                    .containerName(config.containerName)

            return create(
                stagingFolder,
                syncMode,
                schema,
                streamName,
                specializedBlobClientBuilder,
                db,
                config,
                nameTransformer,
                sqlOperations
            )
        } catch (e: Exception) {
            throw RuntimeException(e)
        }
    }

    @Throws(Exception::class)
    abstract fun create(
        stagingFolder: String?,
        syncMode: DestinationSyncMode?,
        schema: String?,
        streamName: String?,
        specializedBlobClientBuilder: SpecializedBlobClientBuilder?,
        db: JdbcDatabase?,
        azureBlobConfig: AzureBlobStorageConfig?,
        nameTransformer: StandardNameTransformer?,
        sqlOperations: SqlOperations?
    ): StreamCopier
}
