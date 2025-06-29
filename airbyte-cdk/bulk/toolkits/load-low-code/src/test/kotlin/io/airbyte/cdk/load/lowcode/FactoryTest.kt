package io.airbyte.cdk.load.lowcode

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.DestinationConfiguration
import kotlin.test.assertFailsWith
import org.junit.jupiter.api.Test

class MockConfig(
    val apiId: String,
    val apiToken: String,
): DestinationConfiguration()

val INVALID_AIRCALL_API_ID: String = "1"
val INVALID_AIRCALL_API_TOKEN: String = "2"

val VALID_AIRCALL_API_ID: String = "<replace value here>"
val VALID_AIRCALL_API_TOKEN: String = "<replace value here>"

class FactoryTest {

    @Test
    internal fun `test given invalid credentials when check then throw`() {
        val config = MockConfig(INVALID_AIRCALL_API_ID, INVALID_AIRCALL_API_TOKEN)
        val checker: DestinationChecker<MockConfig> = Factory(config).createDestinationChecker()
        assertFailsWith<AssertionError>(
            block = { checker.check(config) }
        )
    }

    @Test
    internal fun `test given valid credentials when check then throw`() {
        // FIXME for this test to pass, change the value of VALID_AIRCALL_API_ID and VALID_AIRCALL_API_TOKEN
        val config = MockConfig(VALID_AIRCALL_API_ID, VALID_AIRCALL_API_TOKEN)
        val checker: DestinationChecker<MockConfig> = Factory(config).createDestinationChecker()
        checker.check(config)
        // no assertion, just checking that `check` does not throw
    }

}
