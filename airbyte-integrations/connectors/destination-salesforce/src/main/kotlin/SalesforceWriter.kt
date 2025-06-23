/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.salesforce

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import jakarta.inject.Singleton

@Singleton
class SalesforceWriter : DestinationWriter {
    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return SalesforceStreamLoader(stream)
    }
}
