/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import jakarta.inject.Singleton

@Singleton
class PostgresWriter : DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        throw NotImplementedError("PostgresWriter.createStreamLoader not yet implemented")
    }
}