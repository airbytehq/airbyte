/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command

import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.micronaut.context.RuntimeBeanDefinition
import java.io.ByteArrayOutputStream
import java.io.OutputStream
import java.io.PrintStream

/** Used by [CliRunner] to populate a [BufferingOutputConsumer] instance. */
class CliRunnerOutputStream : OutputStream() {

    val results = BufferingOutputConsumer(ClockFactory().fixed())
    private val lineStream = ByteArrayOutputStream()
    private val printStream = PrintStream(this, true, Charsets.UTF_8)

    val beanDefinition: RuntimeBeanDefinition<PrintStream> =
        RuntimeBeanDefinition.builder(PrintStream::class.java) { printStream }
            .singleton(true)
            .build()

    override fun write(b: Int) {
        if (b == '\n'.code) {
            readLine()
        } else {
            lineStream.write(b)
        }
    }

    override fun close() {
        readLine()
        lineStream.close()
        results.close()
        super.close()
    }

    private fun readLine() {
        val line: String = lineStream.toString(Charsets.UTF_8).trim()
        lineStream.reset()
        if (line.isNotBlank()) {
            results.accept(Jsons.readValue(line, AirbyteMessage::class.java))
        }
    }
}
