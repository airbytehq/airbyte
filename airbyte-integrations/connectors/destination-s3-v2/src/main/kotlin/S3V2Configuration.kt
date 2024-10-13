/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

data object S3V2Configuration : DestinationConfiguration()

@Singleton
class S3V2ConfigurationFactory :
    DestinationConfigurationFactory<S3V2Specification, S3V2Configuration> {
    override fun makeWithoutExceptionHandling(pojo: S3V2Specification): S3V2Configuration {
        return S3V2Configuration
    }
}

@Factory
class S3V2ConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): S3V2Configuration {
        return config as S3V2Configuration
    }
}
