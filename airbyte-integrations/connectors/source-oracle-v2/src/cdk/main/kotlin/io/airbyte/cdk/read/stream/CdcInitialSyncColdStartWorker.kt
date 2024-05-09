package io.airbyte.cdk.read.stream

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.read.*
import io.airbyte.cdk.source.Field

/** Default implementation of [Worker] for [CdcInitialSyncNotStarted]. */
class CdcInitialSyncColdStartWorker(
        val config: SourceConfiguration,
        override val input: CdcInitialSyncNotStarted,
) : Worker<StreamKey, CdcInitialSyncNotStarted> {

    override fun call(): WorkResult<StreamKey, CdcInitialSyncNotStarted, out StreamState> {
        val maybePrimaryKey: List<Field>? =
            key.configuredPrimaryKey ?: key.primaryKeyCandidates.firstOrNull()
        if (maybePrimaryKey != null && config.resumablePreferred) {
            return input.resumable(config.initialLimit, maybePrimaryKey)
        }
        return input.nonResumable()
    }

    override fun signalStop() {} // unstoppable
}
