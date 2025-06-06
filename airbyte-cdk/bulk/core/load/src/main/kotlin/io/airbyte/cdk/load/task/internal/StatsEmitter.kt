/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

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
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.annotation.Nullable
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.delay

private const val STATS_FREQ_QUALIFIER = "statsEmissionFrequencyOverride"
private const val DEFAULT_DELAY_MS = 60_000L

@Singleton
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "SOCKET")
class StatsEmitter(
    private val syncManager: SyncManager,
    private val catalog: DestinationCatalog,
    private val outputConsumer: DummyStatsMessageConsumer,
    @Nullable @Named(STATS_FREQ_QUALIFIER) private val emissionFrequencyMillis: Long? = null
) : Task {
    private val freq: Long = emissionFrequencyMillis ?: DEFAULT_DELAY_MS

    companion object {
        private const val DEST_EMITTED_RECORDS_COUNT = "emittedRecordsCount"
        private const val DEST_EMITTED_BYTES_COUNT = "emittedBytesCount"
        private val EMPTY_JSON = Jsons.emptyObject()
    }

    override val terminalCondition: TerminalCondition = OnEndOfSync

    override suspend fun execute() {
        while (true) {
            catalog.streams.forEach { stream ->
                val manager = syncManager.getStreamManager(stream.descriptor)

                if (manager.receivedStreamComplete()) return@forEach

                val recordsRead = manager.readCount()
                val bytesRead = manager.byteCount()

                // TODO: Think about namespace mapping
                val statsMessage =
                    AirbyteMessage()
                        .withType(AirbyteMessage.Type.RECORD)
                        .withRecord(
                            AirbyteRecordMessage()
                                .withNamespace(stream.unmappedNamespace)
                                .withStream(stream.unmappedName)
                                .withData(EMPTY_JSON)
                                .withAdditionalProperty(OutputConsumer.IS_DUMMY_STATS_MESSAGE, true)
                                .withAdditionalProperty(DEST_EMITTED_RECORDS_COUNT, recordsRead)
                                .withAdditionalProperty(DEST_EMITTED_BYTES_COUNT, bytesRead),
                        )

                outputConsumer.invoke(statsMessage)
            }
            delay(freq)
        }
    }
}

@Factory
class FrequencyFactory {
    @Singleton
    @Named(STATS_FREQ_QUALIFIER)
    fun statsEmissionFrequency(
        @Value("\${airbyte.stats.emission-frequency-ms:$DEFAULT_DELAY_MS}") millis: Long
    ): Long = millis
}

@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "message is guaranteed to be non-null by Kotlin's type system",
)
@Singleton
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "SOCKET")
class DummyStatsMessageConsumer(private val consumer: OutputConsumer) :
    suspend (AirbyteMessage) -> Unit {
    private val log = KotlinLogging.logger {}
    override suspend fun invoke(message: AirbyteMessage) {
        consumer.accept(message)
    }
}
