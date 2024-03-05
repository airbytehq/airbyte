/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.core.context

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.micronaut.configuration.picocli.MicronautFactory
import io.micronaut.context.ApplicationContext
import io.micronaut.context.ApplicationContextBuilder
import io.micronaut.context.env.CommandLinePropertySource
import io.micronaut.context.env.Environment
import io.micronaut.core.cli.CommandLine as MicronautCommandLine
import picocli.CommandLine

/**
 * Replacement for the Micronaut CLI application runner that configures the CLI components and adds
 * the custom property source used to turn the arguments into configuration properties. <p/> Main
 * classes should use this class as follows: <code>
 * ```
 *     public static void main(final String[] args) {
 *         AirbyteConnectorRunner.run(IntegrationCommand.class, args);
 *     }
 * ```
 * </code>
 */
class AirbyteConnectorRunner {
    companion object {
        fun <R : Runnable> run(
            cls: Class<R>,
            vararg args: String,
        ) {
            buildApplicationContext(cls, args).start().use { ctx -> run(cls, ctx, *args) }
        }

        fun <R : Runnable> run(
            cls: Class<R>,
            ctx: ApplicationContext,
            vararg args: String,
        ) {
            val commandLine = CommandLine(cls, MicronautFactory(ctx))
            commandLine.execute(*args)
        }

        private fun buildApplicationContext(
            cls: Class<*>,
            args: Array<out String>,
        ): ApplicationContextBuilder {
            val commandLine: MicronautCommandLine = MicronautCommandLine.parse(*args)
            val connectorConfigurationPropertySource =
                ConnectorConfigurationPropertySource(commandLine)
            val commandLinePropertySource = CommandLinePropertySource(commandLine)
            return ApplicationContext.builder(cls, Environment.CLI)
                .propertySources(connectorConfigurationPropertySource, commandLinePropertySource)
        }
    }
}
