/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.cdk.load.file.s3.S3Object
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.write.db.BulkLoader
import io.airbyte.cdk.load.write.db.BulkLoaderFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

class BigQueryBulkLoader : BulkLoader<S3Object> {
    private val log = KotlinLogging.logger {}

    override suspend fun load(remoteObject: S3Object) {}

    override fun close() {
        /* Do nothing */
    }
}

@Singleton
class BigQueryBulkLoaderFactory() : BulkLoaderFactory<StreamKey, S3Object> {
    override val maxNumConcurrentLoads: Int = 1
    override fun create(key: StreamKey, partition: Int): BulkLoader<S3Object> {
        return BigQueryBulkLoader()
    }
}
