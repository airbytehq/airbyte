/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.s3

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.destination.s3.BaseS3Destination
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfigFactory
import io.airbyte.cdk.integrations.destination.s3.StorageProvider

open class S3Destination : BaseS3Destination {
    constructor() : super(nThreads = 2, memoryRatio = 0.5)

    @VisibleForTesting
    constructor(
        s3DestinationConfigFactory: S3DestinationConfigFactory,
        env: Map<String, String>
    ) : super(s3DestinationConfigFactory, env)

    override fun storageProvider(): StorageProvider {
        return StorageProvider.AWS_S3
    }

    companion object {
        @Throws(Exception::class)
        @JvmStatic
        fun main(args: Array<String>) {
            IntegrationRunner(S3Destination()).run(args)
        }
    }
}
