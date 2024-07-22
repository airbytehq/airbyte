/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.s3

import io.airbyte.cdk.integrations.base.adaptive.AdaptiveDestinationRunner.baseOnEnv

object S3DestinationRunner {
    @Throws(Exception::class)
    @JvmStatic
    fun main(args: Array<String>) {
        baseOnEnv()
            .withOssDestination { S3Destination() }
            .withCloudDestination { S3DestinationStrictEncrypt() }
            .run(args)
    }
}
