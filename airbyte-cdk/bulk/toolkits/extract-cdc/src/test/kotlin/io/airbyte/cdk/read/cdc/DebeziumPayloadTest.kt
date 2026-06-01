/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.read.cdc

import com.fasterxml.jackson.core.JsonFactory
import com.fasterxml.jackson.core.StreamReadConstraints
import com.fasterxml.jackson.core.exc.StreamConstraintsException
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class DebeziumPayloadTest {

    /**
     * Reproduces oncall#12768 at the unit level: when the underlying Jackson parser hits a
     * [StreamConstraintsException] while reading a Debezium event payload, the wrapping logic in
     * [readDebeziumPayload] must surface a [SystemErrorException] with an actionable message that
     * does not leak Jackson class names.
     */
    @Test
    fun readDebeziumPayload_wraps_StreamConstraintsException_with_actionable_message() {
        val tinyConstraints = StreamReadConstraints.builder().maxStringLength(8).build()
        val tinyFactory = JsonFactory().setStreamReadConstraints(tinyConstraints)
        val tinyMapper = ObjectMapper(tinyFactory)
        val oversizedValue = "x".repeat(64)
        val raw = "{\"after\":{\"col\":\"$oversizedValue\"}}"
        val tinyParser: (String) -> JsonNode = { tinyMapper.readTree(it) }

        val translated =
            Assertions.assertThrows(SystemErrorException::class.java) {
                readDebeziumPayload(raw, "value", tinyParser)
            }

        Assertions.assertTrue(
            translated.message!!.contains("CDC event payload exceeds"),
            "Expected actionable message; got: ${translated.message}",
        )
        Assertions.assertTrue(
            translated.message!!.contains("CDC replication"),
            "Expected remediation hint; got: ${translated.message}",
        )
        Assertions.assertTrue(
            translated.message!!.contains("Debezium event part: value"),
            "Expected payload-part identifier; got: ${translated.message}",
        )
        Assertions.assertFalse(
            translated.message!!.contains("StreamReadConstraints") ||
                translated.message!!.contains("StreamConstraintsException"),
            "User-facing message must not leak Jackson class names; got: ${translated.message}",
        )
        val chain = generateSequence(translated.cause) { it.cause }.toList()
        Assertions.assertTrue(
            chain.any { it is StreamConstraintsException },
            "Original StreamConstraintsException must be preserved in cause chain.",
        )
    }

    /**
     * Unrelated parse failures should NOT raise the "row exceeds limit" error; they should fall
     * through to the existing null-event behaviour so a single malformed event does not abort the
     * CDC stream.
     */
    @Test
    fun readDebeziumPayload_returns_null_on_unrelated_parse_failures() {
        val failingParser: (String) -> JsonNode = {
            throw RuntimeException("unrelated parse failure")
        }
        val result = readDebeziumPayload("{}", "value", failingParser)
        Assertions.assertNull(result)
    }

    /** Happy path: a well-formed payload must be deserialized normally. */
    @Test
    fun readDebeziumPayload_returns_jsonNode_on_success() {
        val node = readDebeziumPayload("{\"op\":\"c\"}", "value", Jsons::readTree)
        Assertions.assertEquals("c", node!!.get("op").asText())
    }
}
