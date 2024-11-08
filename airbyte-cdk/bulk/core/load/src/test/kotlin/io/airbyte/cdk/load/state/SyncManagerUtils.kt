/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import com.google.common.collect.Range
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.SimpleBatch

/**
 * Because [SyncManager] and [StreamManager] have thin interfaces with no side effects, mocking them
 * is overkill (the mock implementation converges with the real one). Instead, we provide
 * convenience extension functions to simplify mocking state for testing.
 *
 * TODO: add more of these and apply them throughout the tests to simplify the code.
 */
fun SyncManager.markPersisted(stream: DestinationStream, range: Range<Long>) {
    this.getStreamManager(stream.descriptor)
        .updateBatchState(BatchEnvelope(SimpleBatch(Batch.State.PERSISTED), range))
}
