/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil.logAllAndThrowFirst
import java.util.*
import java.util.concurrent.CompletableFuture

object FutureUtils {
    private const val DEFAULT_TD_THREAD_COUNT = 8

    val countOfTypeAndDedupeThreads: Int
        /**
         * Allow for configuring the number of typing and deduping threads via an environment
         * variable in the destination container.
         *
         * @return the number of threads to use in the typing and deduping pool
         */
        get() =
            Optional.ofNullable(System.getenv("TD_THREADS"))
                .map { s -> s.toInt() }
                .orElse(DEFAULT_TD_THREAD_COUNT)

    /**
     * Log all exceptions from a list of futures, and rethrow the first exception if there is one.
     * This mimics the behavior of running the futures in serial, where the first failure
     */
    @Throws(Exception::class)
    fun reduceExceptions(
        potentialExceptions: Collection<CompletableFuture<Optional<Exception>>>,
        initialMessage: String
    ) {
        val exceptions =
            potentialExceptions
                .map { obj: CompletableFuture<Optional<Exception>> -> obj.join() }
                .filter { obj: Optional<Exception> -> obj.isPresent }
                .map { obj: Optional<Exception> -> obj.get() }
                .toList()
        logAllAndThrowFirst(initialMessage, exceptions)
    }
}
