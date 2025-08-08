package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.csv.toCsvRecord
import io.airbyte.cdk.load.message.BatchState
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.WithBatchState
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.BatchAccumulator
import io.airbyte.cdk.load.pipeline.BatchAccumulatorResult
import io.airbyte.cdk.load.pipeline.FinalOutput
import io.airbyte.cdk.load.pipeline.IntermediateOutput
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.pipeline.NoOutput
import io.airbyte.cdk.load.pipeline.OutputPartitioner
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayOutputStream
import java.io.PrintWriter
import java.nio.charset.StandardCharsets
import kotlin.random.Random
import kotlinx.coroutines.flow.Flow
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVPrinter
import org.apache.commons.csv.QuoteMode

//class FlattenQueueAdapter<K : WithStream, T>(
////    private val queue: PartitionedQueue<PipelineEvent<K, T>>,
////) : PartitionedQueue<PipelineEvent<K, HttpStepOutput<T>>> {
////    override val partitions = queue.partitions
////
////    override fun consume(partition: Int): Flow<PipelineEvent<K, HttpStepOutput<T>>> {
////        throw IllegalStateException(
////            "Trying to consume from the adapter instead of the underlying queue"
////        )
////    }
////
////    override suspend fun close() {
////        queue.close()
////    }
////
////    override suspend fun broadcast(value: PipelineEvent<K, HttpStepOutput<T>>) {
////        when (value) {
////            is PipelineMessage -> value.flatten().forEach {
////                KotlinLogging.logger {  }.error { "piping $it" }
////                queue.broadcast(it)
////            }
////            is PipelineHeartbeat -> queue.broadcast(PipelineHeartbeat())
////            is PipelineEndOfStream -> queue.broadcast(PipelineEndOfStream(value.stream))
////        }
////    }
////
////    override suspend fun publish(value: PipelineEvent<K, HttpStepOutput<T>>, partition: Int) {
////        when (value) {
////            is PipelineMessage -> value.flatten().forEach {
////                KotlinLogging.logger {  }.error { "piping $it" }
////                queue.publish(it, partition)
////            }
////            is PipelineHeartbeat -> queue.publish(PipelineHeartbeat(), partition)
////            is PipelineEndOfStream -> queue.publish(PipelineEndOfStream(value.stream), partition)
////        }
////    }
////
////    // As we are flattening the message, to avoid duplicating the counts, we push them all down
////    // to the last message.
////    private fun PipelineMessage<K, HttpStepOutput<T>>.flatten()
////    : Iterable<PipelineMessage<K, T>> {
////        val lastIndex = value.failedRecords.size - 1
////        return value.failedRecords.mapIndexed { idx, m ->
////            if (idx < lastIndex) {
////                PipelineMessage(
////                    checkpointCounts = emptyMap(),
////                    key = key,
////                    value = m,
////                    postProcessingCallback = null,
////                    context = context,
////                )
////            } else {
////                PipelineMessage(
////                    checkpointCounts = checkpointCounts,
////                    key = key,
////                    value = m,
////                    postProcessingCallback = postProcessingCallback,
////                    context = context,
////                )
////            }
////        }
////    }
////}
////
////class NoopPartitioner : OutputPartitioner<StreamKey, DestinationRecordRaw,
////    StreamKey, HttpStepOutput<DestinationRecordRaw>> {
////    override fun getOutputKey(inputKey: StreamKey, output: HttpStepOutput<DestinationRecordRaw>):
////        StreamKey = StreamKey(stream = inputKey.stream)
////
////    override fun getPart(outputKey: StreamKey, inputPart: Int, numParts: Int): Int {
////        return inputPart
////    }
////}
////
////data class HttpStepOutput<T>(
////    override val state: BatchState,
////    val failedRecords: List<T> = emptyList(),
////) : WithBatchState
////
////class HttpPipelineStep(
////    override val numWorkers: Int,
////    private val outputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
////    private val taskFactory: LoadPipelineStepTaskFactory,
////) : LoadPipelineStep {
////    override fun taskForPartition(partition: Int): Task {
////        return taskFactory.createFirstStep(
////            batchAccumulator = HttpAccumulator(),
////            outputPartitioner = NoopPartitioner(),
////            outputQueue = FlattenQueueAdapter(outputQueue),
////            part = partition,
////            numWorkers = numWorkers,
////        )
////    }
////}
////
////data class HttpRequestState(
////    val records: MutableList<DestinationRecordRaw> = mutableListOf(),
////    val outputStream: ByteArrayOutputStream,
////    val printer: CSVPrinter,
////    override val state: BatchState,
////) : WithBatchState, AutoCloseable {
////    companion object {
////        fun new(): HttpRequestState {
////            val outputStream = ByteArrayOutputStream()
////            return HttpRequestState(
////                outputStream = outputStream,
////                printer = CSVPrinter(PrintWriter(outputStream, true, StandardCharsets.UTF_8), CSVFormat.DEFAULT.withQuoteMode(QuoteMode.NON_NUMERIC)),
////                state = BatchState.PROCESSED,
////            )
////        }
////    }
////
////    override fun close() {
////        KotlinLogging.logger {  }.warn { "close" }
////    }
////}
////
////class HttpAccumulator :
////BatchAccumulator<
////    HttpRequestState,
////    StreamKey,
////    DestinationRecordRaw,
////    HttpStepOutput<DestinationRecordRaw>,
////    >
////{
////    override suspend fun start(key: StreamKey, part: Int): HttpRequestState {
////        KotlinLogging.logger {  }.warn { "start $key $part" }
////        return HttpRequestState.new()
////    }
////
////    override suspend fun accept(
////        input: DestinationRecordRaw,
////        state: HttpRequestState,
////    ): BatchAccumulatorResult<HttpRequestState, HttpStepOutput<DestinationRecordRaw>> {
////        val schema = (input.schema as? ObjectType) ?: throw IllegalArgumentException("schema isn't on ObjectType")
////        state.records.add(input)
////        state.printer.printRecord((input.asDestinationRecordAirbyteValue().data as ObjectValue).toCsvRecord(schema))
////        state.printer.flush()
////        if (state.outputStream.size() > 100) {
////            // TODO check if upload was successful
//////            if (Random.nextBoolean()) {
//////                sendData(state)
//////                return FinalOutput(HttpStepOutput(BatchState.COMPLETE))
//////            }
////            return IntermediateOutput(HttpRequestState.new(), HttpStepOutput(BatchState.LOADED, state.records))
////        } else {
////            return NoOutput(state)
////        }
////    }
////
////    private fun sendData(state: HttpRequestState) {
////        KotlinLogging.logger {  }.error { "Sending data!" }
////        KotlinLogging.logger {  }.warn { "\n${state.outputStream}" }
////    }
////
////    override suspend fun finish(state: HttpRequestState): FinalOutput<HttpRequestState, HttpStepOutput<DestinationRecordRaw>> {
////        KotlinLogging.logger {  }.error { "Finish" }
////        sendData(state)
////        // TODO check if upload was successful
////        return FinalOutput(HttpStepOutput(BatchState.COMPLETE))
////    }
////}
