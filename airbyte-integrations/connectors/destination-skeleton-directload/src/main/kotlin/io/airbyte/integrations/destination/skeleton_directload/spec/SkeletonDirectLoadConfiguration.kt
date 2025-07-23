/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.skeleton_directload.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

data class SkeletonDirectLoadConfiguration(val namespace: String) : DestinationConfiguration()

@Singleton
class SkeletonDirectLoadConfigurationFactory :
    DestinationConfigurationFactory<SkeletonDirectLoadSpecification, SkeletonDirectLoadConfiguration> {
    override fun makeWithoutExceptionHandling(pojo: SkeletonDirectLoadSpecification): SkeletonDirectLoadConfiguration {
        return SkeletonDirectLoadConfiguration(
            namespace = pojo.namespace
        )
    }
}


@Singleton
class SkeletonDirectLoadSpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP,
        )
    override val supportsIncremental = true
}
