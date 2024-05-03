/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.stream

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.consumers.OutputConsumer
import io.airbyte.cdk.read.CdcInitialSyncCompleted
import io.airbyte.cdk.read.CdcInitialSyncNotStarted
import io.airbyte.cdk.read.CursorBasedIncrementalCompleted
import io.airbyte.cdk.read.CursorBasedIncrementalStarting
import io.airbyte.cdk.read.CursorBasedInitialSyncEmptyCompleted
import io.airbyte.cdk.read.CursorBasedNotStarted
import io.airbyte.cdk.read.FullRefreshCompleted
import io.airbyte.cdk.read.FullRefreshNotStarted
import io.airbyte.cdk.read.NonResumableBackfillState
import io.airbyte.cdk.read.ResumableSelectState
import io.airbyte.cdk.read.StreamKey
import io.airbyte.cdk.read.StreamState
import io.airbyte.cdk.read.Worker
import jakarta.inject.Singleton

@Singleton
class DefaultStreamWorkerFactory(
    val config: SourceConfiguration,
    val queryBuilder: SelectQueryGenerator,
    val querier: SelectQuerier,
    val outputConsumer: OutputConsumer,
) : StreamWorkerFactory {

    override fun make(input: StreamState): Worker<StreamKey, out StreamState>? =
        when (input) {
            is FullRefreshNotStarted -> FullRefreshPrepWorker(config, input)
            is FullRefreshCompleted -> null
            is CursorBasedNotStarted ->
                CursorBasedColdStartWorker(config, queryBuilder, querier, input)
            is CursorBasedInitialSyncEmptyCompleted -> null
            is CursorBasedIncrementalStarting ->
                CursorBasedWarmStartWorker(config, queryBuilder, querier, input)
            is CursorBasedIncrementalCompleted -> null
            is CdcInitialSyncNotStarted -> CdcInitialSyncPrepWorker(config, input)
            is CdcInitialSyncCompleted -> null
            is NonResumableBackfillState ->
                NonResumableBackfillWorker(queryBuilder, querier, outputConsumer, input)
            is ResumableSelectState ->
                ResumableSelectWorker(queryBuilder, querier, outputConsumer, input)
        }
}
