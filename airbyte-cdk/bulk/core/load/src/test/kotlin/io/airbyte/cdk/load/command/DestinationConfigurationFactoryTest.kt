/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.command.ConfigurationSpecification
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/** Exception handling in [DestinationConfigurationFactory.make]; plain JUnit, no Micronaut. */
class DestinationConfigurationFactoryTest {

    class TestSpec : ConfigurationSpecification()

    class TestConfiguration : DestinationConfiguration()

    private fun factory(
        block: (TestSpec) -> TestConfiguration,
    ): DestinationConfigurationFactory<TestSpec, TestConfiguration> =
        object : DestinationConfigurationFactory<TestSpec, TestConfiguration> {
            override fun makeWithoutExceptionHandling(pojo: TestSpec): TestConfiguration =
                block(pojo)
        }

    @Test
    fun testSuccessIsPassedThrough() {
        val expected = TestConfiguration()
        Assertions.assertSame(expected, factory { expected }.make(TestSpec()))
    }

    @Test
    fun testConfigErrorExceptionIsRethrownUnchanged() {
        val message = "Connection from Airbyte Cloud requires SSL encryption or an SSH tunnel."
        val thrown = ConfigErrorException(message)
        val caught: ConfigErrorException =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                factory { throw thrown }.make(TestSpec())
            }
        Assertions.assertSame(thrown, caught)
        Assertions.assertEquals(message, caught.message)
        Assertions.assertNull(caught.cause)
    }

    @Test
    fun testTransientErrorExceptionIsRethrownUnchanged() {
        val thrown = TransientErrorException("try again later")
        val caught: TransientErrorException =
            Assertions.assertThrows(TransientErrorException::class.java) {
                factory { throw thrown }.make(TestSpec())
            }
        Assertions.assertSame(thrown, caught)
    }

    @Test
    fun testOtherExceptionIsWrapped() {
        val cause = RuntimeException("boom")
        val caught: ConfigErrorException =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                factory { throw cause }.make(TestSpec())
            }
        Assertions.assertEquals("Failed to build ConnectorConfiguration.", caught.message)
        Assertions.assertSame(cause, caught.cause)
    }
}
