package io.airbyte.cdk.write

import io.github.oshai.kotlinlogging.KotlinLogging
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class DestinationRunnerTest {
    val log = KotlinLogging.logger {}

    @Test
    fun testRunner() = runTest {

        launch {
            val testData = javaClass.getResource("/messages.jsonl")!!.openStream()
            InputStreamReader(testData).run()
            log.info { "test data loaded" }
        }

        val destination = MockDestination(2)
        val runner = DestinationRunner(destination)
        runner.run()
    }
}
