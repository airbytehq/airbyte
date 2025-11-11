/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.output

import io.airbyte.protocol.models.v0.AirbyteLogMessage
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton

/**
 * [CatalogValidationFailureHandler] implementation for integrations tests. Delegates log messages
 * to [OutputConsumer]
 */
@Singleton
@Requires(env = [Environment.CLI])
@Replaces(CatalogValidationFailureHandler::class)
class DelegatingCatalogValidationFailureHandler(
    val outputConsumer: OutputConsumer,
) : CatalogValidationFailureHandler {
    override fun accept(f: CatalogValidationFailure) {
        outputConsumer.accept(
            AirbyteLogMessage().withLevel(AirbyteLogMessage.Level.WARN).withMessage(f.toString()),
        )
    }
}
