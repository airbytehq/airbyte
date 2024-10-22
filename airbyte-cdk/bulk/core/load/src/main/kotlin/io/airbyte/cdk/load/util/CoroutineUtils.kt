/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.util

import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.transformWhile

fun <T> Flow<T>.takeUntilInclusive(predicate: (T) -> Boolean): Flow<T> = transformWhile { value ->
    emit(value)
    !predicate(value)
}

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
