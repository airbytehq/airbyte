/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import io.airbyte.cdk.AirbyteConnectorRunnable
import io.airbyte.cdk.AirbyteConnectorRunner
import io.airbyte.cdk.AirbyteDestinationRunner
import io.airbyte.cdk.AirbyteSourceRunner
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.nio.file.Files
import java.nio.file.Path
import kotlin.io.path.deleteIfExists

data object CliRunner {
    /**
     * Runs a source connector with the given arguments and returns the results.
     *
     * This is useful for writing connector integration tests:
     * - the [config], [catalog] and [state] get written to temporary files;
     * - the file names get passed with the `--config`, `--catalog` and `--state` CLI arguments;
     * - an extra temporary file is created to store the output;
     * - that file name gets passed with the test-only `--output` CLI argument;
     * - [AirbyteSourceRunner] takes the CLI arguments and runs them in a new Micronaut context;
     * - after it's done, the output file contents are read and parsed into [AirbyteMessage]s.
     * - those are stored in a [BufferingOutputConsumer] which is returned.
     */
    fun runSource(
        op: String,
        config: ConfigurationJsonObjectBase? = null,
        catalog: ConfiguredAirbyteCatalog? = null,
        state: List<AirbyteStateMessage>? = null,
    ): BufferingOutputConsumer =
        runConnector(op, config, catalog, state) { args: Array<String> ->
            AirbyteSourceRunner(args)
        }

    /** Same as [runSource] but for destinations. */
    fun runDestination(
        op: String,
        config: ConfigurationJsonObjectBase? = null,
        catalog: ConfiguredAirbyteCatalog? = null,
        state: List<AirbyteStateMessage>? = null,
    ): BufferingOutputConsumer =
        runConnector(op, config, catalog, state) { args: Array<String> ->
            AirbyteDestinationRunner(args)
        }

    private fun runConnector(
        op: String,
        config: ConfigurationJsonObjectBase?,
        catalog: ConfiguredAirbyteCatalog?,
        state: List<AirbyteStateMessage>?,
        connectorRunnerConstructor: (Array<String>) -> AirbyteConnectorRunner,
    ): BufferingOutputConsumer {
        val result = BufferingOutputConsumer(ClockFactory().fixed())
        val configFile: Path? = inputFile(config)
        val catalogFile: Path? = inputFile(catalog)
        val stateFile: Path? = inputFile(state)
        val outputFile: Path = Files.createTempFile(null, null)
        val args: List<String> =
            listOfNotNull(
                "--$op",
                configFile?.let { "--config=$it" },
                catalogFile?.let { "--catalog=$it" },
                stateFile?.let { "--state=$it" },
                "--output=$outputFile",
            )
        try {
            connectorRunnerConstructor(args.toTypedArray()).run<AirbyteConnectorRunnable>()
            Files.readAllLines(outputFile)
                .filter { it.isNotBlank() }
                .map { Jsons.readValue(it, AirbyteMessage::class.java) }
                .forEach { result.accept(it) }
            return result
        } finally {
            configFile?.deleteIfExists()
            catalogFile?.deleteIfExists()
            stateFile?.deleteIfExists()
            outputFile.deleteIfExists()
        }
    }

    private fun inputFile(contents: Any?): Path? =
        contents?.let {
            Files.createTempFile(null, null).also { file ->
                Files.writeString(file, Jsons.writeValueAsString(contents))
            }
        }
}
