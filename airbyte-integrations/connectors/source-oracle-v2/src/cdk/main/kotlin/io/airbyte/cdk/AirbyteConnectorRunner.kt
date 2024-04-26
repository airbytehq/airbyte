/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk

import io.airbyte.cdk.command.ConnectorCommandLinePropertySource
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.util.ApmTraceUtils
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil
import io.micronaut.configuration.picocli.MicronautFactory
import io.micronaut.context.ApplicationContext
import io.micronaut.context.env.CommandLinePropertySource
import io.micronaut.context.env.Environment
import io.micronaut.core.cli.CommandLine as MicronautCommandLine
import java.nio.file.Path
import picocli.CommandLine
import picocli.CommandLine.Model.ArgGroupSpec
import picocli.CommandLine.Model.OptionSpec
import picocli.CommandLine.Model.UsageMessageSpec

/** Source connector entry point. */
class AirbyteSourceRunner(args: Array<out String>) :
    AirbyteConnectorRunner(ConnectorType.SOURCE, args) {

    companion object {
        @JvmStatic
        fun run(vararg args: String) {
            AirbyteSourceRunner(args).run<AirbyteConnectorRunnable>()
        }
    }
}

/** Destination connector entry point. */
class AirbyteDestinationRunner(args: Array<out String>) :
    AirbyteConnectorRunner(ConnectorType.DESTINATION, args) {

    companion object {
        @JvmStatic
        fun run(vararg args: String) {
            AirbyteDestinationRunner(args).run<AirbyteConnectorRunnable>()
        }
    }
}

/**
 * Replacement for the Micronaut CLI application runner that configures the CLI components and adds
 * the custom property source used to turn the arguments into configuration properties.
 */
sealed class AirbyteConnectorRunner(
    val connectorType: ConnectorType,
    val args: Array<out String>,
) {

    val envs: Array<String> = arrayOf(Environment.CLI, connectorType.name.lowercase())

    inline fun <reified R : Runnable> run() {
        val micronautCommandLine: MicronautCommandLine = MicronautCommandLine.parse(*args)
        val configPropertySource = ConnectorCommandLinePropertySource(micronautCommandLine)
        val commandLinePropertySource = CommandLinePropertySource(micronautCommandLine)
        val ctx: ApplicationContext =
            ApplicationContext.builder(R::class.java, *envs)
                .propertySources(configPropertySource, commandLinePropertySource)
                .start()
        val isTest: Boolean = ctx.environment.activeNames.contains(Environment.TEST)
        val picocliFactory: CommandLine.IFactory = MicronautFactory(ctx)
        val picocliCommandLine: CommandLine =
            PicocliCommandLineFactory(connectorType, isTest)
                .build<AirbyteConnectorRunnable>(picocliFactory)
        try {
            picocliCommandLine.execute(*args)
        } catch (e: Throwable) {
            // Many of the exceptions thrown are nested inside layers of RuntimeExceptions. An
            // attempt is made to find the root exception that corresponds to a configuration
            // error. If that does not exist, we just return the original exception.
            ApmTraceUtils.addExceptionToTrace(e)
            val rootThrowable = ConnectorExceptionUtil.getRootConfigError(Exception(e))
            val displayMessage = ConnectorExceptionUtil.getDisplayMessage(rootThrowable)
            // If the connector throws a config error, a trace message with the relevant
            // message should be surfaced.
            if (ConnectorExceptionUtil.isConfigError(rootThrowable)) {
                AirbyteTraceMessageUtility.emitConfigErrorTrace(e, displayMessage)
            }
        }
    }
}

enum class ConnectorType {
    SOURCE,
    DESTINATION
}

/** Encapsulates all picocli logic. Defines the grammar for the CLI. */
class PicocliCommandLineFactory(
    val connectorType: ConnectorType,
    val isTest: Boolean,
) {

    inline fun <reified R : Runnable> build(factory: CommandLine.IFactory): CommandLine {
        val commandSpec: CommandLine.Model.CommandSpec =
            CommandLine.Model.CommandSpec.wrapWithoutInspection(R::class.java, factory)
                .name("airbyte-${connectorType.name.lowercase()}-connector")
                .usageMessage(usageMessageSpec)
                .mixinStandardHelpOptions(true)
                .addArgGroup(commands)
                .addOption(config)
                .addOption(catalog)
                .addOption(state)

        if (isTest) {
            commandSpec.addOption(output)
        }
        return CommandLine(commandSpec, factory)
    }

    val usageMessageSpec: UsageMessageSpec =
        UsageMessageSpec()
            .header(
                "@|magenta     ___    _      __          __       |@",
                "@|magenta    /   |  (_)____/ /_  __  __/ /____   |@",
                "@|magenta   / /| | / / ___/ __ \\/ / / / __/ _   |@",
                "@|magenta  / ___ |/ / /  / /_/ / /_/ / /_/  __/  |@",
                "@|magenta /_/  |_/_/_/  /_.___/\\__, /\\__/\\___/|@",
                "@|magenta                    /____/              |@"
            )
            .description("Executes an Airbyte ${connectorType.name.lowercase()} connector.")

    fun command(name: String, description: String): OptionSpec =
        OptionSpec.builder("--$name").description(description).arity("0").build()
    val spec: OptionSpec = command("spec", "outputs the json configuration specification")
    val check: OptionSpec = command("check", "checks the config can be used to connect")
    val discover: OptionSpec =
        command("discover", "outputs a catalog describing the source's catalog")
    val read: OptionSpec = command("read", "reads the source and outputs messages to STDOUT")
    val write: OptionSpec = command("write", "writes messages from STDIN to the integration")

    val commands: ArgGroupSpec =
        ArgGroupSpec.builder()
            .multiplicity("1")
            .exclusive(true)
            .addArg(spec)
            .addArg(check)
            .apply {
                when (connectorType) {
                    ConnectorType.SOURCE -> addArg(discover).addArg(read)
                    ConnectorType.DESTINATION -> addArg(write)
                }
            }
            .build()

    fun fileOption(name: String, vararg description: String): OptionSpec =
        OptionSpec.builder("--$name")
            .description(*description)
            .type(Path::class.java)
            .arity("1")
            .build()
    val config: OptionSpec =
        fileOption(
            JavaBaseConstants.ARGS_CONFIG_KEY,
            JavaBaseConstants.ARGS_CONFIG_DESC,
            "Required by the following commands: check, discover, read, write"
        )
    val catalog: OptionSpec =
        fileOption(
            JavaBaseConstants.ARGS_CATALOG_KEY,
            JavaBaseConstants.ARGS_CATALOG_DESC,
            "Required by the following commands: read, write"
        )
    val state: OptionSpec =
        fileOption(
            JavaBaseConstants.ARGS_STATE_KEY,
            JavaBaseConstants.ARGS_PATH_DESC,
            "Required by the following commands: read"
        )
    val output: OptionSpec =
        fileOption(
            "output",
            "path to the output file",
            "When present, the connector writes to this file instead of stdout"
        )
}
