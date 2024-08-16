package io.airbyte.integrations.base.destination.experimental

import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Nested

class ImplementingTest: BaseTest() {
    @Disabled
    @Nested
    inner class TestGroup1: BaseTest.TestGroup1()
}
