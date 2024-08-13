/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.util.ThreadRenamingCoroutineName
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
import java.util.concurrent.ConcurrentHashMap
import kotlin.coroutines.CoroutineContext
import kotlin.time.toKotlinDuration
import kotlinx.coroutines.CoroutineExceptionHandler
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.supervisorScope
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.withTimeoutOrNull

/**
 * [RootReader] is at the heart of the READ operation. A [RootReader] manages multiple [FeedReader]
 * instances (one per [Feed]) and synchronizes them using coroutines.
 *
 * This object exists mainly to facilitate unit testing by keeping dependencies to a minimum.
 */
class RootReader(
    val stateManager: StateManager,
    val resourceAcquisitionHeartbeat: Duration,
    val timeout: Duration,
    val outputConsumer: OutputConsumer,
    val partitionsCreatorFactory: PartitionsCreatorFactory,
) {
    private val log = KotlinLogging.logger {}

    /** [Mutex] ensuring that resource acquisition always happens serially. */
    val resourceAcquisitionMutex: Mutex = Mutex()

    private val resourceReleaseFlow: MutableStateFlow<Long> = MutableStateFlow(0L)

    /** Notify a potential change in resource availability. */
    fun notifyResourceAvailability() {
        resourceReleaseFlow.update { it + 1 }
    }

    /** Wait until an availability notification arrives or a timeout is reached. */
    suspend fun waitForResourceAvailability() {
        withTimeoutOrNull(resourceAcquisitionHeartbeat.toKotlinDuration()) {
            resourceReleaseFlow.collectLatest {}
        }
    }

    /** Reads records from all [Feed]s. */
    suspend fun read(listener: suspend (Map<Feed, Job>) -> Unit = {}) {
        supervisorScope {
            val feeds: List<Feed> = stateManager.feeds
            val exceptions = ConcurrentHashMap<Feed, Throwable>()
            // Launch one coroutine per feed.
            val feedJobs: Map<Feed, Job> =
                feeds.associateWith { feed: Feed ->
                    val coroutineName = ThreadRenamingCoroutineName(feed.label)
                    val handler = FeedExceptionHandler(feed, exceptions)
                    launch(coroutineName + handler) { FeedReader(this@RootReader, feed).read() }
                }
            // Call listener hook.
            listener(feedJobs)
            // Join on all stream feeds and collect caught exceptions.
            val streamExceptions: Map<Stream, Throwable?> =
                feeds.filterIsInstance<Stream>().associateWith {
                    feedJobs[it]?.join()
                    exceptions[it]
                }
            // Cancel any incomplete global feed job whose stream feed jobs have not all succeeded.
            for ((global, globalJob) in feedJobs) {
                if (global !is Global) continue
                if (globalJob.isCompleted) continue
                val globalStreamExceptions: List<Throwable> =
                    global.streams.mapNotNull { streamExceptions[it] }
                if (globalStreamExceptions.isNotEmpty()) {
                    val cause: Throwable =
                        globalStreamExceptions.reduce { acc: Throwable, exception: Throwable ->
                            acc.addSuppressed(exception)
                            acc
                        }
                    globalJob.cancel("at least one stream did non complete", cause)
                }
            }
            // Join on all global feeds and collect caught exceptions.
            val globalExceptions: Map<Global, Throwable?> =
                feeds.filterIsInstance<Global>().associateWith {
                    feedJobs[it]?.join()
                    exceptions[it]
                }
            // Reduce and throw any caught exceptions.
            val caughtExceptions: List<Throwable> =
                streamExceptions.values.mapNotNull { it } +
                    globalExceptions.values.mapNotNull { it }
            if (caughtExceptions.isNotEmpty()) {
                val cause: Throwable =
                    caughtExceptions.reduce { acc: Throwable, exception: Throwable ->
                        acc.addSuppressed(exception)
                        acc
                    }
                throw cause
            }
        }
    }

    class FeedExceptionHandler(
        val feed: Feed,
        private val exceptions: ConcurrentHashMap<Feed, Throwable>,
    ) : CoroutineExceptionHandler {
        private val log = KotlinLogging.logger {}

        override val key: CoroutineContext.Key<CoroutineExceptionHandler>
            get() = CoroutineExceptionHandler.Key

        override fun handleException(
            context: CoroutineContext,
            exception: Throwable,
        ) {
            log.warn(exception) { "canceled feed '${feed.label}' due to thrown exception" }
            exceptions[feed] = exception
        }

        override fun toString(): String = "FeedExceptionHandler(${feed.label})"
    }
}
