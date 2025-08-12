/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.cdk

import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.dataflow.DestinationLifecycle
import io.github.oshai.kotlinlogging.KotlinLogging

// @Primary
// @Singleton
// @Requires(property = Operation.PROPERTY, value = "write")
// @Replaces(WriteOperation::class)
class WriteOperationV2(
    private val d: DestinationLifecycle,
) : Operation {
    private val log = KotlinLogging.logger {}

    override fun execute() {
        log.info { "Running new pipe..." }
        d.run()
        log.info { "New pipe complete :tada:" }
    }
}
