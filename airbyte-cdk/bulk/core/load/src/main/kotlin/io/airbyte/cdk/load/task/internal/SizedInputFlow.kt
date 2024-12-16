/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.message.Deserializer
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.io.InputStream
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.FlowCollector

interface SizedInputFlow<T> : Flow<Pair<Long, T>>

abstract class ReservingDeserializingInputFlow<T : Any> : SizedInputFlow<Reserved<T>> {
    val log = KotlinLogging.logger {}

    abstract val config: DestinationConfiguration
    abstract val deserializer: Deserializer<T>
    abstract val memoryManager: ReservationManager
    abstract val inputStream: InputStream

    override suspend fun collect(collector: FlowCollector<Pair<Long, Reserved<T>>>) {
        log.info {
            "Reserved ${memoryManager.totalCapacityBytes/1024}mb memory for input processing"
        }

        inputStream.bufferedReader().lineSequence().forEachIndexed { index, line ->
            if (line.isEmpty()) {
                return@forEachIndexed
            }

            val lineSize = line.length.toLong()
            val estimatedSize = lineSize * config.estimatedRecordMemoryOverheadRatio
            val reserved = memoryManager.reserve(estimatedSize.toLong(), line)
            val message = deserializer.deserialize(line)
            collector.emit(Pair(lineSize, reserved.replace(message)))

            if (index % 10_000 == 0) {
                log.info { "Processed $index lines" }
            }
        }

        log.info { "Finished processing input" }
    }
}

@Singleton
class DefaultInputFlow(
    override val config: DestinationConfiguration,
    override val deserializer: Deserializer<DestinationMessage>,
    @Named("memoryManager") override val memoryManager: ReservationManager,
    override val inputStream: InputStream
) : ReservingDeserializingInputFlow<DestinationMessage>()
