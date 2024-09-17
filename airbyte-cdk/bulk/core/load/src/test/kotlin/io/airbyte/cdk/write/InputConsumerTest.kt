/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.write

import io.airbyte.cdk.message.Deserializer
import io.airbyte.cdk.message.MessageQueueWriter
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Prototype
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.util.stream.Stream
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.ArgumentsProvider
import org.junit.jupiter.params.provider.ArgumentsSource

@MicronautTest
class InputConsumerTest {
    @Inject lateinit var consumerFactory: MockInputConsumerFactory

    @Singleton
    class MockDeserializer : Deserializer<String> {
        override fun deserialize(serialized: String): String {
            return serialized.reversed() + "!"
        }
    }

    @Prototype
    class MockMessageQueueWriter : MessageQueueWriter<String> {
        val collectedStrings = mutableListOf<String>()
        val collectedSizes = mutableListOf<Long>()

        override suspend fun publish(message: String, sizeBytes: Long) {
            collectedStrings.add(message)
            collectedSizes.add(sizeBytes)
        }
    }

    @Prototype
    class MockInputConsumerFactory(
        val testDeserializer: Deserializer<String>,
        val testMessageQueue: MessageQueueWriter<String>
    ) {
        fun make(testInput: List<String>): InputConsumer<String> {
            return object : DeserializingInputStreamConsumer<String> {
                override val log = KotlinLogging.logger {}
                override val inputStream = testInput.joinToString("\n").byteInputStream()
                override val deserializer = testDeserializer
                override val messageQueue = testMessageQueue
            }
        }

        fun getOutputCollector(): MockMessageQueueWriter {
            return testMessageQueue as MockMessageQueueWriter
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
        val consumer = consumerFactory.make(testInput)
        consumer.run()
        Assertions.assertEquals(
            testInput.filter { it != "" }.map { it.reversed() + "!" },
            consumerFactory.getOutputCollector().collectedStrings
        )
        Assertions.assertEquals(
            testInput.filter { it != "" }.map { it.length.toLong() },
            consumerFactory.getOutputCollector().collectedSizes
        )
    }
}
