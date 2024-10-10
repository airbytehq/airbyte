/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean

@Singleton
@Primary
@Requires(env = ["MockScopeProvider"])
class MockScopeProvider : TaskScopeProvider<WrappedTask<ScopedTask>> {
    private val didCloseAB = AtomicBoolean(false)
    private val didKillAB = AtomicBoolean(false)

    val didClose
        get() = didCloseAB.get()
    val didKill
        get() = didKillAB.get()

    override suspend fun launch(task: WrappedTask<ScopedTask>) {
        task.execute()
    }

    override suspend fun close() {
        didCloseAB.set(true)
    }

    override suspend fun kill() {
        didKillAB.set(true)
    }
}
