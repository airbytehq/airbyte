package io.airbyte.integrations.destination.clickhouse_v2

import io.airbyte.cdk.load.file.s3.S3Object
import io.airbyte.cdk.load.write.db.BulkLoader

class ClickhouseBulkLoader(
    // private val clickhouseClient: Client
    // private val recordFormatter = BigQueryRecordFormatter()
    // private val storageClient: S3Client
): BulkLoader<S3Object> {


    override suspend fun load(remoteObject: S3Object) {
        TODO("Not yet implemented")
    }

    override fun close() {
        TODO("Not yet implemented")
    }
}
