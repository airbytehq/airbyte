/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util.destination_process

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.micronaut.context.env.yaml.YamlPropertySourceLoader
import java.nio.file.Files
import java.nio.file.Path

const val DOCKERIZED_TEST_ENV = "DOCKERIZED_INTEGRATION_TEST"

/**
 * Represents a destination process, whether running in-JVM via micronaut, or as a separate Docker
 * container. The general lifecycle is:
 * 1. `val dest = DestinationProcessFactory.createDestinationProcess(...)`
 * 2. `launch { dest.run() }`
 * 3. [sendMessage] as many times as you want
 * 4. [readMessages] as needed (e.g. to check that state messages are emitted during the sync)
 * 5. [shutdown] once you have no more messages to send to the destination
 */
interface DestinationProcess {
    /**
     * Run the destination process. Callers who want to interact with the destination should
     * `launch` this method.
     */
    suspend fun run()

    fun sendMessage(message: AirbyteMessage)
    fun sendMessages(vararg messages: AirbyteMessage) {
        messages.forEach { sendMessage(it) }
    }

    /** Return all messages the destination emitted since the last call to [readMessages]. */
    fun readMessages(): List<AirbyteMessage>

    /**
     * Signal the destination to exit (i.e. close its stdin stream), then wait for it to terminate.
     */
    suspend fun shutdown()
}

@SuppressFBWarnings("NP_NONNULL_RETURN_VIOLATION", "good old lateinit")
abstract class DestinationProcessFactory {
    /**
     * Ideally we'd take this in the constructor, but that's annoying because of how junit injects
     * TestInfo, and how Micronaut injects everything else. Instead, we'll rely on [IntegrationTest]
     * to set this in a BeforeEach function.
     */
    lateinit var testName: String

    abstract fun createDestinationProcess(
        command: String,
        config: ConfigurationSpecification? = null,
        catalog: ConfiguredAirbyteCatalog? = null,
        vararg featureFlags: FeatureFlag,
    ): DestinationProcess

    companion object {
        fun get(): DestinationProcessFactory =
            when (val runner = System.getenv("AIRBYTE_CONNECTOR_INTEGRATION_TEST_RUNNER")) {
                null,
                "non-docker" -> NonDockerizedDestinationFactory()
                "docker" -> {
                    val rawProperties: Map<String, Any?> =
                        YamlPropertySourceLoader()
                            .read(
                                "irrelevant",
                                Files.readAllBytes(Path.of("metadata.yaml")),
                            )
                    DockerizedDestinationFactory(
                        rawProperties["data.dockerRepository"] as String,
                        "dev"
                    )
                }
                else ->
                    throw IllegalArgumentException(
                        "Unknown AIRBYTE_CONNECTOR_INTEGRATION_TEST_RUNNER environment variable: $runner"
                    )
            }
    }
}
