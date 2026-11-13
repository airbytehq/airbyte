/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.fakesource.FakeSourceConfiguration
import io.airbyte.cdk.fakesource.UserDefinedCursor
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import java.time.Duration
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/** Exception handling in [SourceConfigurationFactory.make]; plain JUnit, no Micronaut. */
class SourceConfigurationFactoryExceptionTest {

    class TestSpec : ConfigurationSpecification()

    private fun factory(
        block: (TestSpec) -> FakeSourceConfiguration,
    ): SourceConfigurationFactory<TestSpec, FakeSourceConfiguration> =
        object : SourceConfigurationFactory<TestSpec, FakeSourceConfiguration> {
            override fun makeWithoutExceptionHandling(pojo: TestSpec): FakeSourceConfiguration =
                block(pojo)
        }

    @Test
    fun testSuccessIsPassedThrough() {
        val expected =
            FakeSourceConfiguration(
                realHost = "localhost",
                realPort = 9092,
                sshTunnel = SshNoTunnelMethod,
                sshConnectionOptions = SshConnectionOptions.fromAdditionalProperties(emptyMap()),
                cursor = UserDefinedCursor,
                maxConcurrency = 1,
                checkpointTargetInterval = Duration.ofDays(100L),
            )
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
