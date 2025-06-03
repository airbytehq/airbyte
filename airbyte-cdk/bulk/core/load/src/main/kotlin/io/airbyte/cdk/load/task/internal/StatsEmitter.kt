package io.airbyte.cdk.load.task.internal

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.OnEndOfSync
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import kotlinx.coroutines.delay

@Singleton
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "SOCKET")
class StatsEmitter(
    private val syncManager: SyncManager,
    private val catalog: DestinationCatalog,
    private val outputConsumer: DummyStatsMessageConsumer,
) : Task {

    companion object {
        private const val DEST_EMITTED_RECORDS_COUNT = "emittedRecordsCount"
        private const val DEST_EMITTED_BYTES_COUNT = "emittedBytesCount"
        private val EMPTY_JSON = Jsons.emptyObject()
        private val EMISSION_FREQUENCY_IN_MILLIS = java.time.Duration.ofMinutes(1).toMillis()
    }

    override val terminalCondition: TerminalCondition = OnEndOfSync

    override suspend fun execute() {
        while (true) {
            catalog.streams.forEach {
                val manager = syncManager.getStreamManager(it.descriptor)
                val recordsRead = manager.readCount()
                val bytesRead = manager.byteCount()

                // TODO: Think about namespace mapping
                val dummyMessage =
                    AirbyteMessage()
                        .withType(AirbyteMessage.Type.RECORD)
                        .withRecord(
                            AirbyteRecordMessage()
                                .withNamespace(it.descriptor.namespace)
                                .withStream(it.descriptor.name)
                                .withData(EMPTY_JSON)
                                .withAdditionalProperty(DEST_EMITTED_RECORDS_COUNT, recordsRead)
                                .withAdditionalProperty(DEST_EMITTED_BYTES_COUNT, bytesRead),
                        )

                outputConsumer.invoke(dummyMessage)
                delay(EMISSION_FREQUENCY_IN_MILLIS)
            }
        }
    }
}

@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "message is guaranteed to be non-null by Kotlin's type system",
)
@Singleton
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "SOCKET")
class DummyStatsMessageConsumer(private val consumer: OutputConsumer) :
    suspend (AirbyteMessage) -> Unit {
    override suspend fun invoke(message: AirbyteMessage) {
        consumer.accept(message)
    }
}
