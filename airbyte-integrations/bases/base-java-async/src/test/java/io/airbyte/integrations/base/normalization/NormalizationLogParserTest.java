/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.normalization;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.integrations.destination.normalization.NormalizationLogParser;
import io.airbyte.protocol.models.AirbyteErrorTraceMessage;
import io.airbyte.protocol.models.AirbyteErrorTraceMessage.FailureType;
import io.airbyte.protocol.models.AirbyteLogMessage;
import io.airbyte.protocol.models.AirbyteLogMessage.Level;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class NormalizationLogParserTest {

  private NormalizationLogParser parser;

  @BeforeEach
  void setup() {
    parser = new NormalizationLogParser();
  }

  @Test
  void testWrapNonJsonLogs() {
    runTest(
        """
        foo
        bar
        [error] oh no
        asdf
        [error] qwer
        """,
        List.of(
            logMessage(Level.INFO, "foo"),
            logMessage(Level.INFO, "bar"),
            logMessage(Level.INFO, "[error] oh no"),
            logMessage(Level.INFO, "asdf"),
            logMessage(Level.INFO, "[error] qwer")),
        List.of(
            "[error] oh no",
            "[error] qwer"));
  }

  @Test
  void testWrapJsonLogs() {
    runTest(
        """
        {"code": "A001", "data": {"v": "=1.0.9"}, "invocation_id": "ed2017da-965d-406b-8fa1-07fb7c19fd14", "level": "info", "log_version": 1, "msg": "Running with dbt=1.0.9", "node_info": {}, "pid": 55, "thread_name": "MainThread", "ts": "2023-04-11T16:08:54.781886Z", "type": "log_line"}
        {"code": "A001", "data": {"v": "=1.0.9"}, "invocation_id": "ed2017da-965d-406b-8fa1-07fb7c19fd14", "level": "error", "log_version": 1, "msg": "oh no", "node_info": {}, "pid": 55, "thread_name": "MainThread", "ts": "2023-04-11T16:08:54.781886Z", "type": "log_line"}
        {"type": "TRACE", "trace": {"type": "ERROR", "emitted_at": 1.681766805198E12, "error": {"failure_type": "system_error", "message": "uh oh", "stack_trace": "normalization blew up", "internal_message": "normalization blew up with more detail"}}}
        """,
        List.of(
            logMessage(Level.INFO, "Running with dbt=1.0.9"),
            logMessage(Level.ERROR, "oh no"),
            new AirbyteMessage()
                .withType(Type.TRACE)
                .withTrace(new AirbyteTraceMessage()
                    .withType(AirbyteTraceMessage.Type.ERROR)
                    .withEmittedAt(1.681766805198E12)
                    .withError(new AirbyteErrorTraceMessage()
                        .withFailureType(FailureType.SYSTEM_ERROR)
                        .withMessage("uh oh")
                        .withStackTrace("normalization blew up")
                        .withInternalMessage("normalization blew up with more detail")))),
        List.of(
            "oh no"));
  }

  @Test
  void testWeirdLogs() {
    runTest(
        """
        null
        "null"
        {"msg": "message with no level", "type": "log_line"}
        {"level": "info", "type": "log_line"}
        {"level": "error", "type": "log_line"}
        """,
        List.of(
            logMessage(Level.INFO, "null"),
            logMessage(Level.INFO, "\"null\""),
            logMessage(Level.INFO, "{\n  \"msg\" : \"message with no level\",\n  \"type\" : \"log_line\"\n}"),
            logMessage(Level.INFO, ""),
            logMessage(Level.ERROR, "")),
        List.of(
            ""));
  }

  private void runTest(String rawLogs, List<AirbyteMessage> expectedMessages, List<String> expectedDbtErrors) {
    final List<AirbyteMessage> messages = parser.create(new BufferedReader(
        new InputStreamReader(
            new ByteArrayInputStream(
                rawLogs.getBytes(StandardCharsets.UTF_8)),
            StandardCharsets.UTF_8)))
        .toList();

    assertEquals(
        expectedMessages,
        messages);
    assertEquals(expectedDbtErrors, parser.getDbtErrors());
  }

  private AirbyteMessage logMessage(Level level, String message) {
    return new AirbyteMessage()
        .withType(Type.LOG)
        .withLog(new AirbyteLogMessage()
            .withLevel(level)
            .withMessage(message));
  }

}
