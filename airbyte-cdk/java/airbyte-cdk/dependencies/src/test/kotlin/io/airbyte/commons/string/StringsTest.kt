/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.string

import com.google.common.collect.Lists
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class StringsTest {
    private class JoinClass(private val id: Int) {
        override fun toString(): String {
            return "id = $id"
        }
    }

    @Test
    fun testJoin() {
        Assertions.assertEquals(
            "1, 2, 3, 4, 5",
            Strings.join(Lists.newArrayList(1, 2, 3, 4, 5), ", ")
        )

        Assertions.assertEquals(
            "id = 1, id = 2, id = 3",
            Strings.join(Lists.newArrayList(JoinClass(1), JoinClass(2), JoinClass(3)), ", ")
        )
    }
}
