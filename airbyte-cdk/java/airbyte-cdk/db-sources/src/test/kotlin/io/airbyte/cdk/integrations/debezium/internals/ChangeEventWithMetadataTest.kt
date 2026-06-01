/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import com.fasterxml.jackson.core.JsonFactory
import com.fasterxml.jackson.core.StreamReadConstraints
import com.fasterxml.jackson.core.exc.StreamConstraintsException
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.commons.json.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class ChangeEventWithMetadataTest {

    /**
     * Reproduces oncall#12768 at the unit level: when the configured Jackson parser hits a
     * [StreamConstraintsException] while reading a Debezium event payload, the wrapping logic in
     * [ChangeEventWithMetadata.parseDebeziumPayload] must surface an actionable [RuntimeException]
     * that names the connector-level limit and the remediation, without leaking Jackson class
     * names.
     *
     * A tiny [ObjectMapper] is injected as the parser so the constraint trips with a small input —
     * the production [Jsons] mapper now allows arbitrarily large strings and would not trip without
     * a multi-gigabyte payload.
     */
    @Test
    fun parseDebeziumPayload_wraps_StreamConstraintsException_with_actionable_message() {
        val tinyConstraints = StreamReadConstraints.builder().maxStringLength(8).build()
        val tinyFactory = JsonFactory().setStreamReadConstraints(tinyConstraints)
        val tinyMapper = ObjectMapper(tinyFactory)
        val oversizedValue = "x".repeat(64)
        val raw = "{\"after\":{\"col\":\"$oversizedValue\"}}"
        // The production code wraps Jackson IOExceptions in a RuntimeException
        // (see Jsons.deserialize). Mimic the same shape here.
        val mimicJsonsParser: (String) -> JsonNode = { tinyMapper.readTree(it) }

        val translated =
            Assertions.assertThrows(RuntimeException::class.java) {
                ChangeEventWithMetadata.parseDebeziumPayload(raw, "value", mimicJsonsParser)
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
        // The original cause chain (containing the Jackson exception) must be preserved for logs.
        val chain = generateSequence(translated.cause) { it.cause }.toList()
        Assertions.assertTrue(
            chain.any { it is StreamConstraintsException },
            "Original StreamConstraintsException must be preserved in cause chain.",
        )
    }

    /**
     * A generic JSON parse failure (no [StreamConstraintsException] in the cause chain) must be
     * rethrown unchanged. The "row exceeds limit" branch must not fire for unrelated parse errors.
     */
    @Test
    fun parseDebeziumPayload_does_not_wrap_unrelated_parse_failures() {
        val failingParser: (String) -> JsonNode = {
            throw RuntimeException("unrelated parse failure")
        }
        val rethrown =
            Assertions.assertThrows(RuntimeException::class.java) {
                ChangeEventWithMetadata.parseDebeziumPayload("{}", "value", failingParser)
            }
        Assertions.assertEquals("unrelated parse failure", rethrown.message)
        Assertions.assertFalse(
            rethrown.message!!.contains("CDC event payload exceeds"),
            "Unrelated parse failures must not be re-wrapped with the row-too-large message.",
        )
    }

    /**
     * The happy path: a well-formed payload that fits within the configured limit must be
     * deserialized normally.
     */
    @Test
    fun parseDebeziumPayload_returns_jsonNode_on_success() {
        val node =
            ChangeEventWithMetadata.parseDebeziumPayload(
                "{\"op\":\"c\"}",
                "value",
                Jsons::deserialize,
            )
        Assertions.assertEquals("c", node.get("op").asText())
    }
}
