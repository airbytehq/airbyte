/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write.load

import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.integrations.destination.postgres.write.transform.PostgresValueCoercer
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Test

internal class PostgresRecordFormatterTest {

    @Test
    fun `schema formatter removes nested null characters before serialization`() {
        val value =
            ObjectValue(
                linkedMapOf(
                    "entries" to
                        ArrayValue(
                            listOf(ObjectValue(linkedMapOf("text" to StringValue("a\u0000b"))))
                        )
                )
            )
        val enrichedValue =
            EnrichedAirbyteValue(
                abValue = value,
                type = ObjectTypeWithoutSchema,
                name = "entries",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )
        val coercer = PostgresValueCoercer()
        coercer.map(enrichedValue)

        val serialized =
            PostgresSchemaRecordFormatter(listOf("entries"))
                .format(mapOf("entries" to enrichedValue.abValue))[0]
                .toString()

        assertFalse(serialized.contains('\u0000'))
        assertFalse(serialized.contains("\\u0000"))
    }

    @Test
    fun `raw formatter removes nested null characters before serialization`() {
        val value =
            ObjectValue(
                linkedMapOf(
                    "entries" to
                        ArrayValue(
                            listOf(ObjectValue(linkedMapOf("text" to StringValue("a\u0000b"))))
                        )
                )
            )
        val enrichedValue =
            EnrichedAirbyteValue(
                abValue = value,
                type = ObjectTypeWithoutSchema,
                name = "entries",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )
        val coercer = PostgresValueCoercer()
        coercer.map(enrichedValue)

        val serialized =
            PostgresRawRecordFormatter(listOf("_airbyte_data"))
                .format(mapOf("entries" to enrichedValue.abValue))[0]
                .toString()

        assertFalse(serialized.contains('\u0000'))
        assertFalse(serialized.contains("\\u0000"))
    }
}
