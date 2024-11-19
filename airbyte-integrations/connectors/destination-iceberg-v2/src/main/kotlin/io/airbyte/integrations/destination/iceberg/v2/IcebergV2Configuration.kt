/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import javax.inject.Singleton

// TODO put real fields here
data class IcebergV2Configuration(val something: String) : DestinationConfiguration()

@Singleton
class IcebergV2ConfigurationFactory :
    DestinationConfigurationFactory<IcebergV2Specification, IcebergV2Configuration> {
    override fun makeWithoutExceptionHandling(
        pojo: IcebergV2Specification
    ): IcebergV2Configuration {
        // TODO convert from the jackson-friendly IcebergV2Specification
        //   to the programmer-friendly IcebergV2Configuration
        return IcebergV2Configuration("hello world")
    }
}
