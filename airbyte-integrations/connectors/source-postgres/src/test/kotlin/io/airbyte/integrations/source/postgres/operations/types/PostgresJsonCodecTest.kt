/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.operations.types

import io.airbyte.cdk.util.Jsons
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class PostgresJsonCodecTest {

    @Test
    fun `decodes the JSON text Debezium hands over`() {
        for (text in listOf("""{"k": [1, "a"]}""", "[1, 2]", "\"s\"", "42", "true", "null")) {
            val decoded = PostgresJsonCodec.decode(Jsons.textNode(text))

            assertEquals(text, decoded)
            assertEquals(Jsons.readTree(text), PostgresJsonCodec.encode(decoded))
        }
    }

    @Test
    fun `decodes structured nodes to their JSON text`() {
        val node = Jsons.readTree("""{"k":[1,"a"]}""")

        assertEquals("""{"k":[1,"a"]}""", PostgresJsonCodec.decode(node))
    }

    @Test
    fun `encodes the JSON text JDBC returns as a JSON value`() {
        assertEquals(Jsons.readTree("""{"k":null}"""), PostgresJsonCodec.encode("""{"k": null}"""))
        assertEquals(Jsons.textNode("a"), PostgresJsonCodec.encode("\"a\""))
    }
}
