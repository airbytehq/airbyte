package io.airbyte.cdk.read.stream

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.read.*
import io.airbyte.cdk.source.Field

/** Default implementation of [Worker] for [FullRefreshNotStarted]. */
class FullRefreshColdStartWorker(
        val config: SourceConfiguration,
        override val input: FullRefreshNotStarted,
) : Worker<StreamKey, FullRefreshNotStarted> {

    override fun call(): WorkResult<StreamKey, FullRefreshNotStarted, out StreamState> {
        val maybePrimaryKey: List<Field>? =
            key.configuredPrimaryKey ?: key.primaryKeyCandidates.firstOrNull()
        if (maybePrimaryKey != null && config.resumablePreferred) {
            return input.resumable(config.initialLimit, maybePrimaryKey)
        }
        return input.nonResumable()
    }

    override fun signalStop() {} // unstoppable
}
