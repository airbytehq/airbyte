/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.concurrency

import io.airbyte.commons.functional.Either
import java.util.concurrent.CompletableFuture
import java.util.concurrent.CompletionException
import java.util.concurrent.CompletionStage
import java.util.concurrent.ExecutionException

object CompletableFutures {
    /**
     * Non-blocking implementation which does not use join. and returns an aggregated future. The
     * order of results is preserved from the original list of futures.
     *
     * @param futures list of futures
     * @param Result type of result
     * @return a future that completes when all the input futures have completed
     */
    fun <Result> allOf(
        futures: List<CompletionStage<Result>>
    ): CompletionStage<List<Either<out Exception, Result>>> {
        val futuresArray: Array<CompletableFuture<Result>> =
            futures.map { it.toCompletableFuture() }.toTypedArray()
        return CompletableFuture.allOf(*futuresArray)
            // We're going to get the individual exceptions from the futures,
            // so we ignore the Throwable parameter here.
            // stdlib's allOf() gives us a Void, so we ignore the value as well,
            // and manually fetch the individual future values.
            .handle { _: Void?, _: Throwable? ->
                futures.map {
                    try {
                        // By the time we get here, the futures have already
                        // completed, so we can just get() them
                        Either.right(it.toCompletableFuture().get())
                    } catch (e: ExecutionException) {
                        // For historical reasons, we return the wrapped
                        // exception instead of just returning the underlying
                        // cause.
                        // For _other_ historical reasons, we rewrap this into
                        // a CompletionException.
                        // In practice, most callers will just check the value
                        // of `result.left.cause`, which doesn't care about
                        // the actual exception type.
                        Either.left(CompletionException(e.cause))
                    } catch (e: Exception) {
                        Either.left(e)
                    }
                    // handle() will take care of other Throwable types,
                    // so don't explicitly handle them.
                    // We want to crash loudly on e.g. OutOfMemoryError.
                }
            }
    }
}
