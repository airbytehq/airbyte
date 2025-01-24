/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk

import io.airbyte.cdk.command.ConnectorCommandLinePropertySource
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.command.MetadataYamlPropertySource
import io.micronaut.configuration.picocli.MicronautFactory
import io.micronaut.context.ApplicationContext
import io.micronaut.context.RuntimeBeanDefinition
import io.micronaut.context.env.CommandLinePropertySource
import io.micronaut.context.env.Environment
import io.micronaut.core.cli.CommandLine as MicronautCommandLine
import java.nio.file.Path
import kotlin.system.exitProcess
import picocli.CommandLine
import picocli.CommandLine.Model.ArgGroupSpec
import picocli.CommandLine.Model.OptionSpec
import picocli.CommandLine.Model.UsageMessageSpec

// A micronaut environment, so that connectors can override micronaut properties
// without needing to copy an entire application.yaml out of the core CDK.
// Intended usage is for connectors to create
// `destination-foo/src/main/resources/application-connector.yaml` with the
// specific properties to override.
const val CONNECTOR_OVERRIDE_ENV = "connector"

/** Source connector entry point. */
class AirbyteSourceRunner(
    /** CLI args. */
    args: Array<out String>,
    /** Environment variables. */
    systemEnv: Map<String, String> = System.getenv(),
    /** Micronaut bean definition overrides, used only for tests. */
    vararg testBeanDefinitions: RuntimeBeanDefinition<*>,
) : AirbyteConnectorRunner("source", args, systemEnv, testBeanDefinitions) {
    companion object {
        @JvmStatic
        fun run(vararg args: String) {
            AirbyteSourceRunner(args).run<AirbyteConnectorRunnable>()
        }
    }
}

/** Destination connector entry point. */
class AirbyteDestinationRunner(
    /** CLI args. */
    args: Array<out String>,
    /** Environment variables. */
    systemEnv: Map<String, String> = System.getenv(),
    /** Micronaut bean definition overrides, used only for tests. */
    vararg testBeanDefinitions: RuntimeBeanDefinition<*>,
) : AirbyteConnectorRunner("destination", args, systemEnv, testBeanDefinitions) {
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
    val connectorType: String,
    val args: Array<out String>,
    systemEnv: Map<String, String>,
    val testBeanDefinitions: Array<out RuntimeBeanDefinition<*>>,
) {
    val envs: Array<String> =
        arrayOf(Environment.CLI, connectorType) +
            // Set feature flag environments.
            FeatureFlag.active(systemEnv).map { it.micronautEnvironmentName } +
            // Micronaut's TEST env detection relies on inspecting the stacktrace and checking for
            // any junit calls. This doesn't work if we launch the connector from a different
            // thread, e.g. `Dispatchers.IO`. Force the test env if needed. Some tests launch the
            // connector from the IO context to avoid blocking themselves.
            listOfNotNull(Environment.TEST.takeIf { testBeanDefinitions.isNotEmpty() })

    inline fun <reified R : Runnable> run() {
        val picocliCommandLineFactory = PicocliCommandLineFactory(this)
        val micronautCommandLine: MicronautCommandLine = MicronautCommandLine.parse(*args)
        val airbytePropertySource =
            ConnectorCommandLinePropertySource(
                micronautCommandLine,
                picocliCommandLineFactory.commands.options().map { it.longestName() },
            )
        val commandLinePropertySource = CommandLinePropertySource(micronautCommandLine)
        val ctx: ApplicationContext =
        // note that we put the override envs last.
        // This ensures that micronaut gives those environments precedence
        // (because the last environment's application-XYZ.yaml wins).
        ApplicationContext.builder(R::class.java, *envs, CONNECTOR_OVERRIDE_ENV)
                .propertySources(
                    *listOfNotNull(
                            airbytePropertySource,
                            commandLinePropertySource,
                            MetadataYamlPropertySource(),
                        )
                        .toTypedArray(),
                )
                .beanDefinitions(*testBeanDefinitions)
                .start()
        val isTest: Boolean = ctx.environment.activeNames.contains(Environment.TEST)
        val picocliFactory: CommandLine.IFactory = MicronautFactory(ctx)
        val picocliCommandLine: CommandLine =
            picocliCommandLineFactory.build<AirbyteConnectorRunnable>(picocliFactory)
        val exitCode: Int = picocliCommandLine.execute(*args)
        if (!isTest) {
            // Required by the platform, otherwise syncs may hang.
            exitProcess(exitCode)
        }
        // At this point, we're in a test.
        if (exitCode != 0) {
            // Propagate failure to test callers.
            throw ConnectorUncleanExitException(exitCode)
        }
    }
}

/** Encapsulates all picocli logic. Defines the grammar for the CLI. */
class PicocliCommandLineFactory(
    val runner: AirbyteConnectorRunner,
) {
    inline fun <reified R : Runnable> build(factory: CommandLine.IFactory): CommandLine {
        val commandSpec: CommandLine.Model.CommandSpec =
            CommandLine.Model.CommandSpec.wrapWithoutInspection(R::class.java, factory)
                .name("airbyte-${runner.connectorType}-connector")
                .usageMessage(usageMessageSpec)
                .mixinStandardHelpOptions(true)
                .addArgGroup(commands)
                .addOption(config)
                .addOption(catalog)
                .addOption(state)
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
                "@|magenta                    /____/              |@",
            )
            .description("Executes an Airbyte ${runner.connectorType} connector.")

    fun command(
        name: String,
        description: String,
    ): OptionSpec = OptionSpec.builder("--$name").description(description).arity("0").build()

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
                when (runner) {
                    is AirbyteSourceRunner -> addArg(discover).addArg(read)
                    is AirbyteDestinationRunner -> addArg(write)
                }
            }
            .build()

    fun fileOption(
        name: String,
        vararg description: String,
    ): OptionSpec =
        OptionSpec.builder("--$name")
            .description(*description)
            .type(Path::class.java)
            .arity("1")
            .build()

    val config: OptionSpec =
        fileOption(
            "config",
            "path to the json configuration file",
            "Required by the following commands: check, discover, read, write",
        )
    val catalog: OptionSpec =
        fileOption(
            "catalog",
            "input path for the catalog",
            "Required by the following commands: read, write",
        )
    val state: OptionSpec =
        fileOption(
            "state",
            "path to the json-encoded state file",
            "Required by the following commands: read",
        )
}
