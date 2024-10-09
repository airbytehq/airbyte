/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util.destination_process

import io.airbyte.cdk.command.CliRunnable
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import java.io.PipedInputStream
import java.io.PipedOutputStream
import java.io.PrintWriter
import javax.inject.Singleton

class NonDockerizedDestination(
    command: String,
    config: ConfigurationSpecification?,
    catalog: ConfiguredAirbyteCatalog?,
    vararg featureFlags: FeatureFlag,
) : DestinationProcess {
    private val destinationStdinPipe: PrintWriter
    private val destination: CliRunnable

    init {
        val destinationStdin = PipedInputStream()
        // This could probably be a channel, somehow. But given the current structure,
        // it's easier to just use the pipe stuff.
        destinationStdinPipe =
            // spotbugs requires explicitly specifying the charset,
            // so we also have to specify autoFlush=false (i.e. the default behavior
            // from PrintWriter(outputStream) ).
            // Thanks, spotbugs.
            PrintWriter(PipedOutputStream(destinationStdin), false, Charsets.UTF_8)
        destination =
            CliRunner.destination(
                command,
                config = config,
                catalog = catalog,
                inputStream = destinationStdin,
                featureFlags = featureFlags,
            )
    }

    override fun run() {
        destination.run()
    }

    override fun sendMessage(message: AirbyteMessage) {
        destinationStdinPipe.println(Jsons.serialize(message))
    }

    override fun readMessages(): List<AirbyteMessage> = destination.results.newMessages()

    override fun shutdown() {
        destinationStdinPipe.close()
    }
}

// Notably, not actually a Micronaut factory. We want to inject the actual
// factory into our tests, not a pre-instantiated destination, because we want
// to run multiple destination processes per test.
// TODO only inject this when not running in CI, a la @Requires(notEnv = "CI_master_merge")
@Singleton
class NonDockerizedDestinationFactory : DestinationProcessFactory {
    override fun createDestinationProcess(
        command: String,
        config: ConfigurationSpecification?,
        catalog: ConfiguredAirbyteCatalog?,
        vararg featureFlags: FeatureFlag,
    ): DestinationProcess {
        return NonDockerizedDestination(command, config, catalog, *featureFlags)
    }
}
