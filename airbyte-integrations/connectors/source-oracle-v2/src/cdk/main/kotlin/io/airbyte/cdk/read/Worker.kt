/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.cdk.consumers.OutputConsumer
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
import java.util.concurrent.Callable
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.Future
import java.util.concurrent.TimeUnit
import java.util.concurrent.TimeoutException

/**
 * A [Callable] which performs a unit of work in a READ operation.
 *
 * This unit of work is bounded:
 * - by the [key],
 * - by the [input] state which specifies where to begin READing for this [key],
 * - by a soft timeout defined in the connector configuration, when elapsed [signalStop] is called.
 */
interface Worker<S : Key, I : State<S>> : Callable<WorkResult<S, I>> {

    val input: I

    val key: S
        get() = input.key

    fun signalStop()
}

/** The output of a [Worker]. */
data class WorkResult<S : Key, I : State<S>>(
    val input: I,
    val output: State<S>,
    val numRecords: Long = 0L
)

typealias GlobalWorker<T> = Worker<GlobalKey, T>

typealias StreamWorker<T> = Worker<StreamKey, T>

interface WorkerFactory {

    val outputConsumer: OutputConsumer

    fun create(input: CdcNotStarted): GlobalWorker<CdcNotStarted>
    fun create(input: CdcStarting): GlobalWorker<CdcStarting>
    fun create(input: CdcOngoing): GlobalWorker<CdcOngoing>

    fun create(input: CdcInitialSyncNotStarted): StreamWorker<CdcInitialSyncNotStarted>
    fun create(input: CdcInitialSyncStarting): StreamWorker<CdcInitialSyncStarting>
    fun create(input: CdcInitialSyncOngoing): StreamWorker<CdcInitialSyncOngoing>

    fun create(input: FullRefreshNotStarted): StreamWorker<FullRefreshNotStarted>
    fun create(
        input: FullRefreshNonResumableStarting
    ): StreamWorker<FullRefreshNonResumableStarting>
    fun create(input: FullRefreshResumableStarting): StreamWorker<FullRefreshResumableStarting>
    fun create(input: FullRefreshResumableOngoing): StreamWorker<FullRefreshResumableOngoing>

    fun create(input: CursorBasedNotStarted): StreamWorker<CursorBasedNotStarted>
    fun create(input: CursorBasedInitialSyncStarting): StreamWorker<CursorBasedInitialSyncStarting>
    fun create(input: CursorBasedInitialSyncOngoing): StreamWorker<CursorBasedInitialSyncOngoing>
    fun create(input: CursorBasedIncrementalStarting): StreamWorker<CursorBasedIncrementalStarting>
    fun create(input: CursorBasedIncrementalOngoing): StreamWorker<CursorBasedIncrementalOngoing>
}

/** Executes [Worker]s sequentially for a particular [Key]. */
class WorkerThreadRunnable(
    private val factory: WorkerFactory,
    private val workUnitTimeout: Duration,
    private val stateManager: StateManager,
    private var state: State<out Key>,
) : Runnable {

    val name: String =
        "worker-" +
            when (val key = state.key) {
                is GlobalKey -> "global"
                is StreamKey -> key.namePair.toString()
            }

    private val log = KotlinLogging.logger {}

    private val ex: ExecutorService = Executors.newSingleThreadExecutor { Thread(it, name) }

    override fun run() {
        log.info { "$name: new state machine execution" }
        while (true) {
            log.info { "$name: processing state $state" }
            val worker: Worker<*, *> =
                when (val input: State<out Key> = state) {
                    is CdcNotStarted -> factory.create(input)
                    is CdcStarting -> factory.create(input)
                    is CdcOngoing -> factory.create(input)
                    is CdcCompleted -> break
                    is CdcInitialSyncNotStarted -> factory.create(input)
                    is CdcInitialSyncStarting -> factory.create(input)
                    is CdcInitialSyncOngoing -> factory.create(input)
                    is CdcInitialSyncCompleted -> break
                    is FullRefreshNotStarted -> factory.create(input)
                    is FullRefreshNonResumableStarting -> factory.create(input)
                    is FullRefreshResumableStarting -> factory.create(input)
                    is FullRefreshResumableOngoing -> factory.create(input)
                    is FullRefreshCompleted -> break
                    is CursorBasedNotStarted -> factory.create(input)
                    is CursorBasedInitialSyncStarting -> factory.create(input)
                    is CursorBasedInitialSyncOngoing -> factory.create(input)
                    is CursorBasedIncrementalStarting -> factory.create(input)
                    is CursorBasedIncrementalOngoing -> factory.create(input)
                    is CursorBasedIncrementalCompleted -> break
                }
            log.info { "$name: calling ${worker.javaClass.simpleName}" }
            val future: Future<out WorkResult<*, *>> = ex.submit(worker)
            val result: WorkResult<*, *> =
                try {
                    future.get(workUnitTimeout.toMillis(), TimeUnit.MILLISECONDS)
                } catch (_: TimeoutException) {
                    log.info { "$name: ${worker.javaClass.simpleName} soft timeout" }
                    worker.signalStop()
                    future.get()
                }
            log.info { "$name: ${result.numRecords} produced by $worker" }
            state = result.output
            when (result.output) {
                is SerializableGlobalState -> stateManager.set(result.output, result.numRecords)
                is SerializableStreamState -> stateManager.set(result.output, result.numRecords)
                else -> continue
            }
            val checkpoint: List<AirbyteStateMessage> = stateManager.checkpoint()
            log.info { "$name: checkpoint of ${checkpoint.size} state message(s)" }
            checkpoint.forEach(factory.outputConsumer::accept)
        }
        log.info { "$name: reached terminal state $state" }
    }
}
