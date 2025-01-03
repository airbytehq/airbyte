import com.google.common.collect.Range
import io.netty.channel.ChannelId
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.*
import kotlinx.serialization.json.internal.writeJson

// Dev interface
interface Batch
interface BatchAccumulator<T, U: Batch> {
    suspend fun accumulate(flow: Flow<T>): U
}

// Dev / toolkit-builder impl
class MyWriter(val size: Long = 0) {
    fun accept(record: Record) {
        // ...
    }
    fun flush() {
        // ...
    }
    fun takeBytes(): ByteArray = byteArrayOf()
}

data class Record(val endOfStream: Boolean = false)
data class Part(val bytes: ByteArray): Batch
class MyDestinationBatchAccumulator: BatchAccumulator<Record, Part> {
    companion object { const val MY_PART_SIZE = 1024L }
    override suspend fun accumulate(flow: Flow<Record>): Part {
        val writer = MyWriter()
        flow.takeWhile { writer.size <= MY_PART_SIZE }.collect { record ->
            writer.accept(record)
        }
        writer.flush()
        return Part(writer.takeBytes())
    }
}

// CDK Internal

data class BatchWithMeta<T: Batch>(val batch: T)
class ProcessRecordsTask<T: Batch>(
    val inputQueue: Channel<Record>,
    val outputQueue: Channel<BatchWithMeta<T>>,
    val accumulator: BatchAccumulator<Record, T>
) {
    suspend fun channel() {
        var remainingFlow = inputQueue.consumeAsFlow()
        do {
            val (startRecord, thisFlow) = remainingFlow.peek()
            if (startRecord == null) {
                break
            }
            val batch = accumulator.accumulate(thisFlow)
            val (nextRecord, nextFlow) = inputQueue.consumeAsFlow().peek()
            outputQueue.send(BatchWithMeta(batch))
            remainingFlow = nextFlow
        } while (nextRecord != null)
    }
}

suspend fun <T> Flow<T>.peek(): Pair<T?, Flow<T>> {
    val first = this.firstOrNull()
    if (first == null) {
        return Pair(null, emptyFlow())
    }
    return Pair(first, flowOf(first) + this)
}
