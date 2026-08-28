/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.integrations.destination.firebolt.client.FireboltAirbyteClient
import io.airbyte.integrations.destination.firebolt.config.FireboltConfiguration
import jakarta.inject.Singleton

/** Top-level orchestrator for Firebolt destination syncs. */
@Singleton
class FireboltWriter(
    private val client: FireboltAirbyteClient,
    private val config: FireboltConfiguration,
) : DestinationWriter {

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return FireboltStreamLoader(stream, client, config)
    }
}
