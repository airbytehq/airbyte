/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.source.relationaldb.state

import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream

class SourceStateIteratorForTest<T>(
    messageIterator: Iterator<T>,
    stream: ConfiguredAirbyteStream?,
    sourceStateMessageProducer: SourceStateMessageProducer<T>,
    stateEmitFrequency: StateEmitFrequency
) :
    SourceStateIterator<T>(
        messageIterator,
        stream,
        sourceStateMessageProducer,
        stateEmitFrequency
    ) {
    public override fun computeNext(): AirbyteMessage? = super.computeNext()
}
