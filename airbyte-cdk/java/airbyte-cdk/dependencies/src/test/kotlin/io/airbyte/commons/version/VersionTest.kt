/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.version

import io.airbyte.commons.json.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class VersionTest {
    @Test
    fun testJsonSerializationDeserialization() {
        val jsonString =
            """
                              {"version": "1.2.3"}
                              
                              """.trimIndent()
        val expectedVersion = Version("1.2.3")

        val deserializedVersion = Jsons.deserialize(jsonString, Version::class.java)
        Assertions.assertEquals(expectedVersion, deserializedVersion)

        val deserializedVersionLoop =
            Jsons.deserialize(Jsons.serialize(deserializedVersion), Version::class.java)
        Assertions.assertEquals(expectedVersion, deserializedVersionLoop)
    }
}
