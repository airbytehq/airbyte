/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import jakarta.inject.Singleton

@Singleton
class DevNullWriter : DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        /* Do nothing. Work is done by the DirectLoader. TODO: Remove StreamLoader entirely. */
        return object : StreamLoader {
            override val stream: DestinationStream = stream
        }
    }
}
