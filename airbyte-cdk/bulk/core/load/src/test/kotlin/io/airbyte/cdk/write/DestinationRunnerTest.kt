package io.airbyte.cdk.write

import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class DestinationRunnerTest {
    @Test
    fun testRunner() = runTest {
        val destination = MockDestination(2)
        val runner = DestinationRunner(destination)
        runner.run()
    }
}
