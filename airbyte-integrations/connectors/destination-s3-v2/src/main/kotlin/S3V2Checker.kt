/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.s3.S3Client
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking

@Singleton
class S3V2Checker(
    private val s3Client: S3Client,
    private val pathFactory: ObjectStoragePathFactory
) : DestinationChecker<S3V2Configuration> {
    private val log = KotlinLogging.logger {}

    override fun check(config: S3V2Configuration) {
        runBlocking {
            val path = pathFactory.getStagingDirectory(mockStream())
            val key = path.resolve("_EMPTY").toString()
            log.info { "Checking if destination can write to $path" }
            try {
                s3Client.put(key, byteArrayOf())
                val results = s3Client.list(path.toString()).toList()
                if (results.isEmpty() || results.find { it.key == key } == null) {
                    throw IllegalStateException("Failed to write to S3 bucket")
                }
                log.info { "Successfully wrote: $results" }
            } finally {
                s3Client.delete(key)
                s3Client.list(path.toString()).toList()
            }
        }
    }
}
