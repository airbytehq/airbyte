/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import jakarta.inject.Singleton

/**
 * Writer for Dev Null 2 destination.
 * Creates stream loaders that do nothing since work is done by DirectLoader.
 */
@Singleton
class DevNull2Writer : DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return object : StreamLoader {
            override val stream: DestinationStream = stream
        }
    }
}
