/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk

import io.micronaut.core.cli.CommandLine as MicronautCommandLine
import io.airbyte.cdk.command.ConnectorCommandLinePropertySource
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility
import io.airbyte.cdk.integrations.util.ApmTraceUtils
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.configuration.picocli.MicronautFactory
import io.micronaut.context.ApplicationContext
import io.micronaut.context.ApplicationContextBuilder
import io.micronaut.context.env.CommandLinePropertySource
import io.micronaut.context.env.Environment
import picocli.CommandLine

/**
 * Replacement for the Micronaut CLI application runner that configures the CLI components and adds
 * the custom property source used to turn the arguments into configuration properties.
 */
class AirbyteConnectorRunner {

    enum class ConnectorType {
        SOURCE,
        DESTINATION
    }

    companion object {

        private val logger = KotlinLogging.logger {}

        @JvmStatic
        fun <R : Runnable> run(
            connectorType: ConnectorType,
            cls: Class<R>,
            vararg args: String,
        ) {
            val commandLine: MicronautCommandLine = MicronautCommandLine.parse(*args)
            val configPropertySource = ConnectorCommandLinePropertySource(commandLine)
            val commandLinePropertySource = CommandLinePropertySource(commandLine)
            val ctxBuilder: ApplicationContextBuilder =
                ApplicationContext.builder(cls, Environment.CLI, connectorType.name.lowercase())
                    .propertySources(configPropertySource, commandLinePropertySource)
            try {
                val ctx: ApplicationContext = ctxBuilder.start()
                run(cls, ctx, *args)
            } catch (e: Throwable) {
                logger.error(e) { "Unable to perform command." }
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

        @JvmStatic
        fun <R : Runnable> run(
            cls: Class<R>,
            ctx: ApplicationContext,
            vararg args: String,
        ) {
            CommandLine(cls, MicronautFactory(ctx)).execute(*args)
        }
    }
}
