package io.airbyte.cdk.load.writer

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.http.HttpRequester
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.load.write.dlq.DlqLoader
import io.github.oshai.kotlinlogging.KotlinLogging


private val logger = KotlinLogging.logger {}


class StreamIdentifier(private val destinationObjectName: String, private val operation: ImportType) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false

        other as StreamIdentifier

        if (destinationObjectName != other.destinationObjectName) return false
        if (operation != other.operation) return false

        return true
    }

    override fun hashCode(): Int {
        var result = destinationObjectName.hashCode()
        result = 31 * result + operation.hashCode()
        return result
    }

    override fun toString(): String {
        return "StreamIdentifier(destinationObjectName='$destinationObjectName', operation=$operation)"
    }
}

// FIXME this constructor is very focused on batch stuff and therefore there will probably be a need for an interface
class DeclarativeLoaderStateFactory(private val httpRequester: HttpRequester, private val batchSizeTypeStrategyFactory: BatchSizeStrategyFactory, private val entryAssembler: DeclarativeBatchEntryAssembler, private val batchField: List<String>) {
    fun create(): DeclarativeLoaderState {
        return DeclarativeLoaderState(httpRequester, JsonResponseBodyBuilder(batchSizeTypeStrategyFactory, entryAssembler, batchField))
    }
}


class DeclarativeLoader(
    private val loaderStateFactoryByDestinationOperation: Map<StreamIdentifier, DeclarativeLoaderStateFactory>,
    private val catalog: DestinationCatalog
) : DlqLoader<DeclarativeLoaderState> {
    override fun start(key: StreamKey, part: Int): DeclarativeLoaderState {
        logger.info { "DeclarativeLoader.start for ${key.serializeToString()} with part $part" }
        val streamIdentifier = extractStreamIdentifier(key)
        return loaderStateFactoryByDestinationOperation[streamIdentifier]?.create() ?: throw IllegalStateException("Could not find loader for stream $streamIdentifier")
    }

    private fun extractStreamIdentifier(key: StreamKey): StreamIdentifier {
        val stream =
            (catalog.streams.find { it.mappedDescriptor == key.stream }
                ?: throw IllegalStateException(
                    "Could not find stream ${key.stream} as part of the catalog.",
                ))

        val streamIdentifier = StreamIdentifier(
            stream.destinationObjectName
                ?: throw IllegalStateException("Stream ${key.stream} does not have a destinationObjectName."),
            stream.importType,
        )
        return streamIdentifier
    }

    override fun accept(
        record: DestinationRecordRaw,
        state: DeclarativeLoaderState
    ): DlqLoader.DlqLoadResult {
        state.accumulate(record)
        if (state.isFull()) {
            val failedRecords = state.flush()
            return DlqLoader.Complete(failedRecords)
        } else {
            return DlqLoader.Incomplete
        }
    }

    override fun finish(state: DeclarativeLoaderState): DlqLoader.Complete =
        DlqLoader.Complete(state.flush())

    override fun close() {}

}
