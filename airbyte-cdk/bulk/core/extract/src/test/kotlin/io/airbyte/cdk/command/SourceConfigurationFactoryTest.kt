/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.ConnectorErrorException
import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.fakesource.FakeSourceConfigurationSpecification
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class SourceConfigurationFactoryTest {

    private fun throwingFactory(
        e: Exception
    ): SourceConfigurationFactory<FakeSourceConfigurationSpecification, SourceConfiguration> =
        object :
            SourceConfigurationFactory<FakeSourceConfigurationSpecification, SourceConfiguration> {
            override fun makeWithoutExceptionHandling(
                pojo: FakeSourceConfigurationSpecification
            ): SourceConfiguration = throw e
        }

    private fun assertPassesThroughUnchanged(e: ConnectorErrorException) {
        val thrown =
            assertThrows<ConnectorErrorException> {
                throwingFactory(e).make(FakeSourceConfigurationSpecification())
            }
        Assertions.assertSame(e, thrown)
    }

    @Test
    fun testConfigErrorExceptionPassesThroughUnchanged() {
        val e =
            ConfigErrorException(
                "Connection from Airbyte Cloud requires SSL encryption or an SSH tunnel."
            )
        assertPassesThroughUnchanged(e)
    }

    @Test
    fun testTransientErrorExceptionPassesThroughUnchanged() {
        assertPassesThroughUnchanged(TransientErrorException("transient"))
    }

    @Test
    fun testSystemErrorExceptionPassesThroughUnchanged() {
        assertPassesThroughUnchanged(SystemErrorException("system"))
    }

    @Test
    fun testOtherExceptionIsWrappedInConfigErrorException() {
        val cause = NullPointerException("npe")
        val thrown =
            assertThrows<ConfigErrorException> {
                throwingFactory(cause).make(FakeSourceConfigurationSpecification())
            }
        Assertions.assertEquals("Failed to build ConnectorConfiguration.", thrown.message)
        Assertions.assertSame(cause, thrown.cause)
    }
}
