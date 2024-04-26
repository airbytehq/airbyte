/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.operation

import io.airbyte.cdk.command.InputState
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.read.StateManager
import io.airbyte.cdk.read.StateManagerFactory
import io.airbyte.cdk.read.WorkerFactory
import io.airbyte.cdk.read.WorkerThreadRunnable
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.util.concurrent.ExecutionException
import java.util.concurrent.Executors
import java.util.concurrent.Future
import java.util.concurrent.ThreadFactory

private val log = KotlinLogging.logger {}

@Singleton
@Requires(property = CONNECTOR_OPERATION, value = "read")
@Requires(env = ["source"])
class ReadOperation(
    val config: SourceConfiguration,
    val configuredCatalog: ConfiguredAirbyteCatalog,
    val inputState: InputState,
    val stateManagerFactory: StateManagerFactory,
    val workerFactory: WorkerFactory,
) : Operation {

    override val type = OperationType.READ

    override fun execute() {
        val stateManager: StateManager =
            stateManagerFactory.create(config, configuredCatalog, inputState)
        val threadFactory =
            object : ThreadFactory {
                var n = 1L
                override fun newThread(r: Runnable): Thread = Thread(r, "read-worker-${n++}")
            }
        val ex = Executors.newFixedThreadPool(config.workerConcurrency, threadFactory)
        val runnables =
            stateManager.currentStates().map {
                WorkerThreadRunnable(workerFactory, config.workUnitSoftTimeout, stateManager, it)
            }
        val futures: Map<Future<*>, String> = runnables.associate { ex.submit(it) to it.name }
        var n = 0L
        for ((future, name) in futures) {
            try {
                future.get()
            } catch (e: ExecutionException) {
                n++
                log.error(e.cause ?: e) { "exception thrown by '$name', $n total so far" }
            }
        }
        if (n > 0) {
            throw OperationExecutionException(type, "incomplete read due to $n thread failure(s)")
        }
    }
}
