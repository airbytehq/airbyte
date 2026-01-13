/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.util

import java.util.concurrent.atomic.AtomicBoolean

interface CloseableCoroutine {
    suspend fun close()
}

// this is taken almost verbatim from kotlin's AutoCloseable?.use implementation,
// but with `suspend` modifiers added.
suspend inline fun <T : CloseableCoroutine, R> T.use(block: (T) -> R): R {
    var exception: Throwable? = null
    try {
        return block(this)
    } catch (e: Throwable) {
        exception = e
        throw e
    } finally {
        this.closeFinally(exception)
    }
}

suspend inline fun CloseableCoroutine.closeFinally(cause: Throwable?): Unit =
    when {
        cause == null -> close()
        else ->
            try {
                close()
            } catch (closeException: Throwable) {
                cause.addSuppressed(closeException)
            }
    }

/** Set the latch exactly once. Return true iff this is the first time we've set it. */
fun AtomicBoolean.setOnce() = compareAndSet(false, true)
