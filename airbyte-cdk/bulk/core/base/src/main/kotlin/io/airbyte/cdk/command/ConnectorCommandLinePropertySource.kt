/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import io.airbyte.cdk.Operation
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.env.MapPropertySource
import io.micronaut.core.cli.CommandLine
import java.io.File
import java.nio.file.Path

private val log = KotlinLogging.logger {}

/**
 * Custom Micronaut [MapPropertySource] that reads the command line arguments provided via the
 * connector CLI and turns them into configuration properties. This allows the arguments to be
 * injected into code that depends on them via Micronaut.
 */
class ConnectorCommandLinePropertySource(
    commandLine: CommandLine,
    allLongOptions: List<String>,
) : MapPropertySource("connector", resolveValues(commandLine, allLongOptions))

const val CONNECTOR_CONFIG_PREFIX: String = "airbyte.connector.config"
const val CONNECTOR_CATALOG_PREFIX: String = "airbyte.connector.catalog"
const val CONNECTOR_STATE_PREFIX: String = "airbyte.connector.state"

private fun resolveValues(
    commandLine: CommandLine,
    allLongOptions: List<String>,
): Map<String, Any> {
    val ops: List<String> =
        allLongOptions.map { it.removePrefix("--") }.filter { commandLine.optionValue(it) != null }
    if (ops.isEmpty()) {
        throw IllegalArgumentException("Command line is missing an operation.")
    }
    if (ops.size > 1) {
        throw IllegalArgumentException("Command line has multiple operations: $ops")
    }
    val values: MutableMap<String, Any> = mutableMapOf()
    values[Operation.PROPERTY] = ops.first()
    for ((cliOptionKey, prefix) in
        mapOf(
            "config" to CONNECTOR_CONFIG_PREFIX,
            "catalog" to CONNECTOR_CATALOG_PREFIX,
            "state" to CONNECTOR_STATE_PREFIX,
        )) {
        val cliOptionValue = commandLine.optionValue(cliOptionKey) as String?
        if (cliOptionValue.isNullOrBlank()) {
            continue
        }
        val jsonFile: File = Path.of(cliOptionValue).toFile()
        if (!jsonFile.exists()) {
            log.warn { "File '$jsonFile' not found for '$cliOptionKey'." }
            continue
        }
        values["$prefix.json"] = jsonFile.readText().replace("$", "\${:$}")
    }
    return values
}
