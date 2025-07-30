package io.airbyte.cdk.load.lifecycle

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.dataflow.DataFlowPipeline
import io.airbyte.cdk.load.lifecycle.steps.CreateInputFlowStep
import io.airbyte.cdk.load.lifecycle.steps.TransformDataStep
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.write.DestinationWriter
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.runBlocking

@Singleton
class DestinationLifecycle(
    private val createInputFlowStep: CreateInputFlowStep,
    private val destinationInitializer: DestinationWriter,
    private val syncManager: SyncManager,
    private val destinationCatalog: DestinationCatalog,
    private val transformDataStep: TransformDataStep,
    private val dfp: DataFlowPipeline,
) {

    private val log = KotlinLogging.logger {}
    suspend fun run() {
        // Initialize the destination to make sure that it is ready for the data ingestion
        initializeDestination()

        // Create prepare individual streams for the data ingestion. E.g create tables and propagate the schema updates
        initializeIndividualStream()

        // Start the input consumer which reads the messages from either the stdin or a socket.
        val flow = startInputConsumerTask()

        // Start the data ingestion
//        val tansformedDataFlow: Flow<TransformDataStep.MungedRecordWrapper> = transformDataStep.transformData(flow)
        runBlocking {
            dfp.run()
        }
    }

    private fun startInputConsumerTask(): Flow<DestinationRecordRaw> {
        return runBlocking {
            log.info { "Starting input consumer task" }
            val inputFlow = createInputFlowStep.getInputFlow()
            log.info { "Input consumer task finished" }
            return@runBlocking inputFlow
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
