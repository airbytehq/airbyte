/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.dataflow.finalization.StreamCompletionTracker
import io.airbyte.cdk.load.dataflow.pipeline.PipelineRunner
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.CoroutineDispatcher
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
    @Named("streamInitDispatcher") private val streamInitDispatcher: CoroutineDispatcher,
    @Named("streamFinalizeDispatcher") private val streamFinalizeDispatcher: CoroutineDispatcher,
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

        // At this point all pipelines have completed and all aggregates have been flushed.
        // Notify each input-complete stream so connectors can perform per-stream finalization
        // (e.g., merging a staging branch into main in Iceberg) before teardown.
        notifyPerStreamFlushCompletion(streamLoaders)

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
        return runBlocking {
            val result =
                destinationCatalog.streams
                    .map {
                        async(streamInitDispatcher) {
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

    /**
     * After all pipelines have completed (all records received and all aggregates flushed), call
     * [StreamLoader.onStreamFlushed] for each stream whose source sent a completion message. This
     * allows connectors to perform per-stream finalization before the overall teardown.
     */
    @OptIn(ExperimentalCoroutinesApi::class)
    private fun notifyPerStreamFlushCompletion(streamLoaders: List<StreamLoader>) {
        runBlocking {
            streamLoaders
                .filter { completionTracker.isInputComplete(it.stream.mappedDescriptor) }
                .map {
                    async(streamFinalizeDispatcher) {
                        val desc = it.stream.mappedDescriptor
                        log.info {
                            "Stream ${desc.namespace}:${desc.name} is fully flushed. " +
                                "Invoking onStreamFlushed callback."
                        }
                        it.onStreamFlushed()
                        log.info {
                            "Stream ${desc.namespace}:${desc.name} onStreamFlushed completed."
                        }
                    }
                }
                .awaitAll()
        }
    }

    @OptIn(ExperimentalCoroutinesApi::class)
    private fun finalizeIndividualStreams(streamLoaders: List<StreamLoader>) {
        if (!completionTracker.allStreamsComplete()) {
            log.warn {
                "One or more streams did not complete. Skipping destructive finalization operations..."
            }
        }

        runBlocking {
            streamLoaders
                .map {
                    async(streamFinalizeDispatcher) {
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
