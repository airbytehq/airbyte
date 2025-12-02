/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import org.junit.jupiter.api.Test

class TransformationsTest {
    @Test
    fun `test avro illegal start character`() {
        val unsafeName = "1d_view"
        assert(Transformations.toAvroSafeName(unsafeName) == "_1d_view")
    }

    @Test
    fun `test avro special characters`() {
        val unsafeName = "1d_view!@#$%^&*()"
        assert(Transformations.toAvroSafeName(unsafeName) == "_1d_view__________")
    }
}
