/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.component.TableOperationsFixtures.inputRecord
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.util.Jsons

object TableSchemaEvolutionFixtures {
    val ID_AND_STRING_SCHEMA =
        ObjectType(
            linkedMapOf(
                "id" to FieldType(IntegerType, true),
                "test" to FieldType(StringType, true),
            ),
        )
    val ID_AND_UNKNOWN_SCHEMA =
        ObjectType(
            linkedMapOf(
                "id" to FieldType(IntegerType, true),
                "test" to FieldType(UnknownType(Jsons.readTree("""{"type": "potato"}""")), true),
            ),
        )

    val STRING_TO_UNKNOWN_TYPE_INPUT_RECORDS =
        listOf(
            inputRecord("id" to IntegerValue(1), "test" to StringValue("\"foo\"")),
            inputRecord("id" to IntegerValue(2), "test" to StringValue("""{"foo": "bar"}""")),
            inputRecord("id" to IntegerValue(3), "test" to StringValue("true")),
            inputRecord("id" to IntegerValue(4), "test" to StringValue("0")),
            inputRecord("id" to IntegerValue(5), "test" to StringValue("foo")),
        )
    val STRING_TO_UNKNOWN_TYPE_EXPECTED_RECORDS =
        listOf(
            mapOf("id" to 1L, "test" to "\"foo\""),
            mapOf("id" to 2L, "test" to """{"foo": "bar"}"""),
            mapOf("id" to 3L, "test" to "true"),
            mapOf("id" to 4L, "test" to "0"),
            mapOf("id" to 5L, "test" to "foo"),
        )

    val UNKNOWN_TO_STRING_TYPE_INPUT_RECORDS =
        listOf(
            inputRecord("id" to IntegerValue(1), "test" to StringValue("foo")),
            inputRecord(
                "id" to IntegerValue(2),
                "test" to ObjectValue(linkedMapOf("foo" to StringValue("bar")))
            ),
            inputRecord("id" to IntegerValue(3), "test" to BooleanValue(true)),
            inputRecord("id" to IntegerValue(4), "test" to IntegerValue(0)),
        )
    val UNKNOWN_TO_STRING_TYPE_EXPECTED_RECORDS =
        listOf(
            mapOf("id" to 1L, "test" to "foo"),
            mapOf("id" to 2L, "test" to """{"foo":"bar"}"""),
            mapOf("id" to 3L, "test" to "true"),
            mapOf("id" to 4L, "test" to "0"),
        )

    val APPLY_CHANGESET_INITIAL_COLUMN_MAPPING =
        ColumnNameMapping(
            mapOf(
                "id" to "id",
                "updated_at" to "updated_at",
                "to_retain" to "to_retain",
                "to_change" to "to_change",
                "to_drop" to "to_drop",
            )
        )
    val APPLY_CHANGESET_MODIFIED_COLUMN_MAPPING =
        ColumnNameMapping(
            mapOf(
                "id" to "id",
                "updated_at" to "updated_at",
                "to_retain" to "to_retain",
                "to_change" to "to_change",
                "to_add" to "to_add",
            )
        )
    val APPLY_CHANGESET_EXPECTED_EXTRACTED_AT = "2025-01-22T00:00:00Z"
}
