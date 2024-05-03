/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.global

import io.airbyte.cdk.command.GlobalStateValue
import io.airbyte.cdk.read.CdcNotStarted
import io.airbyte.cdk.read.CdcOngoing
import io.airbyte.cdk.read.CdcStarting
import io.airbyte.cdk.read.GlobalKey
import io.airbyte.cdk.read.GlobalState
import io.airbyte.cdk.read.WorkResult
import io.airbyte.cdk.read.Worker
import io.airbyte.cdk.read.completed
import io.airbyte.cdk.read.ongoing
import io.airbyte.commons.json.Jsons
import java.util.concurrent.atomic.AtomicBoolean

sealed class CdcWorker<I : GlobalState> : Worker<GlobalKey, I>

class CdcColdStartWorker(override val input: CdcNotStarted) : CdcWorker<CdcNotStarted>() {

    override fun signalStop() {} // unstoppable

    override fun call(): WorkResult<GlobalKey, CdcNotStarted, out GlobalState> {
        /**
         * TODO: determine the actual [GlobalStateValue] at the tail of the WAL. For Debezium this
         * means a real offset state and a real database schema change history. This requires
         * running the Debezium Engine.
         */
        val fakeGlobalStateValue = GlobalStateValue(Jsons.emptyObject())
        return input.completed(fakeGlobalStateValue)
    }
}

class CdcWarmStartWorker(override val input: CdcStarting) : CdcWorker<CdcStarting>() {

    override fun signalStop() {} // unstoppable

    override fun call(): WorkResult<GlobalKey, CdcStarting, out GlobalState> {
        /**
         * TODO: synthesize a [GlobalStateValue] corresponding to the tail of the WAL. For Debezium
         * this means a synthetic offset state.
         */
        val fakeGlobalStateValue = GlobalStateValue(Jsons.emptyObject())
        return input.ongoing(fakeGlobalStateValue)
    }
}

class CdcOngoingWorker(override val input: CdcOngoing) : CdcWorker<CdcOngoing>() {

    val stopping = AtomicBoolean()

    override fun signalStop() {
        stopping.set(true)
    }

    override fun call(): WorkResult<GlobalKey, CdcOngoing, out GlobalState> {
        /**
         * TODO: actually consume the WAL between [input.checkpoint] and [input.target]. For
         * Debezium this requires running the Debezium Engine.
         */
        return input.ongoing(input.checkpoint, 0L)
    }
}
