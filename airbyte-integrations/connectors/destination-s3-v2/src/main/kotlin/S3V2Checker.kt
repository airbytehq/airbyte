/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.check.DestinationChecker
import jakarta.inject.Singleton

@Singleton
class S3V2Checker : DestinationChecker<S3V2Configuration> {
    override fun check(config: S3V2Configuration) {
        // TODO: validate that the configuration works
    }
}
