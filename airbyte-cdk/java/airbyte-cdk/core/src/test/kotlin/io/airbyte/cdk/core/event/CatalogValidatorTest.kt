/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.event

import io.airbyte.cdk.core.command.option.MicronautConfiguredAirbyteCatalog
import io.airbyte.cdk.core.operation.Operation
import io.airbyte.cdk.core.operation.OperationType
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.micronaut.context.event.StartupEvent
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.EnumSource

class CatalogValidatorTest {
    @ParameterizedTest
    @EnumSource(value = OperationType::class, names = ["READ", "WRITE"])
    internal fun `test that a populated configured catalog can be validated`(
        operationType: OperationType
    ) {
        val connectorName = "test-destination"
        val streamName = "test-name"
        val streamNamespace = "test-namespace"
        val catalogJson =
            "{\"streams\":[{\"stream\":{\"name\":\"$streamName\",\"namespace\":\"$streamNamespace\"}}]}"
        val catalog: MicronautConfiguredAirbyteCatalog = mockk()
        val operation: Operation = mockk()

        every { catalog.getConfiguredCatalog() } returns
            Jsons.deserialize(catalogJson, ConfiguredAirbyteCatalog::class.java)
        every { operation.type() } returns operationType

        val validator =
            CatalogValidator(
                connectorName = connectorName,
                micronautConfiguredAirbyteCatalog = catalog,
                operation = operation
            )
        val event: StartupEvent = mockk()
        assertDoesNotThrow { validator.onApplicationEvent(event) }
        verify { catalog.getConfiguredCatalog() }
    }

    @ParameterizedTest
    @EnumSource(value = OperationType::class, names = ["READ", "WRITE"])
    internal fun `test that a missing configured catalog can be invalidated`(
        operationType: OperationType
    ) {
        val connectorName = "test-destination"
        val catalog: MicronautConfiguredAirbyteCatalog = mockk()
        val operation: Operation = mockk()

        every { catalog.getConfiguredCatalog() } returns CatalogValidator.emptyCatalog
        every { operation.type() } returns operationType

        val validator =
            CatalogValidator(
                connectorName = connectorName,
                micronautConfiguredAirbyteCatalog = catalog,
                operation = operation
            )
        val event: StartupEvent = mockk()
        assertThrows<IllegalArgumentException> { validator.onApplicationEvent(event) }
        verify { catalog.getConfiguredCatalog() }
    }

    @ParameterizedTest
    @EnumSource(value = OperationType::class, names = ["SPEC", "DISCOVER", "CHECK"])
    internal fun `test that catalog validation is skipped for unsupported operations`(
        operationType: OperationType
    ) {
        val connectorName = "test-destination"
        val streamName = "test-name"
        val streamNamespace = "test-namespace"
        val catalogJson =
            "{\"streams\":[{\"stream\":{\"name\":\"$streamName\",\"namespace\":\"$streamNamespace\"}}]}"
        val catalog: MicronautConfiguredAirbyteCatalog = mockk()
        val operation: Operation = mockk()

        every { catalog.getConfiguredCatalog() } returns
            Jsons.deserialize(catalogJson, ConfiguredAirbyteCatalog::class.java)
        every { operation.type() } returns operationType

        val validator =
            CatalogValidator(
                connectorName = connectorName,
                micronautConfiguredAirbyteCatalog = catalog,
                operation = operation
            )
        val event: StartupEvent = mockk()
        assertDoesNotThrow { validator.onApplicationEvent(event) }
        verify(exactly = 0) { catalog.getConfiguredCatalog() }
    }
}
