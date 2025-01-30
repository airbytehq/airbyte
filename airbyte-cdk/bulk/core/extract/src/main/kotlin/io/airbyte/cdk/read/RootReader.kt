/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.discover.MetaFieldDecorator
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.util.ThreadRenamingCoroutineName
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
import java.util.concurrent.ConcurrentHashMap
import kotlin.coroutines.CoroutineContext
import kotlin.time.toKotlinDuration
import kotlinx.coroutines.CoroutineExceptionHandler
import kotlinx.coroutines.Job
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
@SuppressFBWarnings(value = ["NP_NONNULL_PARAM_VIOLATION"], justification = "Kotlin coroutines")
class RootReader(
    val stateManager: StateManager,
    val resourceAcquisitionHeartbeat: Duration,
    val timeout: Duration,
    val outputConsumer: OutputConsumer,
    val metaFieldDecorator: MetaFieldDecorator,
    val partitionsCreatorFactories: List<PartitionsCreatorFactory>,
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

    val streamStatusManager = StreamStatusManager(stateManager.feeds, outputConsumer::accept)

    /** Reads records from all [Feed]s. */
    suspend fun read(listener: suspend (Collection<Job>) -> Unit = {}) {
        readFeeds<Global>(listener)
        readFeeds<Stream>(listener)
    }

    private suspend inline fun <reified T : Feed> readFeeds(
        crossinline listener: suspend (Collection<Job>) -> Unit,
    ) {
        val feeds: List<T> = stateManager.feeds.filterIsInstance<T>()
        log.info { "Reading feeds of type ${T::class}: $feeds." }
        val exceptions = ConcurrentHashMap<T, Throwable>()
        supervisorScope {
            // Launch one coroutine per feed of same type.
            val feedJobs: List<Job> =
                feeds.map { feed: T ->
                    val coroutineName = ThreadRenamingCoroutineName(feed.label)
                    val handler = FeedExceptionHandler(feed, streamStatusManager, exceptions)
                    launch(coroutineName + handler) { FeedReader(this@RootReader, feed).read() }
                }
            // Call listener hook.
            listener(feedJobs)
            // Close the supervisorScope to join on all feeds.
        }
        // Reduce and throw any caught exceptions.
        if (exceptions.isNotEmpty()) {
            throw feeds
                .mapNotNull { exceptions[it] }
                .reduce { acc: Throwable, exception: Throwable ->
                    acc.addSuppressed(exception)
                    acc
                }
        }
    }

    class FeedExceptionHandler<T : Feed>(
        val feed: T,
        val streamStatusManager: StreamStatusManager,
        private val exceptions: ConcurrentHashMap<T, Throwable>,
    ) : CoroutineExceptionHandler {
        private val log = KotlinLogging.logger {}

        override val key: CoroutineContext.Key<CoroutineExceptionHandler>
            get() = CoroutineExceptionHandler.Key

        override fun handleException(
            context: CoroutineContext,
            exception: Throwable,
        ) {
            log.warn(exception) { "canceled feed '${feed.label}' due to thrown exception" }
            streamStatusManager.notifyFailure(feed)
            exceptions[feed] = exception
        }

        override fun toString(): String = "FeedExceptionHandler(${feed.label})"
    }
}
