/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.command.s3.createS3Client
import io.airbyte.cdk.load.check.DestinationChecker
import jakarta.inject.Singleton
import kotlin.io.path.Path
import kotlinx.coroutines.runBlocking

@Singleton
class S3V2Checker : DestinationChecker<S3V2Configuration> {
    override fun check(config: S3V2Configuration) {
        runBlocking { config.createS3Client().list(Path("/")) }
    }
}
