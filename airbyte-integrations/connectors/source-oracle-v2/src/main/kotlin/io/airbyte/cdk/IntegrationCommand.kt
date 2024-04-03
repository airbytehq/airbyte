/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.operation.Operation
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Value
import jakarta.inject.Inject
import java.nio.file.Path
import java.util.*
import picocli.CommandLine

private val logger = KotlinLogging.logger {}

/**
 * As a [Runnable], this object invokes the requested operation for the connector.
 * Otherwise, its [CommandLine] annotations define the command-line interface.
 * The annotated fields are never used directly, instead the command-line is parsed
 * via [io.airbyte.cdk.command.ConnectorCommandLinePropertySource].
 */
@CommandLine.Command(
    name = "airbyte-connector",
    description = ["Executes an Airbyte connector"],
    mixinStandardHelpOptions = true,
    header =
        [
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

    @CommandLine.Option(
        names = ["--spec"],
        description = ["outputs the json configuration specification"],
    )
    var isSpec: Boolean = false

    @CommandLine.Option(
        names = ["--check"],
        description = ["checks the config can be used to connect"],
    )
    var isCheck: Boolean = false

    @CommandLine.Option(
        names = ["--discover"],
        description = ["outputs a catalog describing the source's catalog"],
    )
    var isDiscover: Boolean = false

    @CommandLine.Option(
        names = ["--read"],
        description = ["reads the source and outputs messages to STDOUT"],
    )
    var isRead: Boolean = false

    @CommandLine.Option(
        names = ["--write"],
        description = ["writes messages from STDIN to the integration"],
    )
    var isWrite: Boolean = false

    /*
     * This option is present so that the usage information will include the option.  It
     * is not actually used in this class and is handled by the property source loader.
     */
    @CommandLine.Option(
        names = ["--" + JavaBaseConstants.ARGS_CONFIG_KEY],
        description =
            [
                JavaBaseConstants.ARGS_CONFIG_DESC,
                "Required by the following commands: check, discover, read, write",
            ],
    )
    lateinit var configFile: Optional<Path>

    /*
     * This option is present so that the usage information will include the option.  It
     * is not actually used in this class and is handled by the property source loader.
     */
    @CommandLine.Option(
        names = ["--" + JavaBaseConstants.ARGS_CATALOG_KEY],
        description =
            [
                JavaBaseConstants.ARGS_CATALOG_DESC,
                "Required by the following commands: read, write",
            ],
    )
    lateinit var catalogFile: Optional<Path>

    @CommandLine.Option(
        names = ["--" + JavaBaseConstants.ARGS_STATE_KEY],
        description =
            [
                JavaBaseConstants.ARGS_PATH_DESC,
                "Required by the following commands: read",
            ],
    )
    lateinit var stateFile: Optional<Path>

    override fun run() {
        try {
            operation.execute()
        } finally {
            logger.info { "Completed integration: $connectorName" }
        }
    }

    @Value("\${micronaut.application.name}") lateinit var connectorName: String
    @Inject lateinit var operation: Operation
}
