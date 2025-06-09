/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.http.decoder

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

val JSON_CONTENT: String = """
{
  "field": "value"
}
"""

class JsonDecoderTest {

    private lateinit var decoder: JsonDecoder

    @BeforeEach
    fun setup() {
        decoder = JsonDecoder()
    }

    @Test
    internal fun `test given valid json when decode then return json object`() {
        val jsonBody = decoder.decode(JSON_CONTENT.byteInputStream())

        Assertions.assertEquals(
            mapOf<String, JsonNode>("field" to Jsons.textNode("value")),
            jsonBody.fields().asSequence().associate { it.key to it.value }
        )
    }
}
