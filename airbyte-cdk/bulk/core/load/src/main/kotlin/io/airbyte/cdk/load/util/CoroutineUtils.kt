/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.util

import java.util.concurrent.atomic.AtomicBoolean

interface CloseableCoroutine {
    suspend fun close()
}

suspend fun <T : CloseableCoroutine, R> T.use(block: suspend (T) -> R) =
    try {
        block(this)
    } finally {
        close()
    }

/** Set the latch exactly once. Return true iff this is the first time we've set it. */
fun AtomicBoolean.setOnce() = compareAndSet(false, true)
