/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.command.s3.S3Client
import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.file.TimeProvider
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking

@Singleton
class S3V2Checker(
    private val timeProvider: TimeProvider,
    private val s3Client: S3Client,
) : DestinationChecker<S3V2Configuration> {
    private val log = KotlinLogging.logger {}

    override fun check(config: S3V2Configuration) {
        runBlocking {
            val pathFactory = config.createPathFactory(timeProvider.currentTimeMillis())
            val path = pathFactory.getStagingDirectory(mockStream())
            log.info { "Checking if destination can list objects in $path" }
            s3Client.list(path.toString())
        }
    }
}
