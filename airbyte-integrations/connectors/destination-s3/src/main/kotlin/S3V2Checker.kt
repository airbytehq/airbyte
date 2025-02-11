/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.aws.AwsAssumeRoleCredentials
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.s3.S3ClientFactory
import io.airbyte.cdk.load.file.s3.S3Object
import io.airbyte.cdk.load.util.write
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.io.OutputStream
import java.nio.file.Paths
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking

@Singleton
class S3V2Checker<T : OutputStream>(
    private val timeProvider: TimeProvider,
    private val assumeRoleCredentials: AwsAssumeRoleCredentials?,
) : DestinationChecker<S3V2Configuration<T>> {
    private val log = KotlinLogging.logger {}

    override fun check(config: S3V2Configuration<T>) {
        runBlocking {
            val s3Client = S3ClientFactory.make(config, assumeRoleCredentials)
            val pathFactory = ObjectStoragePathFactory.from(config, timeProvider)
            val path =
                if (pathFactory.supportsStaging) {
                    pathFactory.getStagingDirectory(mockStream())
                } else {
                    pathFactory.getFinalDirectory(mockStream())
                }
            val key = Paths.get(path, "_EXAMPLE").toString()
            log.info { "Checking if destination can write to $path" }
            var s3Object: S3Object? = null
            val compressor = config.objectStorageCompressionConfiguration.compressor
            try {
                val upload = s3Client.startStreamingUpload(key)
                val byteStream = ByteArrayOutputStream()
                compressor.wrapper(byteStream).use { it.write("""{"data": 1}""") }
                upload.uploadPart(byteStream.toByteArray(), 1)
                s3Object = upload.complete()
                val results = s3Client.list(path).toList()
                if (results.isEmpty() || results.find { it.key == key } == null) {
                    throw IllegalStateException("Failed to write to S3 bucket")
                }
                log.info { "Successfully wrote test file: $results" }
            } finally {
                s3Object?.also { s3Client.delete(it) }
                log.info { "Successfully removed test file" }
            }
        }
    }
}
