package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.runBlocking

@Singleton
class DestinationLifecycle(
    private val destinationInitializer: DestinationWriter,
    private val destinationCatalog: DestinationCatalog,
    private val pipeline: DataFlowPipeline,
) {
    private val log = KotlinLogging.logger {}

    fun run() {
        // Initialize the destination to make sure that it is ready for the data ingestion
        initializeDestination()

        // Create prepare individual streams for the data ingestion. E.g create tables and propagate
        // the schema updates
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

    private fun initializeIndividualStreams(): List<StreamLoader> {
        return runBlocking {
            val result = mutableListOf<StreamLoader>()
            destinationCatalog.streams
                .map {
                    async {
                        log.info {
                            "Starting stream loader for stream ${it.mappedDescriptor.namespace}:${it.mappedDescriptor.name}"
                        }
                        val streamLoader = destinationInitializer.createStreamLoader(it)
                        streamLoader.start()
                        result.add(streamLoader)
                        log.info {
                            "Stream loader for stream ${it.mappedDescriptor.namespace}:${it.mappedDescriptor.name} started"
                        }
                    }
                }
                .awaitAll()

            return@runBlocking result
        }
    }

    private fun finalizeIndividualStreams(streamLoaders: List<StreamLoader>) {
        runBlocking {
            streamLoaders
                .map {
                    async {
                        log.info {
                            "Finalizing stream ${it.stream.mappedDescriptor.namespace}:${it.stream.mappedDescriptor.name}"
                        }
                        it.close(true)
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
