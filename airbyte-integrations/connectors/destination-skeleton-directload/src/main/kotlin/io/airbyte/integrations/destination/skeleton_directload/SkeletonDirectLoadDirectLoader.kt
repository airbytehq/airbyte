/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.skeleton_directload

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.airbyte.integrations.destination.skeleton_directload.spec.SkeletonDirectLoadConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

class SkeletonDirectLoadDirectLoader(
    private val config: SkeletonDirectLoadConfiguration,
) : DirectLoader {
    private var recordCount: Long = 0L

    override suspend fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
        return if (++recordCount % 10_000 == 0L) {
            DirectLoader.Complete
        } else {
            DirectLoader.Incomplete
        }
    }

    override suspend fun finish() {
        /* do nothing */
    }

    override fun close() {
        /* do even more nothing */
    }
}

@Singleton
class SkeletonDirectLoadDirectLoaderFactory(private val config: SkeletonDirectLoadConfiguration) :
    DirectLoaderFactory<SkeletonDirectLoadDirectLoader> {
    private val log = KotlinLogging.logger {}

    override fun create(
        streamDescriptor: DestinationStream.Descriptor,
        part: Int
    ): SkeletonDirectLoadDirectLoader {
        return SkeletonDirectLoadDirectLoader(config)
    }
}
