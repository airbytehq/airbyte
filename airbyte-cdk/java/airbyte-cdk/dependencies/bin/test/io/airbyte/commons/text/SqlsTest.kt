/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.text

import com.google.common.collect.Lists
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class SqlsTest {
    internal enum class E1 {
        VALUE_1,
        VALUE_TWO,
        value_three,
    }

    @Test
    fun testToSqlName() {
        Assertions.assertEquals("value_1", Sqls.toSqlName(E1.VALUE_1))
        Assertions.assertEquals("value_two", Sqls.toSqlName(E1.VALUE_TWO))
        Assertions.assertEquals("value_three", Sqls.toSqlName(E1.value_three))
    }

    @Test
    fun testInFragment() {
        Assertions.assertEquals(
            "('value_two','value_three')",
            Sqls.toSqlInFragment(Lists.newArrayList(E1.VALUE_TWO, E1.value_three))
        )
    }
}
