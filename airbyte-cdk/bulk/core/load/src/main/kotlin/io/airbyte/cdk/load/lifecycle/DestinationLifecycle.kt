package io.airbyte.cdk.load.lifecycle

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.internal.InputConsumerTask
import io.airbyte.cdk.load.write.DestinationWriter
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.runBlocking

@Singleton
class DestinationLifecycle(
    private val inputConsumerTask: InputConsumerTask,
    private val destinationInitializer: DestinationWriter,
    private val syncManager: SyncManager,
    private val destinationCatalog: DestinationCatalog
) {

    private val log = KotlinLogging.logger {}
    suspend fun run() {
        // Start the input consumer which reads the messages from either the stdin or a socket.
        startInputConsumerTask()

        // Initialize the destination to make sure that it is ready for the data ingestion
        initializeDestination()

        // Create prepare individual streams for the data ingestion. E.g create table and propagate the schema updates
        initializeIndividualStream()
    }

    private fun startInputConsumerTask() {
        runBlocking {
            log.info { "Starting input consumer task" }
            inputConsumerTask.execute()
            log.info { "Input consumer task finished" }
        }
    }

    private fun initializeDestination() {
        // The run blocking is not needed
        runBlocking {
            log.info { "Initializing the destination" }
            destinationInitializer.setup()
            syncManager.markSetupComplete()
            log.info { "Destination initialized" }
        }
    }

    private fun initializeIndividualStream() {
        runBlocking {
            destinationCatalog.streams.map {
                async {
                    log.info { "Starting stream loader for stream ${it.mappedDescriptor.namespace}:${it.mappedDescriptor.name}" }
                    val streamLoader = destinationInitializer.createStreamLoader(it)
                    streamLoader.start()
                    log.info { "Stream loader for stream ${it.mappedDescriptor.namespace}:${it.mappedDescriptor.name} started" }
                }
            }.awaitAll()
        }
    }
}
