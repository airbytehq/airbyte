/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class BigQuerySQLNameTransformerTest {
    @Test
    fun testGetNamespace() {
        RAW_TO_NORMALIZED_NAMESPACES.forEach { (raw: String?, normalized: String?) ->
            Assertions.assertEquals(normalized, INSTANCE.getNamespace(raw))
        }
    }

    companion object {
        private val INSTANCE = BigQuerySQLNameTransformer()

        private val RAW_TO_NORMALIZED_NAMESPACES: Map<String, String> =
            java.util.Map.of(
                "name-space",
                "name_space",
                "spécial_character",
                "special_character", // dataset name is allowed to start with a number
                "99namespace",
                "99namespace", // dataset name starting with an underscore is hidden, so we prepend
                // a letter
                "*_namespace",
                "n__namespace",
                "_namespace",
                "n_namespace"
            )
    }
}
