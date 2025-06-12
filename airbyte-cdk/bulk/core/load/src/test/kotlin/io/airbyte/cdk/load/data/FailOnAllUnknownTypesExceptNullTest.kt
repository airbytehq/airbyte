/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.load.test.util.Root
import io.airbyte.cdk.load.test.util.SchemaRecordBuilder
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class FailOnAllUnknownTypesExceptNullTest {
    @Test
    fun testBasicTypeBehavior() {
        val nullType = JsonNodeFactory.instance.objectNode().put("type", "null")
        val (inputSchema, expectedOutput) =
            SchemaRecordBuilder<Root>()
                .with(UnknownType(nullType))
                .with(
                    UnknownType(
                        JsonNodeFactory.instance
                            .objectNode()
                            .set(
                                "type",
                                JsonNodeFactory.instance.arrayNode().add("null").add("null")
                            )
                    )
                )
                .build()
        FailOnAllUnknownTypesExceptNull().map(inputSchema).let {
            Assertions.assertEquals(expectedOutput, it)
        }
    }

    @Test
    fun `test throws on non-null unknown types`() {
        val (inputSchema, _) =
            SchemaRecordBuilder<Root>()
                .with(UnknownType(JsonNodeFactory.instance.objectNode().put("type", "whatever")))
                .build()
        Assertions.assertThrows(IllegalStateException::class.java) {
            FailOnAllUnknownTypesExceptNull().map(inputSchema)
        }
    }
}
