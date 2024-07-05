/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.map

import com.google.common.collect.ImmutableMap
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class MoreMapsTest {
    @Test
    fun testMerge() {
        val map1: Map<String, Int> = ImmutableMap.of("a", 3, "b", 2)
        val map2: Map<String, Int> = ImmutableMap.of("a", 1)

        Assertions.assertEquals(ImmutableMap.of("a", 1, "b", 2), MoreMaps.merge(map1, map2))
    }
}
