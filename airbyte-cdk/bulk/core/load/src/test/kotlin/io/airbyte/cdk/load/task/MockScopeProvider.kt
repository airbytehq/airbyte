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
class MockScopeProvider : TaskScopeProvider<ScopedTask> {
    private val didCloseAB = AtomicBoolean(false)

    val didClose
        get() = didCloseAB.get()

    override suspend fun launch(task: ScopedTask) {
        task.execute()
    }

    override suspend fun close() {
        didCloseAB.set(true)
    }
}
