/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import io.airbyte.protocol.models.v0.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.function.Consumer

private val LOGGER = KotlinLogging.logger {}
/**
 * Minimal abstract class intended to handle the case where the destination can commit records every
 * time a state message appears. This class does that commit and then immediately emits the state
 * message. This should only be used in cases when the commit is relatively cheap. immediately.
 */
abstract class CommitOnStateAirbyteMessageConsumer(
    private val outputRecordCollector: Consumer<AirbyteMessage>
) : FailureTrackingAirbyteMessageConsumer(), AirbyteMessageConsumer {
    @Throws(Exception::class)
    override fun accept(message: AirbyteMessage) {
        if (message.type == AirbyteMessage.Type.STATE) {
            commit()
            outputRecordCollector.accept(message)
        }
        super.accept(message)
    }

    @Throws(Exception::class) abstract fun commit()
}
