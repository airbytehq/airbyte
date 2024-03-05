/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.context.env

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource.Companion.CONNECTOR_CATALOG_KEY
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource.Companion.CONNECTOR_CATALOG_PREFIX
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource.Companion.CONNECTOR_CONFIG_PREFIX
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource.Companion.CONNECTOR_OPERATION
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource.Companion.CONNECTOR_STATE_KEY
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource.Companion.CONNECTOR_STATE_PREFIX
import io.airbyte.cdk.core.operation.OperationType
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.micronaut.core.cli.CommandLine
import io.mockk.every
import io.mockk.mockk
import kotlin.io.path.pathString
import kotlin.io.path.writeText
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class ConnectorConfigurationPropertySourceTest {
    @Test
    internal fun `test converting the connector configuration argument to configuration properties`() {
        val key = "key"
        val value = "foo"
        val operation = OperationType.CHECK.name.lowercase()
        val commandLine: CommandLine = mockk()
        val configJson = "{\"$key\":\"$value\", \"nested\": { \"$key\":\"$value\" } }"
        val configFile = kotlin.io.path.createTempFile("connector-config-", ".json")
        configFile.writeText(configJson)
        every { commandLine.rawArguments } returns
            arrayOf(operation, JavaBaseConstants.ARGS_CONFIG_KEY, configFile.pathString)
        every { commandLine.optionValue(JavaBaseConstants.ARGS_CONFIG_KEY) } returns
            configFile.pathString
        every { commandLine.optionValue(JavaBaseConstants.ARGS_CATALOG_KEY) } returns ""
        every { commandLine.optionValue(JavaBaseConstants.ARGS_STATE_KEY) } returns ""

        val propertySource = ConnectorConfigurationPropertySource(commandLine)
        assertEquals(operation, propertySource.get(CONNECTOR_OPERATION))
        assertEquals(value, propertySource.get("$CONNECTOR_CONFIG_PREFIX.$key"))
        assertEquals(value, propertySource.get("$CONNECTOR_CONFIG_PREFIX.nested.$key"))
    }

    @Test
    internal fun `test converting the connector configuration argument with an unknown path to configuration properties`() {
        val operation = OperationType.CHECK.name.lowercase()
        val commandLine: CommandLine = mockk()
        val configFilePath = "/does/not/exist"
        every { commandLine.rawArguments } returns
            arrayOf(operation, JavaBaseConstants.ARGS_CONFIG_KEY, configFilePath)
        every { commandLine.optionValue(JavaBaseConstants.ARGS_CONFIG_KEY) } returns configFilePath
        every { commandLine.optionValue(JavaBaseConstants.ARGS_CATALOG_KEY) } returns ""
        every { commandLine.optionValue(JavaBaseConstants.ARGS_STATE_KEY) } returns ""

        val propertySource = ConnectorConfigurationPropertySource(commandLine)
        assertEquals(1, propertySource.asMap().size)
        assertEquals(operation, propertySource.get(CONNECTOR_OPERATION))
    }

    @Test
    internal fun `test converting the connector configuration argument with a blank path to configuration properties`() {
        val operation = OperationType.CHECK.name.lowercase()
        val commandLine: CommandLine = mockk()
        every { commandLine.rawArguments } returns
            arrayOf(operation, JavaBaseConstants.ARGS_CONFIG_KEY)
        every { commandLine.optionValue(JavaBaseConstants.ARGS_CONFIG_KEY) } returns ""
        every { commandLine.optionValue(JavaBaseConstants.ARGS_CATALOG_KEY) } returns ""
        every { commandLine.optionValue(JavaBaseConstants.ARGS_STATE_KEY) } returns ""

        val propertySource = ConnectorConfigurationPropertySource(commandLine)
        assertEquals(1, propertySource.asMap().size)
        assertEquals(operation, propertySource.get(CONNECTOR_OPERATION))
    }

    @Test
    internal fun `test converting the connector catalog argument to configuration properties`() {
        val streamName = "test"
        val streamNamespace = "test-namespace"
        val operation = OperationType.READ.name.lowercase()
        val commandLine: CommandLine = mockk()
        val catalogJson =
            "{\"streams\":[{\"stream\":{\"name\":\"$streamName\",\"namespace\":\"$streamNamespace\"}}]}"
        val catalogFile = kotlin.io.path.createTempFile("connector-catalog-", ".json")
        catalogFile.writeText(catalogJson)
        every { commandLine.rawArguments } returns
            arrayOf(operation, JavaBaseConstants.ARGS_CATALOG_KEY, catalogFile.pathString)
        every { commandLine.optionValue(JavaBaseConstants.ARGS_CONFIG_KEY) } returns ""
        every { commandLine.optionValue(JavaBaseConstants.ARGS_CATALOG_KEY) } returns
            catalogFile.pathString
        every { commandLine.optionValue(JavaBaseConstants.ARGS_STATE_KEY) } returns ""

        val propertySource = ConnectorConfigurationPropertySource(commandLine)
        assertEquals(operation, propertySource.get(CONNECTOR_OPERATION))
        assertEquals(
            catalogJson,
            propertySource.get("$CONNECTOR_CATALOG_PREFIX.$CONNECTOR_CATALOG_KEY")
        )
    }

    @Test
    internal fun `test converting the connector catalog argument with an unknown path to configuration properties`() {
        val operation = OperationType.READ.name.lowercase()
        val commandLine: CommandLine = mockk()
        val catalogFilePath = "/does/not/exist"
        every { commandLine.rawArguments } returns
            arrayOf(operation, JavaBaseConstants.ARGS_CATALOG_KEY, catalogFilePath)
        every { commandLine.optionValue(JavaBaseConstants.ARGS_CONFIG_KEY) } returns ""
        every { commandLine.optionValue(JavaBaseConstants.ARGS_CATALOG_KEY) } returns
            catalogFilePath
        every { commandLine.optionValue(JavaBaseConstants.ARGS_STATE_KEY) } returns ""

        val propertySource = ConnectorConfigurationPropertySource(commandLine)
        assertEquals(1, propertySource.asMap().size)
        assertEquals(operation, propertySource.get(CONNECTOR_OPERATION))
    }

    @Test
    internal fun `test converting the connector catalog argument with a blank path to configuration properties`() {
        val operation = OperationType.READ.name.lowercase()
        val commandLine: CommandLine = mockk()
        every { commandLine.rawArguments } returns
            arrayOf(operation, JavaBaseConstants.ARGS_CATALOG_KEY)
        every { commandLine.optionValue(JavaBaseConstants.ARGS_CONFIG_KEY) } returns ""
        every { commandLine.optionValue(JavaBaseConstants.ARGS_CATALOG_KEY) } returns ""
        every { commandLine.optionValue(JavaBaseConstants.ARGS_STATE_KEY) } returns ""

        val propertySource = ConnectorConfigurationPropertySource(commandLine)
        assertEquals(1, propertySource.asMap().size)
        assertEquals(operation, propertySource.get(CONNECTOR_OPERATION))
    }

    @Test
    internal fun `test converting the state argument to configuration properties`() {
        val operation = OperationType.READ.name.lowercase()
        val commandLine: CommandLine = mockk()
        val stateJson = "{\"cursor\":\"foo\"}"
        val stateFile = kotlin.io.path.createTempFile("connector-state-", ".json")
        stateFile.writeText(stateJson)
        every { commandLine.rawArguments } returns
            arrayOf(operation, JavaBaseConstants.ARGS_STATE_KEY, stateFile.pathString)
        every { commandLine.optionValue(JavaBaseConstants.ARGS_CONFIG_KEY) } returns ""
        every { commandLine.optionValue(JavaBaseConstants.ARGS_CATALOG_KEY) } returns ""
        every { commandLine.optionValue(JavaBaseConstants.ARGS_STATE_KEY) } returns
            stateFile.pathString

        val propertySource = ConnectorConfigurationPropertySource(commandLine)
        assertEquals(operation, propertySource.get(CONNECTOR_OPERATION))
        assertEquals(stateJson, propertySource.get("$CONNECTOR_STATE_PREFIX.$CONNECTOR_STATE_KEY"))
    }

    @Test
    internal fun `test converting the connector state argument with an unknown path to configuration properties`() {
        val operation = OperationType.READ.name.lowercase()
        val commandLine: CommandLine = mockk()
        val stateFilePath = "/does/not/exist"
        every { commandLine.rawArguments } returns
            arrayOf(operation, JavaBaseConstants.ARGS_STATE_KEY, stateFilePath)
        every { commandLine.optionValue(JavaBaseConstants.ARGS_CONFIG_KEY) } returns ""
        every { commandLine.optionValue(JavaBaseConstants.ARGS_CATALOG_KEY) } returns ""
        every { commandLine.optionValue(JavaBaseConstants.ARGS_STATE_KEY) } returns stateFilePath

        val propertySource = ConnectorConfigurationPropertySource(commandLine)
        assertEquals(1, propertySource.asMap().size)
        assertEquals(operation, propertySource.get(CONNECTOR_OPERATION))
    }

    @Test
    internal fun `test converting the connector state argument with a blank path to configuration properties`() {
        val operation = OperationType.READ.name.lowercase()
        val commandLine: CommandLine = mockk()
        every { commandLine.rawArguments } returns
            arrayOf(operation, JavaBaseConstants.ARGS_STATE_KEY)
        every { commandLine.optionValue(JavaBaseConstants.ARGS_CONFIG_KEY) } returns ""
        every { commandLine.optionValue(JavaBaseConstants.ARGS_CATALOG_KEY) } returns ""
        every { commandLine.optionValue(JavaBaseConstants.ARGS_STATE_KEY) } returns ""

        val propertySource = ConnectorConfigurationPropertySource(commandLine)
        assertEquals(1, propertySource.asMap().size)
        assertEquals(operation, propertySource.get(CONNECTOR_OPERATION))
    }
}
