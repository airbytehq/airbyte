/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base.normalization

import io.airbyte.cdk.integrations.destination.normalization.NormalizationLogParser
import io.airbyte.protocol.models.AirbyteErrorTraceMessage
import io.airbyte.protocol.models.AirbyteLogMessage
import io.airbyte.protocol.models.AirbyteMessage
import io.airbyte.protocol.models.AirbyteTraceMessage
import java.io.BufferedReader
import java.io.ByteArrayInputStream
import java.io.InputStreamReader
import java.nio.charset.StandardCharsets
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class NormalizationLogParserTest {
    private var parser: NormalizationLogParser? = null

    @BeforeEach
    fun setup() {
        parser = NormalizationLogParser()
    }

    @Test
    fun testWrapNonJsonLogs() {
        runTest(
            """
        foo
        bar
        [error] oh no
        asdf
        [error] qwer
        
        """.trimIndent(),
            java.util.List.of(
                logMessage(AirbyteLogMessage.Level.INFO, "foo"),
                logMessage(AirbyteLogMessage.Level.INFO, "bar"),
                logMessage(AirbyteLogMessage.Level.INFO, "[error] oh no"),
                logMessage(AirbyteLogMessage.Level.INFO, "asdf"),
                logMessage(AirbyteLogMessage.Level.INFO, "[error] qwer")
            ),
            listOf("[error] oh no", "[error] qwer")
        )
    }

    @Test
    fun testWrapJsonLogs() {
        runTest(
            """
        {"code": "A001", "data": {"v": "=1.0.9"}, "invocation_id": "ed2017da-965d-406b-8fa1-07fb7c19fd14", "level": "info", "log_version": 1, "msg": "Running with dbt=1.0.9", "node_info": {}, "pid": 55, "thread_name": "MainThread", "ts": "2023-04-11T16:08:54.781886Z", "type": "log_line"}
        {"code": "A001", "data": {"v": "=1.0.9"}, "invocation_id": "ed2017da-965d-406b-8fa1-07fb7c19fd14", "level": "error", "log_version": 1, "msg": "oh no", "node_info": {}, "pid": 55, "thread_name": "MainThread", "ts": "2023-04-11T16:08:54.781886Z", "type": "log_line"}
        {"type": "TRACE", "trace": {"type": "ERROR", "emitted_at": 1.681766805198E12, "error": {"failure_type": "system_error", "message": "uh oh", "stack_trace": "normalization blew up", "internal_message": "normalization blew up with more detail"}}}
        
        """.trimIndent(),
            java.util.List.of(
                logMessage(AirbyteLogMessage.Level.INFO, "Running with dbt=1.0.9"),
                logMessage(AirbyteLogMessage.Level.ERROR, "oh no"),
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.TRACE)
                    .withTrace(
                        AirbyteTraceMessage()
                            .withType(AirbyteTraceMessage.Type.ERROR)
                            .withEmittedAt(1.681766805198E12)
                            .withError(
                                AirbyteErrorTraceMessage()
                                    .withFailureType(
                                        AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR
                                    )
                                    .withMessage("uh oh")
                                    .withStackTrace("normalization blew up")
                                    .withInternalMessage("normalization blew up with more detail")
                            )
                    )
            ),
            listOf("oh no")
        )
    }

    @Test
    fun testWeirdLogs() {
        runTest(
            """
        null
        "null"
        {"msg": "message with no level", "type": "log_line"}
        {"level": "info", "type": "log_line"}
        {"level": "error", "type": "log_line"}
        
        """.trimIndent(),
            java.util.List.of(
                logMessage(AirbyteLogMessage.Level.INFO, "null"),
                logMessage(AirbyteLogMessage.Level.INFO, "\"null\""),
                logMessage(
                    AirbyteLogMessage.Level.INFO,
                    "{\n  \"msg\" : \"message with no level\",\n  \"type\" : \"log_line\"\n}"
                ),
                logMessage(AirbyteLogMessage.Level.INFO, ""),
                logMessage(AirbyteLogMessage.Level.ERROR, "")
            ),
            listOf("")
        )
    }

    private fun runTest(
        rawLogs: String,
        expectedMessages: List<AirbyteMessage>,
        expectedDbtErrors: List<String>
    ) {
        val messages =
            parser!!
                .create(
                    BufferedReader(
                        InputStreamReader(
                            ByteArrayInputStream(rawLogs.toByteArray(StandardCharsets.UTF_8)),
                            StandardCharsets.UTF_8
                        )
                    )
                )
                .toList()

        Assertions.assertEquals(expectedMessages, messages)
        Assertions.assertEquals(expectedDbtErrors, parser!!.dbtErrors)
    }

    private fun logMessage(level: AirbyteLogMessage.Level, message: String): AirbyteMessage {
        return AirbyteMessage()
            .withType(AirbyteMessage.Type.LOG)
            .withLog(AirbyteLogMessage().withLevel(level).withMessage(message))
    }
}
