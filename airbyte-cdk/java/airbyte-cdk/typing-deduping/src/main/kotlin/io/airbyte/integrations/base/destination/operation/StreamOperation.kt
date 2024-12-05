/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.operation

import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import java.util.stream.Stream

/** Operations on individual streams. */
interface StreamOperation<T> {

    val updatedDestinationState: T

    fun writeRecords(streamConfig: StreamConfig, stream: Stream<PartialAirbyteMessage>)

    fun finalizeTable(streamConfig: StreamConfig, syncSummary: StreamSyncSummary)
}
