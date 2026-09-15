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
 * Connection checker: uploads a small probe file via [GcsV2ClientFactory], verifies it can be
 * listed, then deletes it. Builds the client from the config directly (not via DI) per the
 * [DestinationChecker] contract.
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
