/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.firebolt.client.FireboltAirbyteClient
import io.airbyte.integrations.destination.firebolt.config.FireboltConfiguration

/** Stream loader for the Firebolt destination. This is a stub for the initial skeleton. */
class FireboltStreamLoader(
    override val stream: DestinationStream,
    private val client: FireboltAirbyteClient,
    private val config: FireboltConfiguration,
) : StreamLoader {

    private val prettyName: String = stream.mappedDescriptor.toPrettyString()

    override suspend fun start() {
        println("Starting stream loader for $prettyName")
    }

    override suspend fun teardown(completedSuccessfully: Boolean) {
        println("Tearing down stream loader for $prettyName; success=$completedSuccessfully")
    }
}
