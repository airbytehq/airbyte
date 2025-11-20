/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.component.TableOperationsFixtures.inputRecord
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.StringValue

object TableSchemaEvolutionFixtures {
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
}
