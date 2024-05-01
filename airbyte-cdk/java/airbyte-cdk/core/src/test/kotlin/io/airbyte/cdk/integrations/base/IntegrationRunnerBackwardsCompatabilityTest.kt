/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import java.io.*
import java.nio.charset.StandardCharsets
import java.util.*
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class IntegrationRunnerBackwardsCompatabilityTest {
    @Test
    @Throws(Exception::class)
    fun testByteArrayInputStreamVersusScanner() {
        val testInputs =
            arrayOf(
                "This is line 1\nThis is line 2\nThis is line 3",
                "This is line 1\n\nThis is line 2\n\n\nThis is line 3",
                "This is line 1\rThis is line 2\nThis is line 3\r\nThis is line 4",
                "This is line 1 with emoji 😊\nThis is line 2 with Greek characters: Α, Β, Χ\nThis is line 3 with Cyrillic characters: Д, Ж, З",
                "This is a very long line that contains a lot of characters...",
                "This is line 1 with an escaped newline \\n character\nThis is line 2 with another escaped newline \\n character",
                "This is line 1\n\n",
                "\nThis is line 2",
                "\n"
            )

        for (testInput in testInputs) {
            // get new output
            val stream1: InputStream =
                ByteArrayInputStream(testInput.toByteArray(StandardCharsets.UTF_8))
            val consumer2 = MockConsumer()
            IntegrationRunner.consumeWriteStream(consumer2, stream1)
            val newOutput = consumer2.getOutput()

            // get old output
            val oldOutput: MutableList<String> = ArrayList()
            val stream2: InputStream =
                ByteArrayInputStream(testInput.toByteArray(StandardCharsets.UTF_8))
            val scanner = Scanner(stream2, StandardCharsets.UTF_8).useDelimiter("[\r\n]+")
            while (scanner.hasNext()) {
                oldOutput.add(scanner.next())
            }

            Assertions.assertEquals(oldOutput, newOutput)
        }
    }

    private class MockConsumer : SerializedAirbyteMessageConsumer {
        private val output: MutableList<String> = ArrayList()

        override fun start() {}

        override fun accept(message: String, sizeInBytes: Int) {
            output.add(message)
        }

        override fun close() {}

        fun getOutput(): List<String> {
            return ArrayList(output)
        }
    }
}
