/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.util

import kotlin.coroutines.CoroutineContext
import kotlinx.coroutines.ThreadContextElement

/** Alternative to [kotlinx.coroutines.CoroutineName] that works in prod. */
data class ThreadRenamingCoroutineName(
    val name: String,
) : ThreadContextElement<String> {
    companion object Key : CoroutineContext.Key<ThreadRenamingCoroutineName>

    override val key: CoroutineContext.Key<ThreadRenamingCoroutineName>
        get() = Key

    override fun updateThreadContext(context: CoroutineContext): String {
        val previousName: String = Thread.currentThread().name
        Thread.currentThread().name = "$previousName#$name"
        return previousName
    }

    override fun restoreThreadContext(
        context: CoroutineContext,
        oldState: String,
    ) {
        Thread.currentThread().name = oldState
    }

    override fun toString(): String = "CoroutineName($name)"
}
