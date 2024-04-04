/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.event

import io.airbyte.cdk.core.config.ConnectorConfiguration
import io.airbyte.cdk.core.operation.OperationType
import io.airbyte.protocol.models.Jsons
import io.airbyte.validation.json.JsonSchemaValidator
import io.micronaut.context.event.StartupEvent
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.EnumSource

class ConfigurationValidatorTest {
    @ParameterizedTest
    @EnumSource(value = OperationType::class, names = ["CHECK", "DISCOVER", "READ", "WRITE"])
    internal fun `test that a populated connector configuration can be validated`(operationType: OperationType) {
        val connectorName = "test-destination"
        val operation = operationType.name.lowercase()
        val connectorConfiguration: ConnectorConfiguration = mockk()
        val jsonValidator: JsonSchemaValidator = mockk()

        every { jsonValidator.validate(any(), any()) } returns setOf()
        every { connectorConfiguration.toJson() } returns Jsons.deserialize("{\"key\":\"value\"}")

        val validator =
            ConfigurationValidator(
                connectorName = connectorName,
                operation = operation,
                configuration = connectorConfiguration,
                validator = jsonValidator,
            )
        val event: StartupEvent = mockk()

        assertDoesNotThrow {
            validator.onApplicationEvent(event)
        }

        verify { jsonValidator.validate(any(), any()) }
    }

    @ParameterizedTest
    @EnumSource(value = OperationType::class, names = ["CHECK", "DISCOVER", "READ", "WRITE"])
    internal fun `test that an invalid populated connector configuration fails validation`(operationType: OperationType) {
        val connectorName = "test-destination"
        val operation = operationType.name.lowercase()
        val connectorConfiguration: ConnectorConfiguration = mockk()
        val jsonValidator: JsonSchemaValidator = mockk()

        every { jsonValidator.validate(any(), any()) } returns setOf("some error")
        every { connectorConfiguration.toJson() } returns Jsons.deserialize("{\"key\":\"value\"}")

        val validator =
            ConfigurationValidator(
                connectorName = connectorName,
                operation = operation,
                configuration = connectorConfiguration,
                validator = jsonValidator,
            )
        val event: StartupEvent = mockk()

        assertThrows<Exception> {
            validator.onApplicationEvent(event)
        }

        verify { jsonValidator.validate(any(), any()) }
    }

    @ParameterizedTest
    @EnumSource(value = OperationType::class, names = ["SPEC"])
    internal fun `test that a connector configuration validation is skipped for unsupported operations`(operationType: OperationType) {
        val connectorName = "test-destination"
        val operation = operationType.name.lowercase()
        val connectorConfiguration: ConnectorConfiguration = mockk()
        val jsonValidator: JsonSchemaValidator = mockk()

        every { jsonValidator.validate(any(), any()) } returns setOf()
        every { connectorConfiguration.toJson() } returns Jsons.deserialize("{\"key\":\"value\"}")

        val validator =
            ConfigurationValidator(
                connectorName = connectorName,
                operation = operation,
                configuration = connectorConfiguration,
                validator = jsonValidator,
            )
        val event: StartupEvent = mockk()

        assertDoesNotThrow {
            validator.onApplicationEvent(event)
        }

        verify(exactly = 0) { jsonValidator.validate(any(), any()) }
    }
}
