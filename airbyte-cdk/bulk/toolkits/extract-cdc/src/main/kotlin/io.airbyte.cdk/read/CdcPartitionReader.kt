/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.cdc

import com.fasterxml.jackson.databind.node.NullNode
import io.airbyte.cdk.read.CdcAware
import io.airbyte.cdk.read.CdcSharedState
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionReader.TryAcquireResourcesStatus
import io.airbyte.cdk.read.PartitionReader.TryAcquireResourcesStatus.*
import io.airbyte.cdk.read.cdcResourceTaker
import io.debezium.engine.ChangeEvent
import io.debezium.engine.DebeziumEngine
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.delay

class CdcPartitionReader<S : CdcSharedState>(
    val sharedState: S
) : PartitionReader, CdcAware, cdcResourceTaker {

    private val log = KotlinLogging.logger {}
    private var engine: DebeziumEngine<ChangeEvent<String?, String?>>? = null
    private val acquiredResources = AtomicReference<AcquiredResources>()

    /** Calling [close] releases the resources acquired for the [JdbcPartitionReader]. */
    fun interface AcquiredResources : AutoCloseable

    override fun tryAcquireResources(): TryAcquireResourcesStatus {
        if (!cdcReadyToRun()) {
            return RETRY_LATER
        }

        val acquiredResources: AcquiredResources =
            sharedState.tryAcquireResourcesForReader() ?: return RETRY_LATER
        this.acquiredResources.set(acquiredResources)
        return READY_TO_RUN
    }

    override suspend fun run() {
        delay(5000)
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        return PartitionReadCheckpoint(NullNode.instance, 0)
    }

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.close()
        cdcRunEnded()
        // Release global CDC lock
    }

    enum class DebeziumCloseReason() {
        TIMEOUT,
        ITERATOR_CLOSE,
        HEARTBEAT_REACHED_TARGET_POSITION,
        CHANGE_EVENT_REACHED_TARGET_POSITION,
        HEARTBEAT_NOT_PROGRESSING
    }

    private fun requestClose(closeLogMessage: String, closeReason: DebeziumCloseReason) {
        log.info { closeLogMessage }
        log.info { closeReason }
        // TODO : send close analytics message
        // TODO : Close the engine. Note that engine must be closed in a different thread
        // than the running engine.
        // launch { engine?.close() }
    }
}
