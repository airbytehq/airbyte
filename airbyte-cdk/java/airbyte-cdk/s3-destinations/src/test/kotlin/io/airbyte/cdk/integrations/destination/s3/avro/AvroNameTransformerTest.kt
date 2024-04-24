/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.avro

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class AvroNameTransformerTest {

    companion object {
        private val INSTANCE = AvroNameTransformer()
        private val RAW_TO_NORMALIZED_IDENTIFIERS: Map<String, String> =
            mapOf(
                "name-space" to "name_space",
                "spécial_character" to "special_character",
                "99namespace" to "_99namespace",
            )

        private val RAW_TO_NORMALIZED_NAMESPACES: Map<String, String> =
            mapOf(
                "" to "",
                "name-space1.name-space2.namespace3" to "name_space1.name_space2.namespace3",
                "namespace1.spécial_character" to "namespace1.special_character",
                "99namespace.namespace2" to "_99namespace.namespace2",
            )
    }

    @Test
    internal fun testGetIdentifier() {
        RAW_TO_NORMALIZED_IDENTIFIERS.forEach { (raw: String?, normalized: String?) ->
            Assertions.assertEquals(normalized, INSTANCE.getIdentifier(raw))
            Assertions.assertEquals(
                normalized,
                INSTANCE.convertStreamName(raw),
            )
        }
    }

    @Test
    internal fun testGetNamespace() {
        RAW_TO_NORMALIZED_NAMESPACES.forEach { (raw: String?, normalized: String?) ->
            Assertions.assertEquals(normalized, INSTANCE.getNamespace(raw))
        }
    }
}
