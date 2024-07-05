/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import java.io.ByteArrayOutputStream
import java.io.PrintStream
import java.nio.charset.StandardCharsets
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito

class AirbyteTraceMessageUtilityTest {
    var originalOut: PrintStream = System.out
    private val outContent = ByteArrayOutputStream()

    @BeforeEach
    fun setUpOut() {
        System.setOut(PrintStream(outContent, true, StandardCharsets.UTF_8))
    }

    private fun assertJsonNodeIsTraceMessage(jsonNode: JsonNode) {
        // todo: this check could be better by actually trying to convert the JsonNode to an
        // AirbyteTraceMessage instance
        Assertions.assertEquals("TRACE", jsonNode["type"].asText())
        Assertions.assertNotNull(jsonNode["trace"])
    }

    @Test
    fun testEmitSystemErrorTrace() {
        AirbyteTraceMessageUtility.emitSystemErrorTrace(
            Mockito.mock(RuntimeException::class.java),
            "this is a system error"
        )
        val outJson = Jsons.deserialize(outContent.toString(StandardCharsets.UTF_8))
        assertJsonNodeIsTraceMessage(outJson)
        Assertions.assertEquals("system_error", outJson["trace"]["error"]["failure_type"].asText())
    }

    @Test
    fun testEmitConfigErrorTrace() {
        AirbyteTraceMessageUtility.emitConfigErrorTrace(
            Mockito.mock(RuntimeException::class.java),
            "this is a config error"
        )
        val outJson = Jsons.deserialize(outContent.toString(StandardCharsets.UTF_8))
        assertJsonNodeIsTraceMessage(outJson)
        Assertions.assertEquals("config_error", outJson["trace"]["error"]["failure_type"].asText())
    }

    @Test
    fun testEmitErrorTrace() {
        AirbyteTraceMessageUtility.emitErrorTrace(
            Mockito.mock(RuntimeException::class.java),
            "this is an error",
            AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR
        )
        assertJsonNodeIsTraceMessage(Jsons.deserialize(outContent.toString(StandardCharsets.UTF_8)))
    }

    @Test
    fun testCorrectStacktraceFormat() {
        try {
            val x = 1 / 0
        } catch (e: Exception) {
            AirbyteTraceMessageUtility.emitSystemErrorTrace(e, "you exploded the universe")
        }
        val outJson = Jsons.deserialize(outContent.toString(StandardCharsets.UTF_8))
        Assertions.assertTrue(outJson["trace"]["error"]["stack_trace"].asText().contains("\n\tat"))
    }

    @AfterEach
    fun revertOut() {
        System.setOut(originalOut)
    }
}
