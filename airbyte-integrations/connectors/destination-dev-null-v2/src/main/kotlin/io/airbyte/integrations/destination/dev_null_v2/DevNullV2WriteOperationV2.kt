/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_v2

import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.dataflow.DestinationLifecycle
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Primary
@Singleton
@Requires(property = Operation.PROPERTY, value = "write")
class DevNullV2WriteOperationV2(
    private val destinationLifecycle: DestinationLifecycle,
) : Operation {
    private val log = KotlinLogging.logger {}

    override fun execute() {
        log.info { "Starting dev-null write operation..." }
        destinationLifecycle.run()
        log.info { "Dev-null write operation complete (all data discarded successfully)" }
    }
}
