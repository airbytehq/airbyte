/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.AirbyteCatalog
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Isolated

/** DISCOVER must produce the legacy catalog (`airbyte/source-slack:3.2.24 discover`) exactly. */
/** Runs alone: the fake server, its request log and the system properties are shared state. */
@Isolated
class SlackSourceDiscoverTest {

    @Test
    fun testCatalogEqualsLegacyCatalog() {
        val actual: AirbyteCatalog = SlackTestSupport.discover(server)
        val expected: JsonNode = Jsons.readTree(ResourceUtils.readResource("legacy-catalog.json"))
        java.io.File("build").mkdirs()
        java.io
            .File("build/actual-catalog.json")
            .writeText(
                Jsons.writerWithDefaultPrettyPrinter()
                    .writeValueAsString(sortStreams(Jsons.valueToTree(actual)))
            )
        Assertions.assertEquals(sortStreams(expected), sortStreams(Jsons.valueToTree(actual)))
        // Discovery is static: no Slack call is needed.
        Assertions.assertTrue(
            server.requests.none { it.method != "auth.test" },
            "unexpected requests: ${server.requests}"
        )
    }

    /**
     * Streams in name order, and without an empty `default_cursor_field`: the protocol model
     * defaults the property to an empty list when a catalog is parsed back (the in-process runner
     * does that), while the legacy connector's output simply lacks the key.
     */
    private fun sortStreams(catalog: JsonNode): JsonNode {
        val copy: ObjectNode = catalog.deepCopy()
        val streams: List<JsonNode> =
            copy["streams"]
                .map { stream: JsonNode ->
                    (stream.deepCopy() as ObjectNode).also {
                        if (it["default_cursor_field"]?.isEmpty == true)
                            it.remove("default_cursor_field")
                    }
                }
                .sortedBy { it["name"].asText() }
        copy.set<JsonNode>("streams", Jsons.arrayNode().addAll(streams) as ArrayNode)
        return copy
    }

    companion object {
        lateinit var server: FakeSlackServer

        @JvmStatic
        @BeforeAll
        fun startServer() {
            server = FakeSlackServer(FakeSlackData.generate(messagesPerChannel = 3)).start()
        }

        @JvmStatic
        @AfterAll
        fun stopServer() {
            server.stop()
        }
    }
}
