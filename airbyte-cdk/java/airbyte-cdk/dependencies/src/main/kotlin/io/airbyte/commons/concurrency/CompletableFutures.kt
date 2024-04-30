/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.concurrency

import io.airbyte.commons.functional.Either
import java.util.*
import java.util.concurrent.CompletableFuture
import java.util.concurrent.CompletionStage
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.flow.*

object CompletableFutures {
    /**
     * Non-blocking implementation which does not use join. and returns an aggregated future. The
     * order of results is preserved from the original list of futures.
     *
     * @param futures list of futures
     * @param <Result> type of result
     * @return a future that completes when all the input futures have completed </Result>
     */
    fun <Result> allOf(
        futures: List<CompletionStage<Result>>
    ): CompletionStage<List<Either<out Exception, Result>>> {
        val result = CompletableFuture<List<Either<out Exception, Result>>>()
        val size = futures.size
        val counter = AtomicInteger()
        // This whole function should probably use kotlin flows, but I couldn't figure it out...
        @Suppress("unchecked_cast")
        val results =
            java.lang.reflect.Array.newInstance(Either::class.java, size)
                as Array<Either<Exception, Result>>
        // attach a whenComplete to all futures

        for (i in 0 until size) {
            val currentIndex = i
            futures[i].whenComplete { value: Result, exception: Throwable? ->
                // if exception is null, then the future completed successfully
                // maybe synchronization is unnecessary here, but it's better to be safe
                synchronized(results) {
                    if (exception == null) {
                        results[currentIndex] = Either.right(value)
                    } else {
                        if (exception is Exception) {
                            results[currentIndex] = Either.left(exception)
                        } else {
                            // this should never happen
                            throw RuntimeException(
                                "Unexpected exception in a future completion.",
                                exception
                            )
                        }
                    }
                }
                val completedCount = counter.incrementAndGet()
                if (completedCount == size) {
                    result.complete(Arrays.asList(*results))
                }
            }
        }
        return result
    }
}
