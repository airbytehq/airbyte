/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.context.env

import com.fasterxml.jackson.core.type.TypeReference
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.commons.json.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.env.MapPropertySource
import io.micronaut.core.cli.CommandLine
import java.nio.file.Path

private val logger = KotlinLogging.logger {}

/**
 * Custom Micronaut {@link PropertySource} that reads the command line arguments provided via the
 * connector CLI and turns them into configuration properties. This allows the arguments to be
 * injected into code that depends on them via Micronaut. <p /> This property source adds the
 * following properties to the configuration if the matching value is present in the CLI arguments:
 * <ul> <li><b>airbyte.connector.operation</b> - the operation argument (e.g. "check", "discover",
 * etc)</li> <li><b>airbyte.connector.catalog</b> - the Airbyte configured catalog as JSON read from
 * the configured catalog file path argument, if present.</li> <li><b>airbyte.connector.config</b> -
 * the normalized Airbyte connector configuration read from the configured connector configuration
 * file path argument, if present.</li> <li><b>airbyte.connector.state</b> - the Airbyte connector
 * state as JSON read from the state file path argument, if present.</li> </ol>
 */
class ConnectorConfigurationPropertySource(commandLine: CommandLine) :
    MapPropertySource("connector", resolveValues(commandLine)) {
    companion object {
        private const val PREFIX_FORMAT = "%s.%s"
        private const val ROOT_CONFIGURATION_PROPERTY_KEY = "airbyte.connector"
        const val CONNECTOR_OPERATION: String = "$ROOT_CONFIGURATION_PROPERTY_KEY.operation"
        const val CONNECTOR_CONFIG_PREFIX: String = "$ROOT_CONFIGURATION_PROPERTY_KEY.config"
        const val CONNECTOR_CATALOG_PREFIX: String = "$ROOT_CONFIGURATION_PROPERTY_KEY.catalog"
        const val CONNECTOR_CATALOG_KEY: String = "json"
        const val CONNECTOR_STATE_PREFIX: String = "$ROOT_CONFIGURATION_PROPERTY_KEY.state"
        const val CONNECTOR_STATE_KEY: String = "json"

        private fun resolveValues(commandLine: CommandLine): Map<String, Any> {
            val values: MutableMap<String, Any> = mutableMapOf()
            if (commandLine.rawArguments.isNotEmpty()) {
                values[CONNECTOR_OPERATION] = commandLine.rawArguments[0].lowercase()
                commandLine.optionValue(JavaBaseConstants.ARGS_CONFIG_KEY)?.let {
                    values.putAll(
                        loadFile(
                            it as String,
                            CONNECTOR_CONFIG_PREFIX,
                        ),
                    )
                }
                commandLine.optionValue(JavaBaseConstants.ARGS_CATALOG_KEY)?.let {
                    values.putAll(
                        loadFileContents(
                            it as String,
                            String.format(
                                PREFIX_FORMAT,
                                CONNECTOR_CATALOG_PREFIX,
                                CONNECTOR_CATALOG_KEY
                            ),
                        ),
                    )
                }
                commandLine.optionValue(JavaBaseConstants.ARGS_STATE_KEY)?.let {
                    values.putAll(
                        loadFileContents(
                            it as String,
                            String.format(
                                PREFIX_FORMAT,
                                CONNECTOR_STATE_PREFIX,
                                CONNECTOR_STATE_KEY
                            ),
                        ),
                    )
                }
            }
            logger.debug { "Resolved values: $values" }
            return values
        }

        private fun loadFile(
            propertyFilePath: String,
            prefix: String,
        ): Map<String, Any> {
            if (propertyFilePath.isNotBlank()) {
                val propertyFile = Path.of(propertyFilePath).toFile()
                if (propertyFile.exists()) {
                    val properties: Map<String, Any> =
                        Jsons.deserialize(propertyFile.readText(), MapTypeReference())
                    return flatten(properties, prefix).map { it.key to it.value }.toList().toMap()
                } else {
                    logger.warn { "Property file '$propertyFile', not found for prefix '$prefix'." }
                    return mapOf()
                }
            } else {
                return mapOf()
            }
        }

        private fun loadFileContents(
            propertyFilePath: String,
            prefix: String,
        ): Map<String, Any> {
            if (propertyFilePath.isNotBlank()) {
                val propertyFile = Path.of(propertyFilePath).toFile()
                if (propertyFile.exists()) {
                    return mapOf<String, Any>(prefix to propertyFile.readText())
                } else {
                    logger.warn { "Property file '$propertyFile', not found for prefix '$prefix'." }
                    return mapOf()
                }
            } else {
                return mapOf()
            }
        }

        private fun flatten(
            map: Map<String, Any>,
            prefix: String,
        ): Map<String, Any> {
            return map.flatMap { flattenValue(it, prefix).toList() }.toMap()
        }

        @Suppress("UNCHECKED_CAST")
        private fun flattenValue(
            entry: Map.Entry<String, Any>,
            prefix: String,
        ): Map<String, Any> {
            return if (entry.value is Map<*, *>) {
                flatten(
                    entry.value as Map<String, Any>,
                    String.format(PREFIX_FORMAT, prefix, entry.key)
                )
            } else {
                mapOf(
                    String.format(
                        PREFIX_FORMAT,
                        prefix,
                        entry.key,
                    ) to entry.value
                )
            }
        }
    }

    private class MapTypeReference : TypeReference<Map<String, Any>>()
}
