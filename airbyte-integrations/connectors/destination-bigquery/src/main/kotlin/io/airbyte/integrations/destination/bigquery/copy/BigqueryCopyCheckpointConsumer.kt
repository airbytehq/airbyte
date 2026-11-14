/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.destination.bigquery.copy

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.state.FreeingAnnotatingCheckpointConsumer
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.util.use
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/** Zero-record checkpoints can become ready before the legacy task launcher's setup completes. */
@Singleton
@Primary
@Requires(property = Operation.PROPERTY, value = "write")
@SuppressFBWarnings(
    value = ["NP_NONNULL_PARAM_VIOLATION"],
    justification = "Kotlin coroutine resume stubs pass null placeholders for saved arguments",
)
class BigqueryCopyCheckpointConsumer(
    private val archive: BigqueryS3Copy,
    private val delegate: FreeingAnnotatingCheckpointConsumer,
) : suspend (Reserved<CheckpointMessage>, Long, Long, Long) -> Unit {
    override suspend fun invoke(
        message: Reserved<CheckpointMessage>,
        totalRecords: Long,
        totalBytes: Long,
        totalRejectedRecords: Long,
    ) {
        if (archive.metadataReady()) {
            delegate(message, totalRecords, totalBytes, totalRejectedRecords)
        } else {
            // FailSyncTask also flushes ready state. Release its reservation without acknowledging
            // a refresh whose metadata failed; throwing here would prevent failed-sync teardown.
            message.use {}
        }
    }
}
