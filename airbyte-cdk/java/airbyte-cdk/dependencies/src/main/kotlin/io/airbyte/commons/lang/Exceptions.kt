/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.lang

import java.lang.invoke.MethodHandles
import java.util.concurrent.Callable
import java.util.function.Function
import org.slf4j.Logger
import org.slf4j.LoggerFactory

object Exceptions {
    private val log: Logger = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass())

    /**
     * Catch a checked exception and rethrow as a [RuntimeException]
     *
     * @param callable
     * - function that throws a checked exception.
     * @param <T> - return type of the function.
     * @return object that the function returns. </T>
     */
    @JvmStatic
    fun <T> toRuntime(callable: Callable<T>): T {
        try {
            return callable.call()
        } catch (e: java.lang.RuntimeException) {
            throw e
        } catch (e: Exception) {
            throw java.lang.RuntimeException(e)
        }
    }

    /**
     * Catch a checked exception and rethrow as a [RuntimeException].
     *
     * @param voidCallable
     * - function that throws a checked exception.
     */
    @JvmStatic
    fun toRuntime(voidCallable: Procedure) {
        castCheckedToRuntime(voidCallable) { cause: Exception -> RuntimeException(cause) }
    }

    private fun castCheckedToRuntime(
        voidCallable: Procedure,
        exceptionFactory: Function<Exception, java.lang.RuntimeException>
    ) {
        try {
            voidCallable.call()
        } catch (e: java.lang.RuntimeException) {
            throw e
        } catch (e: Exception) {
            throw exceptionFactory.apply(e)
        }
    }

    fun swallow(procedure: Procedure) {
        try {
            procedure.call()
        } catch (e: Exception) {
            log.error("Swallowed error.", e)
        }
    }

    fun <T> swallowWithDefault(procedure: Callable<T>, defaultValue: T): T {
        return try {
            procedure.call()
        } catch (e: Exception) {
            defaultValue
        }
    }

    fun interface Procedure {
        @Throws(Exception::class) fun call()
    }
}
