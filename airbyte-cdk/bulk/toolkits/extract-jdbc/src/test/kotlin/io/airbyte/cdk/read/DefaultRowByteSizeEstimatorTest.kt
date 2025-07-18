/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.read.TestFixtures.sharedState
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class DefaultRowByteSizeEstimatorTest {

    fun estimate(jsonRecord: String): Int =
        sharedState().rowByteSizeEstimator().apply(Jsons.readTree(jsonRecord) as ObjectNode).toInt()

    @Test
    fun testZero() {
        Assertions.assertEquals(18, estimate("""{}"""))
    }

    @Test
    fun testOne() {
        Assertions.assertEquals(34, estimate("""{"one":1}"""))
    }

    @Test
    fun testTwo() {
        Assertions.assertEquals(51, estimate("""{"one":1,"two":2}"""))
    }

    @Test
    fun testThree() {
        Assertions.assertEquals(68, estimate("""{"one":1,"two":2,"three":3}"""))
    }

    @Test
    fun testFour() {
        Assertions.assertEquals(90, estimate("""{"one":1,"two":2,"three":3,"four":"four"}"""))
    }
}
