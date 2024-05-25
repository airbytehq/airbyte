/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.concurrency

import io.airbyte.commons.functional.Either
import java.util.*
import java.util.concurrent.CompletableFuture
import java.util.concurrent.CompletionStage
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class CompletableFuturesTest {
    @Test
    fun testAllOf() {
        // Complete in random order
        val futures =
            Arrays.asList<CompletionStage<Int>>(
                returnSuccessWithDelay(1, 2000),
                returnSuccessWithDelay(2, 200),
                returnSuccessWithDelay(3, 500),
                returnSuccessWithDelay(4, 100),
                returnFailureWithDelay("Fail 5", 2000),
                returnFailureWithDelay("Fail 6", 300)
            )

        val allOfResult = CompletableFutures.allOf(futures).toCompletableFuture()
        val result = allOfResult.join()
        val success = result.filter { obj: Either<out Exception, Int> -> obj.isRight() }
        Assertions.assertEquals(
            success,
            Arrays.asList(
                Either.right(1),
                Either.right(2),
                Either.right(3),
                Either.right<Any, Int>(4)
            )
        )
        // Extract wrapped CompletionException messages.
        val failureMessages =
            result
                .filter { obj: Either<out Exception, Int> -> obj.isLeft() }
                .map { either: Either<out Exception, Int> -> either.left!!.cause!!.message }

        Assertions.assertEquals(failureMessages, mutableListOf("Fail 5", "Fail 6"))
    }

    private fun returnSuccessWithDelay(value: Int, delayMs: Long): CompletableFuture<Int> {
        return CompletableFuture.supplyAsync {
            try {
                Thread.sleep(delayMs)
            } catch (e: InterruptedException) {
                throw RuntimeException(e)
            }
            value
        }
    }

    private fun returnFailureWithDelay(message: String, delayMs: Long): CompletableFuture<Int> {
        return CompletableFuture.supplyAsync {
            try {
                Thread.sleep(delayMs)
            } catch (e: InterruptedException) {
                throw RuntimeException(e)
            }
            throw RuntimeException(message)
        }
    }
}
