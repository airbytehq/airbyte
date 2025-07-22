/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.skeleton_directload.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import jakarta.inject.Singleton

data class SkeletonDirectLoadConfiguration(val internalNamespace: String) : DestinationConfiguration()

@Singleton
class SkeletonDirectLoadConfigurationFactory :
    DestinationConfigurationFactory<SkeletonDirectLoadSpecification, SkeletonDirectLoadConfiguration> {
    override fun makeWithoutExceptionHandling(pojo: SkeletonDirectLoadSpecification): SkeletonDirectLoadConfiguration {
        return SkeletonDirectLoadConfiguration(
            internalNamespace = pojo.internalNamespace
        )
    }
}
