/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.test.util.destination_process.DestinationProcess
import io.airbyte.cdk.load.test.util.destination_process.DestinationProcessFactory
import io.airbyte.cdk.load.test.util.destination_process.NonDockerizedDestinationFactory
import io.airbyte.cdk.load.test.util.destination_process.TestDeploymentMode
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.micronaut.context.annotation.Primary
import javax.inject.Singleton

// The mock destination has no docker equivalent, so we always run non-docker.
@Singleton
@Primary
class ForceNonDockerizedDestinationFactory : DestinationProcessFactory() {
    override fun createDestinationProcess(
        command: String,
        config: ConfigurationSpecification?,
        catalog: ConfiguredAirbyteCatalog?,
        deploymentMode: TestDeploymentMode
    ): DestinationProcess {
        return NonDockerizedDestinationFactory()
            .createDestinationProcess(command, config, catalog, deploymentMode)
    }
}
