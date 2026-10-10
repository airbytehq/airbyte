/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodb

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
import java.util.concurrent.ConcurrentHashMap
import kotlin.random.Random
import kotlinx.coroutines.delay
import software.amazon.awssdk.awscore.exception.AwsServiceException
import software.amazon.awssdk.services.dynamodb.model.ProvisionedThroughputExceededException
import software.amazon.awssdk.services.dynamodb.model.RequestLimitExceededException
import software.amazon.awssdk.services.dynamodb.model.ThrottlingException

private val log = KotlinLogging.logger {}

/**
 * Retries a throttled DynamoDB request until it succeeds, so that a scan slows down to the
 * throughput the table allows instead of failing the sync.
 *
 * DynamoDB throttles a `Scan` when the table's provisioned read capacity, or the maximum read
 * throughput configured for an on-demand table (`OnDemandThroughput.MaxReadRequestUnits`), is
 * exceeded; concurrent parallel-scan segments reach either limit much sooner than one scan. The SDK
 * already retries a throttled request a few times within about a minute; once it gives up, this
 * waits with capped, jittered exponential backoff and sends the same request again (the same
 * `ExclusiveStartKey`), so no item is skipped or read twice.
 *
 * The time a key has spent throttled without a successful request survives the reader that hit it:
 * the CDK cancels a reader at its checkpoint deadline, possibly while it waits here, and the next
 * round's reader of the same segment continues the same budget. Once a key has been throttled for
 * [maxThrottledDuration] without a single success, the last throttling exception is rethrown and
 * classified (`application.yml`).
 */
@SuppressFBWarnings(value = ["NP_NONNULL_PARAM_VIOLATION"], justification = "Kotlin coroutines")
class DynamoDbThrottlingBackoff(
    val initialBackoff: Duration = DEFAULT_INITIAL_BACKOFF,
    val maxBackoff: Duration = DEFAULT_MAX_BACKOFF,
    val maxThrottledDuration: Duration = DEFAULT_MAX_THROTTLED_DURATION,
    private val nanoTime: () -> Long = System::nanoTime,
    private val sleep: suspend (Duration) -> Unit = { delay(it.toMillis()) },
    private val random: Random = Random.Default,
) {
    /** Start of the current run of throttled attempts of each key, in [nanoTime] nanoseconds. */
    private val throttledSince = ConcurrentHashMap<String, Long>()

    /**
     * Runs [request], retrying it while DynamoDB throttles it. [key] identifies what is retried
     * (one table segment) across readers; [label] is for the logs.
     */
    suspend fun <T> call(key: String, label: String, request: () -> T): T {
        var attempt = 0
        while (true) {
            try {
                val result: T = request()
                if (throttledSince.remove(key) != null) {
                    log.info { "DynamoDB stopped throttling the scan of $label." }
                }
                return result
            } catch (e: AwsServiceException) {
                if (!isThrottling(e)) throw e
                val now: Long = nanoTime()
                val since: Long = throttledSince.putIfAbsent(key, now) ?: now
                val throttledFor: Duration = Duration.ofNanos(now - since)
                if (throttledFor >= maxThrottledDuration) {
                    log.warn {
                        "DynamoDB has throttled the scan of $label for $throttledFor without a " +
                            "successful request; giving up."
                    }
                    throw e
                }
                val backoff: Duration = backoff(attempt++)
                log.warn {
                    "DynamoDB throttled the scan of $label (throttled for $throttledFor): " +
                        "${e.awsErrorDetails()?.errorMessage() ?: e.message}; retrying in $backoff."
                }
                sleep(backoff)
            }
        }
    }

    /** Uniform in `[cap / 2, cap]` where `cap = min(maxBackoff, initialBackoff * 2^attempt)`. */
    internal fun backoff(attempt: Int): Duration {
        val capMillis: Long =
            initialBackoff
                .toMillis()
                .shl(attempt.coerceAtMost(MAX_EXPONENT))
                .coerceIn(1L, maxBackoff.toMillis().coerceAtLeast(1L))
        return Duration.ofMillis(random.nextLong(capMillis / 2, capMillis + 1))
    }

    companion object {
        const val DEFAULT_INITIAL_BACKOFF_MILLIS: Long = 1_000L
        val DEFAULT_INITIAL_BACKOFF: Duration = Duration.ofMillis(DEFAULT_INITIAL_BACKOFF_MILLIS)
        val DEFAULT_MAX_BACKOFF: Duration = Duration.ofSeconds(60)
        val DEFAULT_MAX_THROTTLED_DURATION: Duration = Duration.ofMinutes(30)
        private const val MAX_EXPONENT = 20

        fun isThrottling(e: AwsServiceException): Boolean =
            e is ThrottlingException ||
                e is ProvisionedThroughputExceededException ||
                e is RequestLimitExceededException ||
                e.isThrottlingException
    }
}
