/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.operation.executor

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Named("discoverOperationExecutor")
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "discover",
)
@Requires(env = ["source"])
class DefaultDiscoverOperationExecutor : OperationExecutor {
    override fun execute(): Result<AirbyteMessage?> {
        return Result.success(AirbyteMessage().withType(AirbyteMessage.Type.CATALOG).withCatalog(AirbyteCatalog()))
    }
}
