/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.net.ConnectException
import java.net.URI
import java.net.URLEncoder
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import java.net.http.HttpTimeoutException
import java.nio.charset.StandardCharsets
import java.time.Duration
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ThreadLocalRandom
import kotlin.math.max
import kotlin.math.min
import kotlinx.coroutines.delay

private val log = KotlinLogging.logger {}

/**
 * The Slack Web API client of the connector: plain HTTP (`java.net.http`) plus Jackson, so that
 * records are the raw JSON objects Slack returns, exactly as the legacy connector emitted them.
 *
 * **Rate limits.** Slack limits every Web API method separately, per app and workspace (Tier 1: 1+
 * per minute, Tier 2: 20+, Tier 3: 50+, Tier 4: 100+, with short bursts allowed), and answers HTTP
 * 429 with a `Retry-After` header when a method's budget is exhausted. Since the May 2025 terms
 * change, `conversations.history` and `conversations.replies` are additionally limited to 1 request
 * per minute (15 objects per page) for apps that are not listed on the Slack Marketplace. The
 * legacy connector only reacted to 429s (sleeping for `Retry-After`, then, for OAuth, dropping to
 * one request per minute until five requests succeeded). This client keeps one adaptive token
 * bucket per method ([MethodRateLimiter]): requests are paced at the method's documented tier rate
 * so that 429s are rare, a 429 halves the rate (never below one request per minute) and honours
 * `Retry-After`, and sustained successes restore the rate step by step. Because the buckets are per
 * method, the streams (each on its own method) can be read concurrently without competing for the
 * same budget.
 *
 * **Errors.** Slack reports most errors as HTTP 200 with `{"ok": false, "error": "..."}`. They are
 * classified like the legacy manifest did: authentication and permission errors are
 * [ConfigErrorException]s, transient service errors are retried with backoff and become a
 * [TransientErrorException] when the retries are exhausted, the errors a stream should skip a
 * partition on (`not_in_channel`, `channel_not_found`, ...) are [SlackSkipException]s, and anything
 * else is a [SlackApiException] (a system error).
 */
@SuppressFBWarnings(value = ["NP_NONNULL_PARAM_VIOLATION"], justification = "Kotlin coroutines")
class SlackApiClient(
    private val configuration: SlackSourceConfiguration,
    /** Multiplies every method's rate; tests against the fake server run at a high scale. */
    rateLimitScale: Double = 1.0,
    private val maxAttempts: Int = DEFAULT_MAX_ATTEMPTS,
    private val httpClient: HttpClient =
        HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(30)).build(),
) : AutoCloseable {

    private val limiters = ConcurrentHashMap<String, MethodRateLimiter>()
    private val scale: Double = rateLimitScale.coerceAtLeast(MIN_RATE_LIMIT_SCALE)

    /** The response envelope of a `GET <method>?<params>` call whose `ok` is true. */
    suspend fun get(method: String, params: Map<String, String> = emptyMap()): ObjectNode =
        call(method, params, post = false)

    /** The response envelope of a `POST <method>` call (JSON body) whose `ok` is true. */
    suspend fun post(method: String, params: Map<String, String> = emptyMap()): ObjectNode =
        call(method, params, post = true)

    /**
     * Every page of a cursor-paginated method, as a sequence of envelopes: the next page is fetched
     * when the sequence advances, from `response_metadata.next_cursor` until it is empty.
     */
    suspend fun pages(
        method: String,
        params: Map<String, String>,
        firstCursor: String? = null,
        onPage: suspend (page: ObjectNode, requestCursor: String?, nextCursor: String?) -> Boolean,
    ) {
        var cursor: String? = firstCursor?.ifBlank { null }
        while (true) {
            val page: ObjectNode =
                get(method, if (cursor == null) params else params + ("cursor" to cursor))
            val next: String? = nextCursor(page)
            val goOn: Boolean = onPage(page, cursor, next)
            if (!goOn || next == null) {
                return
            }
            cursor = next
        }
    }

    fun limiter(method: String): MethodRateLimiter =
        limiters.computeIfAbsent(method) {
            MethodRateLimiter(it, SlackRateLimits.perMinute(it) * scale)
        }

    private suspend fun call(
        method: String,
        params: Map<String, String>,
        post: Boolean
    ): ObjectNode {
        val limiter: MethodRateLimiter = limiter(method)
        var attempt = 0
        var backoffMillis: Long = INITIAL_BACKOFF_MILLIS
        while (true) {
            attempt++
            limiter.acquire()
            val response: HttpResponse<String> =
                try {
                    httpClient.send(
                        request(method, params, post),
                        HttpResponse.BodyHandlers.ofString()
                    )
                } catch (e: HttpTimeoutException) {
                    if (attempt >= maxAttempts) {
                        throw TransientErrorException(
                            "Slack API $method timed out $attempt times.",
                            e
                        )
                    }
                    log.warn {
                        "Slack API $method timed out (attempt $attempt); retrying in ${backoffMillis}ms"
                    }
                    delay(backoffMillis)
                    backoffMillis = min(backoffMillis * 2, MAX_BACKOFF_MILLIS)
                    continue
                } catch (e: IOException) {
                    // A refused connection or an unknown host will not fix itself in a minute:
                    // fail fast so that CHECK reports it, instead of retrying for many minutes.
                    val attempts: Int =
                        if (e is ConnectException) MAX_CONNECT_ATTEMPTS else maxAttempts
                    if (attempt >= attempts) {
                        throw TransientErrorException(
                            "Could not reach the Slack API at ${configuration.apiBaseUrl} ($method): ${e.message}",
                            e,
                        )
                    }
                    log.warn(e) {
                        "Slack API $method failed (attempt $attempt); retrying in ${backoffMillis}ms"
                    }
                    delay(backoffMillis)
                    backoffMillis = min(backoffMillis * 2, MAX_BACKOFF_MILLIS)
                    continue
                }
            val status: Int = response.statusCode()
            val body: ObjectNode? = parseBody(response.body())
            val error: String? = body?.get("error")?.asText()
            val ok: Boolean = body?.get("ok")?.asBoolean() ?: (status in 200..299)

            if (status == HTTP_TOO_MANY_REQUESTS || error == RATE_LIMITED) {
                val retryAfter: Duration = retryAfter(response)
                limiter.onRateLimited(retryAfter)
                if (attempt >= maxAttempts) {
                    throw TransientErrorException(
                        "Slack API rate limited: $method was rejected $attempt times in a row " +
                            "(last Retry-After: ${retryAfter.toSeconds()}s).",
                    )
                }
                log.warn {
                    "Slack API rate limited $method (HTTP $status); waiting ${retryAfter.toSeconds()}s " +
                        "and pacing $method at ${"%.2f".format(limiter.currentPerMinute())} requests/min"
                }
                continue
            }
            if (ok && status in 200..299 && body != null) {
                limiter.onSuccess()
                return body
            }
            if (status >= 500 || error in TRANSIENT_ERRORS) {
                if (attempt >= maxAttempts) {
                    throw TransientErrorException(
                        "Slack API $method failed $attempt times: HTTP $status ${error ?: ""}".trim(),
                    )
                }
                log.warn {
                    "Slack API $method returned HTTP $status ${error ?: ""} (attempt $attempt); retrying in ${backoffMillis}ms"
                }
                delay(backoffMillis)
                backoffMillis = min(backoffMillis * 2, MAX_BACKOFF_MILLIS)
                continue
            }
            if (error in AUTH_ERRORS) {
                throw ConfigErrorException(
                    "Slack API authentication/permission error: $error." +
                        (body?.get("needed")?.asText()?.let { " Missing OAuth scope: $it." } ?: ""),
                )
            }
            if (error in SKIP_ERRORS) {
                throw SlackSkipException(method, error!!, params)
            }
            if (status == 403 || status == 400 || status == 401) {
                throw ConfigErrorException(
                    "Slack API $method request denied or malformed (HTTP $status${error?.let { ": $it" } ?: ""}).",
                )
            }
            throw SlackApiException(
                method,
                error,
                "Slack API returned an unrecognized error: ${error ?: "HTTP $status"} (method $method).",
            )
        }
    }

    private fun request(method: String, params: Map<String, String>, post: Boolean): HttpRequest {
        val builder: HttpRequest.Builder =
            HttpRequest.newBuilder()
                .timeout(REQUEST_TIMEOUT)
                .header("Authorization", "Bearer ${configuration.token}")
                .header("Accept", "application/json")
        if (post) {
            val body: ObjectNode = Jsons.objectNode()
            params.forEach { (k, v) -> body.put(k, v) }
            return builder
                .uri(configuration.apiBaseUrl.resolve(method))
                .header("Content-Type", "application/json; charset=utf-8")
                .POST(HttpRequest.BodyPublishers.ofString(Jsons.writeValueAsString(body)))
                .build()
        }
        val query: String =
            params.entries.joinToString("&") { (k, v) -> "${encode(k)}=${encode(v)}" }
        val uri: URI =
            configuration.apiBaseUrl.resolve(if (query.isEmpty()) method else "$method?$query")
        return builder.uri(uri).GET().build()
    }

    override fun close() {
        // java.net.http.HttpClient has no close() before JDK 21's AutoCloseable; nothing to do.
    }

    companion object {
        const val HTTP_TOO_MANY_REQUESTS = 429
        const val RATE_LIMITED = "ratelimited"
        const val DEFAULT_MAX_ATTEMPTS = 20
        const val MAX_CONNECT_ATTEMPTS = 3
        const val INITIAL_BACKOFF_MILLIS = 1_000L
        const val MAX_BACKOFF_MILLIS = 60_000L
        /** When Slack rate limits without a `Retry-After` header. */
        val DEFAULT_RETRY_AFTER: Duration = Duration.ofSeconds(30)
        val REQUEST_TIMEOUT: Duration = Duration.ofMinutes(2)
        const val MIN_RATE_LIMIT_SCALE = 0.01

        /** Same lists as the legacy manifest's error handlers. */
        val AUTH_ERRORS: Set<String> =
            setOf(
                "missing_scope",
                "not_authed",
                "account_inactive",
                "invalid_auth",
                "token_revoked",
                "token_expired",
                "no_permission",
                "org_login_required",
                "ekm_access_denied",
                "access_denied",
                "not_allowed_token_type",
                "enterprise_is_restricted",
                "team_access_not_granted",
            )
        val SKIP_ERRORS: Set<String> =
            setOf(
                "not_in_channel",
                "channel_not_found",
                "channel_is_limited_access",
                "is_archived",
                "thread_not_found",
                "method_not_supported_for_channel_type",
            )
        val TRANSIENT_ERRORS: Set<String> =
            setOf(
                "request_timeout",
                "service_unavailable",
                "fatal_error",
                "internal_error",
                "accesslimited",
                "team_added_to_org",
            )

        fun nextCursor(page: JsonNode): String? =
            page.get("response_metadata")?.get("next_cursor")?.asText()?.ifBlank { null }

        private fun encode(s: String): String = URLEncoder.encode(s, StandardCharsets.UTF_8)

        private fun parseBody(body: String?): ObjectNode? =
            try {
                if (body.isNullOrBlank()) null else Jsons.readTree(body) as? ObjectNode
            } catch (_: Exception) {
                null
            }

        private fun retryAfter(response: HttpResponse<*>): Duration =
            response
                .headers()
                .firstValue("Retry-After")
                .map { it.trim().toLongOrNull() }
                .orElse(null)
                ?.let { Duration.ofSeconds(it) }
                ?: DEFAULT_RETRY_AFTER
    }
}

/** A Slack error the legacy connector skipped the partition on (`not_in_channel`, ...). */
class SlackSkipException(val method: String, val error: String, val params: Map<String, String>) :
    RuntimeException("Slack API $method returned '$error' for $params; skipping.")

/** A Slack `ok: false` error nobody expected; the sync fails with a system error. */
class SlackApiException(val method: String, val error: String?, message: String) :
    RuntimeException(message)

/**
 * Documented rate limit tiers of the methods the connector calls, in requests per minute. Slack
 * documents them as "N+ per minute" with bursts allowed; the connector paces at exactly N and
 * relies on 429s (see [MethodRateLimiter]) for the rest.
 */
object SlackRateLimits {
    const val TIER_1 = 1.0
    const val TIER_2 = 20.0
    const val TIER_3 = 50.0
    const val TIER_4 = 100.0

    /**
     * `conversations.history` and `conversations.replies` for apps that are not on the Slack
     * Marketplace (terms change of May 2025): one request per minute, 15 objects per page. The
     * limiter drops to this rate on the first 429 and, if the app really is limited like this,
     * stays there; it starts at Tier 3 because Airbyte Cloud's OAuth app is a Marketplace app.
     */
    const val NON_MARKETPLACE_HISTORY = 1.0
    const val NON_MARKETPLACE_PAGE_SIZE = 15

    private val perMinute: Map<String, Double> =
        mapOf(
            // "Special" tier: hundreds per minute.
            "auth.test" to 600.0,
            "users.list" to TIER_2,
            "conversations.list" to TIER_2,
            "conversations.members" to TIER_4,
            "conversations.history" to TIER_3,
            "conversations.replies" to TIER_3,
            "conversations.join" to TIER_3,
            "conversations.info" to TIER_3,
        )

    fun perMinute(method: String): Double = perMinute[method] ?: TIER_2
}

/**
 * Adaptive token bucket of one Web API method. Refills at [currentPerMinute] requests per minute
 * with a burst of [burst] requests; [onRateLimited] halves the rate (never below one request per
 * minute) and blocks the bucket for the `Retry-After` duration, [onSuccess] restores the rate by a
 * quarter after every [RECOVERY_SUCCESSES] successes, up to the configured tier rate.
 */
class MethodRateLimiter(
    val method: String,
    private val configuredPerMinute: Double,
    private val burst: Double = DEFAULT_BURST,
    private val nanoTime: () -> Long = System::nanoTime,
) {
    private val lock = Any()
    private var perMinute: Double = configuredPerMinute
    private var tokens: Double = min(burst, configuredPerMinute)
    private var lastRefillNanos: Long = nanoTime()
    private var blockedUntilNanos: Long = Long.MIN_VALUE
    private var successes: Int = 0
    var rateLimitedCount: Long = 0
        private set

    fun currentPerMinute(): Double = synchronized(lock) { perMinute }

    /** Suspends until a request may be sent. */
    suspend fun acquire() {
        while (true) {
            val waitNanos: Long = tryAcquireOrWaitNanos()
            if (waitNanos <= 0L) {
                return
            }
            delay(waitNanos / 1_000_000L + 1)
        }
    }

    /** 0 when a token was taken; otherwise how long to wait before trying again. */
    fun tryAcquireOrWaitNanos(): Long =
        synchronized(lock) {
            val now: Long = nanoTime()
            if (now < blockedUntilNanos) {
                return blockedUntilNanos - now
            }
            refill(now)
            if (tokens >= 1.0) {
                tokens -= 1.0
                return 0L
            }
            val perNano: Double = perMinute / 60_000_000_000.0
            ((1.0 - tokens) / perNano).toLong().coerceAtLeast(1L)
        }

    private fun refill(now: Long) {
        val elapsed: Long = now - lastRefillNanos
        if (elapsed > 0) {
            tokens = min(burst, tokens + elapsed * (perMinute / 60_000_000_000.0))
            lastRefillNanos = now
        }
    }

    fun onRateLimited(retryAfter: Duration) {
        synchronized(lock) {
            rateLimitedCount++
            successes = 0
            tokens = 0.0
            // Halve the rate, and never exceed what Retry-After implies: a 60 s Retry-After means
            // the method is on the one-request-per-minute regime, a 1 s one only a burst.
            val impliedPerMinute: Double = 60.0 / retryAfter.toSeconds().coerceAtLeast(1L)
            perMinute = max(MIN_PER_MINUTE, min(perMinute / 2.0, impliedPerMinute))
            // A little jitter so that concurrent readers do not all retry in the same instant.
            val jitterNanos: Long = ThreadLocalRandom.current().nextLong(0L, 500_000_000L)
            blockedUntilNanos = nanoTime() + retryAfter.toNanos() + jitterNanos
            lastRefillNanos = blockedUntilNanos
        }
    }

    fun onSuccess() {
        synchronized(lock) {
            if (perMinute >= configuredPerMinute) {
                return
            }
            successes++
            if (successes >= RECOVERY_SUCCESSES) {
                successes = 0
                perMinute = min(configuredPerMinute, perMinute * 1.25)
                log.info {
                    "Slack API $method: rate restored to ${"%.2f".format(perMinute)} requests/min"
                }
            }
        }
    }

    companion object {
        const val DEFAULT_BURST = 5.0
        const val MIN_PER_MINUTE = 1.0
        const val RECOVERY_SUCCESSES = 20
    }
}
