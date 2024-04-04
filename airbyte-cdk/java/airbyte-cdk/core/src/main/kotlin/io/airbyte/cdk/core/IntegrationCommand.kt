/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.core.operation.Operation
import io.airbyte.cdk.core.operation.OperationType
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.util.ApmTraceUtils
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Value
import jakarta.inject.Inject
import jakarta.inject.Named
import picocli.CommandLine
import java.nio.file.Path
import java.util.Optional
import java.util.function.Consumer

private val logger = KotlinLogging.logger {}

/**
 * CLI implementation that invokes the requested operation for the connector.
 */
@CommandLine.Command(
    name = "airbyte-connector",
    description = ["Executes an Airbyte connector"],
    mixinStandardHelpOptions = true,
    header = [
        "@|magenta     ___    _      __          __       |@",
        "@|magenta    /   |  (_)____/ /_  __  __/ /____   |@",
        "@|magenta   / /| | / / ___/ __ \\/ / / / __/ _   |@",
        "@|magenta  / ___ |/ / /  / /_/ / /_/ / /_/  __/  |@",
        "@|magenta /_/  |_/_/_/  /_.___/\\__, /\\__/\\___/|@",
        "@|magenta                    /____/              |@",
    ],
)
@SuppressFBWarnings(
    value = ["NP_NONNULL_RETURN_VIOLATION", "NP_OPTIONAL_RETURN_NULL"],
    justification = "Uses dependency injection",
)
class IntegrationCommand : Runnable {
    @Value("\${micronaut.application.name}")
    lateinit var connectorName: String

    @Inject
    lateinit var operations: List<Operation>

    @Inject
    @Named("outputRecordCollector")
    lateinit var outputRecordCollector: Consumer<AirbyteMessage>

    @CommandLine.Parameters(
        index = "0",
        description = [
            "The command to execute (check|discover|read|spec|write)",
            "\t check - checks the config can be used to connect",
            "\t discover - outputs a catalog describing the source's catalog",
            "\t read - reads the source and outputs messages to STDOUT",
            "\t spec - outputs the json configuration specification",
            "\t write - writes messages from STDIN to the integration",
        ],
    )
    lateinit var command: String

    @CommandLine.Option(
        names = [ "--" + JavaBaseConstants.ARGS_CONFIG_KEY ],
        description = [
            JavaBaseConstants.ARGS_CONFIG_DESC,
            "Required by the following commands: check, discover, read, write",
        ],
    )
    lateinit var configFile: Path

    @CommandLine.Option(
        names = [ "--" + JavaBaseConstants.ARGS_CATALOG_KEY ],
        description = [
            JavaBaseConstants.ARGS_CATALOG_DESC,
            "Required by the following commands: read, write",
        ],
    )
    lateinit var catalogFile: Path

    @CommandLine.Option(
        names = [ "--" + JavaBaseConstants.ARGS_STATE_KEY ],
        description = [
            JavaBaseConstants.ARGS_PATH_DESC,
            "Required by the following commands: read",
        ],
    )
    lateinit var stateFile: Optional<Path>

    @CommandLine.Spec
    lateinit var commandSpec: CommandLine.Model.CommandSpec

    override fun run() {
        val result = execute(command)
        result.onSuccess { airbyteMessage ->
            airbyteMessage?.let {
                outputRecordCollector.accept(airbyteMessage)
            }
        }
        result.onFailure {
            commandSpec.commandLine().usage(System.out)
            logger.error(it) { "\nUnable to perform operation '$command'." }
            // Many of the exceptions thrown are nested inside layers of RuntimeExceptions. An attempt is made
            // to
            // find the root exception that corresponds to a configuration error. If that does not exist, we
            // just return the original exception.
            ApmTraceUtils.addExceptionToTrace(it)
            val rootThrowable = ConnectorExceptionUtil.getRootConfigError(Exception(it))
            val displayMessage = ConnectorExceptionUtil.getDisplayMessage(rootThrowable)
            // If the source connector throws a config error, a trace message with the relevant message should
            // be surfaced.
            if (ConnectorExceptionUtil.isConfigError(rootThrowable)) {
                AirbyteTraceMessageUtility.emitConfigErrorTrace(it, displayMessage)
            }
            if (OperationType.CHECK.name.equals(command, true)) {
                // Currently, special handling is required for the CHECK case since the user display information in
                // the trace message is
                // not properly surfaced to the FE. In the future, we can remove this and just throw an exception.
                outputRecordCollector
                    .accept(
                        AirbyteMessage()
                            .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                            .withConnectionStatus(
                                AirbyteConnectionStatus()
                                    .withStatus(AirbyteConnectionStatus.Status.FAILED)
                                    .withMessage(displayMessage),
                            ),
                    )
            }
        }

        logger.info { "Completed integration: $connectorName" }
    }

    private fun execute(command: String): Result<AirbyteMessage?> {
        return try {
            val operationType = OperationType.valueOf(command.uppercase())
            val operation: Operation? = operations.firstOrNull { o: Operation -> (operationType == o.type()) }
            operation?.execute()
                ?: Result.failure(
                    IllegalArgumentException(
                        "Connector does not support the '${operationType.name.lowercase()}' operation.",
                    ),
                )
        } catch (e: IllegalArgumentException) {
            Result.failure(IllegalArgumentException("Connector does not support the '${command.lowercase()}' operation.", e))
        }
    }
}
