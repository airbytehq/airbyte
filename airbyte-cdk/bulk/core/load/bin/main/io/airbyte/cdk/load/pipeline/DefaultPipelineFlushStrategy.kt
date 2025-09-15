/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton

/**
 * This composes the two built-in flush strategies
 * - if the record-batch-size-override is set, flush every record (ignore the actual value, this is
 * just to make some of our unit tests work)
 * - if the data held in flight > the configured max data age, flush
 *
 * NOTE: If you override this, you must at least provide the microbatch behavior to keep tests from
 * breaking. TODO: make the pipeline inject the microbatching no matter what, so no dev has to think
 * about it.
 *
 * Microbatching means finishing work for every record. We do this in integration tests to guarantee
 * that state gets flushed, so multi-sync tests that test recovery can wait for a state ack before
 * killing the connector. (Otherwise they might hang forever.) We can probably get rid of this if we
 * can better guarantee that all in-flight work is flushed during exception handling:
 * https://github.com/airbytehq/airbyte-internal-issues/issues/12310
 */
@Singleton
class DefaultPipelineFlushStrategy(
    @Value("\${airbyte.destination.core.record-batch-size-override:null}")
    private val microBatchOverride: Long? = null,
    private val config: DestinationConfiguration
) : PipelineFlushStrategy {
    override fun shouldFlush(inputCount: Long, dataAgeMs: Long): Boolean {
        // This shouldn't happen, but if it does, we should definitely not flush.
        if (inputCount == 0L) {
            return false
        }

        // If the legacy batch override is set, assume we're microbatching and force
        // a finish for every row.
        if (microBatchOverride != null) {
            return true
        }

        // Force finishing any data in flight that is older than the configured max timeout
        return dataAgeMs >= config.maxTimeWithoutFlushingDataSeconds * 1000L
    }
}
