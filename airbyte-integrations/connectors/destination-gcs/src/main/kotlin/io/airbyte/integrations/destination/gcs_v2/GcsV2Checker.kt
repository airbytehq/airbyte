/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.file.gcs.GcsBlob
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.util.write
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.io.OutputStream
import java.nio.file.Paths
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking

/**
 * Mirror of S3V2Checker. Follows the [DestinationChecker] contract "do not inject configuration;
 * only use the config passed to check" by BUILDING the client from the config in-method — exactly
 * as S3V2Checker does via S3ClientFactory.make(config, ...).
 *
 * The client is built through the connector-local [GcsV2ClientFactory] (which wraps the CDK's
 * S3ClientFactory for the GCS S3-interop endpoint); the DI-scoped GcsClient bean is intentionally
 * NOT used here, per the checker contract.
 *
 * Behavior mirrors S3: streaming-upload a compressed {"data":1} probe under the resolved final
 * directory, list to confirm, delete in `finally`. Replaces v0.4.x's separate single + multipart
 * upload probe with the same real multipart round-trip destination-s3 uses.
 */
@Singleton
class GcsV2Checker<T : OutputStream>(
    private val timeProvider: TimeProvider,
) : DestinationChecker<GcsV2Configuration<T>> {
    private val log = KotlinLogging.logger {}

    override fun check(config: GcsV2Configuration<T>) {
        runBlocking {
            val gcsClient = GcsV2ClientFactory.make(config.gcsClientConfiguration)
            val pathFactory = ObjectStoragePathFactory.from(config, timeProvider)
            val path = pathFactory.getFinalDirectory(mockStream())
            val key = Paths.get(path, "_EXAMPLE").toString()
            log.info { "Checking if destination can write to $path" }
            var gcsObject: GcsBlob? = null
            val compressor = config.objectStorageCompressionConfiguration.compressor
            try {
                val upload = gcsClient.startStreamingUpload(key)
                val byteStream = ByteArrayOutputStream()
                compressor.wrapper(byteStream).use { it.write("""{"data": 1}""") }
                upload.uploadPart(byteStream.toByteArray(), 1)
                gcsObject = upload.complete()
                val results = gcsClient.list(path).toList()
                if (results.isEmpty() || results.find { it.key == key } == null) {
                    throw IllegalStateException("Failed to write to GCS bucket")
                }
                log.info { "Successfully wrote test file: $results" }
            } finally {
                gcsObject?.also { gcsClient.delete(it) }
                log.info { "Successfully removed test file" }
            }
        }
    }
}
