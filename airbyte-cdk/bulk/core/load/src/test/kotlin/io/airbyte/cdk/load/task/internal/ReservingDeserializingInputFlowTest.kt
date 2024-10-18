/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.message.Deserializer
import io.airbyte.cdk.load.state.MemoryManager
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.io.InputStream
import java.util.stream.Stream
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.ArgumentsProvider
import org.junit.jupiter.params.provider.ArgumentsSource

@MicronautTest(
    rebuildContext = true,
    environments =
        [
            "ReservingDeserializingInputFlowTest",
            "MockDestinationCatalog",
            "MockDestinationConfiguration"
        ],
)
class ReservingDeserializingInputFlowTest {
    @Inject lateinit var config: DestinationConfiguration
    @Inject lateinit var inputFlow: ReservingDeserializingInputFlow<String>
    @Inject lateinit var inputStream: MockInputStream

    @Singleton
    @Primary
    @Requires(env = ["ReservingDeserializingInputFlowTest"])
    class MockInputFlow(
        override val config: DestinationConfiguration,
        override val inputStream: InputStream,
        override val deserializer: Deserializer<String>,
        override val memoryManager: MemoryManager,
    ) : ReservingDeserializingInputFlow<String>()

    @Singleton
    @Primary
    @Requires(env = ["ReservingDeserializingInputFlowTest"])
    class MockDeserializer : Deserializer<String> {
        override fun deserialize(serialized: String): String {
            return serialized.reversed() + "!"
        }
    }

    @Singleton
    @Primary
    @Requires(env = ["ReservingDeserializingInputFlowTest"])
    class MockInputStream : InputStream() {
        val chars = mutableListOf<Char>()

        fun load(lines: List<String>) {
            lines.forEach { line ->
                chars.addAll(line.toList())
                chars.add('\n')
            }
        }

        override fun read(): Int {
            return if (chars.isEmpty()) {
                -1
            } else {
                chars.removeAt(0).code
            }
        }
    }

    class InputConsumerTestArgumentsProvider : ArgumentsProvider {
        override fun provideArguments(context: ExtensionContext): Stream<out Arguments> {
            return Stream.of(
                Arguments.of(listOf("cat", "dog", "turtle")),
                Arguments.of(listOf("", "109j321dcDASD", "2023", "1", "2", "3"))
            )
        }
    }

    @ParameterizedTest
    @ArgumentsSource(InputConsumerTestArgumentsProvider::class)
    fun testInputConsumer(testInput: List<String>) = runTest {
        inputStream.load(testInput)
        val inputs = inputFlow.toList()
        Assertions.assertEquals(
            testInput.filter { it != "" }.map { it.reversed() + "!" },
            inputs.map { it.second.value }.toList()
        )
        Assertions.assertEquals(
            testInput.filter { it != "" }.map { it.length.toLong() },
            inputs.map { it.first }.toList()
        )
        Assertions.assertEquals(
            testInput
                .filter { it != "" }
                .map { (it.length.toLong() * config.estimatedRecordMemoryOverheadRatio).toLong() }
                .toList(),
            inputs.map { it.second.bytesReserved }.toList()
        )
    }
}
