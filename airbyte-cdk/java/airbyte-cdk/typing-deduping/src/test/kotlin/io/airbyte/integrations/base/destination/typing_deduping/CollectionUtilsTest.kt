/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import io.airbyte.integrations.base.destination.typing_deduping.CollectionUtils.matchingKey
import java.util.*
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

class CollectionUtilsTest {
    @ParameterizedTest
    @CsvSource("foo,foo", "bar,BAR", "fIzZ,fizz", "ZIP_zop,zip_ZOP", "nope,")
    fun testMatchingKey(input: String, output: String?) {
        val expected = Optional.ofNullable(output)
        Assertions.assertEquals(matchingKey(TEST_COLLECTION, input), expected)
    }

    companion object {
        var TEST_COLLECTION: Set<String> = setOf("foo", "BAR", "fizz", "zip_ZOP")
    }
}
