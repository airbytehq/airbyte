/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http.okhttp

import dev.failsafe.RetryPolicy
import dev.failsafe.RetryPolicyBuilder
import dev.failsafe.function.CheckedPredicate
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
import java.time.temporal.ChronoUnit
import kotlin.text.toLong
import okhttp3.Response

private val logger = KotlinLogging.logger {}

class RetryPolicyFactory {
    fun createDefault(): List<RetryPolicy<Response>> {
        return listOf(
            // at the time of this comment, `ofDefaults()` means `3 execution attempts max with no
            // delay when there is an exception`
            RetryPolicy.ofDefaults(),
            fromPredicate { response -> response.code == 429 }
                // when the delay function return a negative number, it'll fall back on any other
                // DelayablePolicy defined (in this case, `withBackoff`)
                .withDelayFn { ctx ->
                    Duration.ofSeconds(ctx.lastResult?.headers?.get("retry-after")?.toLong() ?: -1)
                }
                .withBackoff(1, 300, ChronoUnit.SECONDS)
                .withMaxAttempts(10)
                .onFailedAttempt { e ->
                    logger.warn {
                        "Request got rate limited. Response body is: ${e.lastResult.body?.string() ?: "<empty>"}"
                    }
                }
                .onRetry { _ -> logger.warn { "Retrying rate limited request..." } }
                .build(),
            fromPredicate { response -> response.code >= 500 && response.code < 600 }
                .withBackoff(1, 60, ChronoUnit.SECONDS)
                .withMaxDuration(Duration.ofMinutes(10))
                .onFailedAttempt { e ->
                    logger.warn {
                        "Server error with status ${e.lastResult?.code}. . Response body is: ${e.lastResult?.body?.string() ?: "<empty>"}"
                    }
                }
                .onRetry { _ -> logger.warn { "Retrying request with server error..." } }
                .build(),
        )
    }

    private fun fromPredicate(predicate: CheckedPredicate<Response>): RetryPolicyBuilder<Response> =
        RetryPolicy.builder<Response>()
            .handleResultIf { predicate.test(it) }
            // Specifying handleIf is very weird because we don't care about exceptions here but the
            // retry policy will fail if we don't check the exceptions and there is an exception.
            // See:
            // https://github.com/failsafe-lib/failsafe/blob/98bb496198e18436e654ddca39358a4634ca32bd/core/src/main/java/dev/failsafe/spi/FailurePolicy.java#L59-L60
            .handleIf { _ -> false }
}
