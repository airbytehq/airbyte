/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.dataflow.config.MemoryAndParallelismConfig
import io.airbyte.cdk.load.dataflow.finalization.StreamCompletionTracker
import io.airbyte.cdk.load.dataflow.pipeline.PipelineRunner
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.runBlocking

@Singleton
class DestinationLifecycle(
    private val destinationInitializer: DestinationWriter,
    private val destinationCatalog: DestinationCatalog,
    private val pipeline: PipelineRunner,
    private val completionTracker: StreamCompletionTracker,
    private val memoryAndParallelismConfig: MemoryAndParallelismConfig,
) {
    private val log = KotlinLogging.logger {}

    fun run() {
        // Initialize the destination to make sure that it is ready for the data ingestion
        initializeDestination()

        // Create prepare individual streams for the data ingestion. E.g. create tables and
        // propagate the schema updates
        val streamLoaders = initializeIndividualStreams()

        // Move data
        runBlocking { pipeline.run() }

        finalizeIndividualStreams(streamLoaders)

        teardownDestination()
    }

    private fun initializeDestination() {
        // The run blocking is not needed
        runBlocking {
            log.info { "Initializing the destination" }
            destinationInitializer.setup()
            log.info { "Destination initialized" }
        }
    }

    @OptIn(ExperimentalCoroutinesApi::class)
    private fun initializeIndividualStreams(): List<StreamLoader> {
        val initDispatcher: CoroutineDispatcher =
            Dispatchers.Default.limitedParallelism(
                memoryAndParallelismConfig.maxConcurrentLifecycleOperations
            )

        return runBlocking {
            val result =
                destinationCatalog.streams
                    .map {
                        async(initDispatcher) {
                            log.info {
                                "Starting stream loader for stream ${it.mappedDescriptor.namespace}:${it.mappedDescriptor.name}"
                            }
                            val streamLoader = destinationInitializer.createStreamLoader(it)
                            streamLoader.start()
                            log.info {
                                "Stream loader for stream ${it.mappedDescriptor.namespace}:${it.mappedDescriptor.name} started"
                            }
                            streamLoader
                        }
                    }
                    .awaitAll()

            return@runBlocking result
        }
    }

    @OptIn(ExperimentalCoroutinesApi::class)
    private fun finalizeIndividualStreams(streamLoaders: List<StreamLoader>) {
        if (!completionTracker.allStreamsComplete()) {
            log.warn {
                "One or more streams did not complete. Skipping destructive finalization operations..."
            }
        }

        val finalizeDispatcher: CoroutineDispatcher =
            Dispatchers.Default.limitedParallelism(
                memoryAndParallelismConfig.maxConcurrentLifecycleOperations
            )

        runBlocking {
            streamLoaders
                .map {
                    async(finalizeDispatcher) {
                        log.info {
                            "Finalizing stream ${it.stream.mappedDescriptor.namespace}:${it.stream.mappedDescriptor.name}"
                        }
                        it.teardown(completionTracker.allStreamsComplete())
                        log.info {
                            "Finalized stream ${it.stream.mappedDescriptor.namespace}:${it.stream.mappedDescriptor.name}"
                        }
                    }
                }
                .awaitAll()
        }
    }

    private fun teardownDestination() {
        runBlocking {
            log.info { "Tearing down the destination" }
            destinationInitializer.teardown()
            log.info { "Destination torn down" }
        }
    }
}
