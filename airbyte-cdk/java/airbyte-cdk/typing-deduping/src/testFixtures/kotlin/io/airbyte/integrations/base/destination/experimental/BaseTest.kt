package io.airbyte.integrations.base.destination.experimental

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test

abstract class BaseTest {
    @Nested
    open inner class TestGroup1: FeatureSpecificTest()

    @Nested
    open inner class TestGroup2 {
        @Test
        open fun test1() {
            Assertions.fail<Unit>()
        }
    }
}
