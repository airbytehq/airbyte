/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.util

import com.google.common.collect.ImmutableList
import io.airbyte.commons.functional.Either
import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.commons.lang3.exception.ExceptionUtils

private val LOGGER = KotlinLogging.logger {}
/** Utility class defining methods for handling configuration exceptions in connectors. */
object ConnectorExceptionUtil {

    const val COMMON_EXCEPTION_MESSAGE_TEMPLATE: String =
        "Could not connect with provided configuration. Error: %s"

    @JvmField val HTTP_AUTHENTICATION_ERROR_CODES: List<Int> = ImmutableList.of(401, 403)

    /**
     * Log all the exceptions, and rethrow the first. This is useful for e.g. running multiple
     * futures and waiting for them to complete/fail. Rather than combining them into a single
     * mega-exception (which works poorly in the UI), we just log all of them, and throw the first
     * exception.
     *
     * In most cases, all the exceptions will look very similar, so the user only needs to see the
     * first exception anyway. This mimics e.g. a for-loop over multiple tasks, where the loop would
     * break on the first exception.
     */
    @JvmStatic
    fun <T : Throwable> logAllAndThrowFirst(initialMessage: String, throwables: Collection<T>) {
        if (!throwables.isEmpty()) {
            val stacktraces =
                throwables.joinToString("\n") { throwable: Throwable ->
                    ExceptionUtils.getStackTrace(throwable)
                }
            LOGGER.error { "$initialMessage$stacktraces\nRethrowing first exception." }
            throw throwables.iterator().next()
        }
    }

    @JvmStatic
    fun <T : Throwable, Result> getResultsOrLogAndThrowFirst(
        initialMessage: String,
        eithers: List<Either<out T, Result>>
    ): List<Result> {
        val throwables: List<T> = eithers.filter { it.isLeft() }.map { it.left!! }
        if (throwables.isNotEmpty()) {
            logAllAndThrowFirst(initialMessage, throwables)
        }
        // No need to filter on isRight since isLeft will throw before reaching this line.
        return eithers.map { obj: Either<out T, Result> -> obj.right!! }
    }
}
