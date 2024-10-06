/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb.state

import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream

/**
 * To be used with SourceStateIterator. SourceStateIterator will iterate over the records and
 * generate state messages when needed. This interface defines how would those state messages be
 * generated, and how the incoming record messages will be processed.
 *
 * @param <T> </T>
 */
interface SourceStateMessageProducer<T> {
    /** Returns a state message that should be emitted at checkpoint. */
    fun generateStateMessageAtCheckpoint(stream: ConfiguredAirbyteStream?): AirbyteStateMessage?

    /** For the incoming record message, this method defines how the connector will consume it. */
    fun processRecordMessage(stream: ConfiguredAirbyteStream?, message: T): AirbyteMessage

    /**
     * At the end of the iteration, this method will be called and it will generate the final state
     * message.
     *
     * @return
     */
    fun createFinalStateMessage(stream: ConfiguredAirbyteStream?): AirbyteStateMessage?

    /**
     * Determines if the iterator has reached checkpoint or not per connector's definition. By
     * default iterator will check if the number of records processed is greater than the checkpoint
     * interval or last state message has already passed syncCheckpointDuration.
     */
    fun shouldEmitStateMessage(stream: ConfiguredAirbyteStream?): Boolean
}
