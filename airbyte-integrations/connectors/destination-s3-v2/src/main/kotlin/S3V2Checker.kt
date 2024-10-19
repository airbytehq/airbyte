/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.object_storage.CSVFormatConfiguration
import io.airbyte.cdk.load.command.object_storage.JsonFormatConfiguration
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.s3.S3ClientFactory
import io.airbyte.cdk.load.file.s3.S3Object
import io.airbyte.cdk.load.util.write
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.exceptions.ConfigurationException
import jakarta.inject.Singleton
import java.io.OutputStream
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking

@Singleton
class S3V2Checker<T : OutputStream>(private val timeProvider: TimeProvider) :
    DestinationChecker<S3V2Configuration<T>> {
    private val log = KotlinLogging.logger {}

    override fun check(config: S3V2Configuration<T>) {
        runBlocking {
            if (
                config.objectStorageFormatConfiguration !is JsonFormatConfiguration &&
                    config.objectStorageFormatConfiguration !is CSVFormatConfiguration
            ) {
                throw ConfigurationException("Currently only JSON and CSV format is supported")
            }
            val s3Client = S3ClientFactory.make(config)
            val pathFactory = ObjectStoragePathFactory.from(config, timeProvider)
            val path = pathFactory.getStagingDirectory(mockStream())
            val key = path.resolve("_EXAMPLE").toString()
            log.info { "Checking if destination can write to $path" }
            var s3Object: S3Object? = null
            val compressor = config.objectStorageCompressionConfiguration.compressor
            try {
                s3Object = s3Client.streamingUpload(key, compressor) { it.write("""{"data": 1}""") }
                val results = s3Client.list(path.toString()).toList()
                if (results.isEmpty() || results.find { it.key == key } == null) {
                    throw IllegalStateException("Failed to write to S3 bucket")
                }
                log.info { "Successfully wrote test file: $results" }
            } finally {
                s3Object?.also { s3Client.delete(it) }
                val results = s3Client.list(path.toString()).toList()
                log.info { "Successfully removed test tile: $results" }
            }
        }
    }
}
