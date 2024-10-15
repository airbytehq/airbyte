/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.s3.S3Client
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking

@Singleton
class S3V2Checker(private val s3Client: S3Client) : DestinationChecker<S3V2Configuration> {
    override fun check(config: S3V2Configuration) {
        runBlocking { s3Client.list("") }
    }
}
