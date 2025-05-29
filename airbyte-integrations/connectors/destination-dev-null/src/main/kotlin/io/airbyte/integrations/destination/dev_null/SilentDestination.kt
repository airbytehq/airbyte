/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.dev_null

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.BaseConnector
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.util.function.Consumer

/** This destination silently receives records. */
class SilentDestination : BaseConnector(), Destination {
    override fun check(config: JsonNode): AirbyteConnectionStatus {
        return AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
    }

    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer {
        return RecordConsumer(outputRecordCollector)
    }

    class RecordConsumer(private val outputRecordCollector: Consumer<AirbyteMessage>) :
        AirbyteMessageConsumer {
        override fun start() {}

        override fun accept(message: AirbyteMessage) {
            if (message.type == AirbyteMessage.Type.STATE) {
                outputRecordCollector.accept(message)
            }
        }

        override fun close() {}
    }
}
