package io.airbyte.integrations.base.destination.experimental

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

abstract class FeatureSpecificTest {
    @Test
    open fun test1() {
        Assertions.fail<Unit>()
    }
}
