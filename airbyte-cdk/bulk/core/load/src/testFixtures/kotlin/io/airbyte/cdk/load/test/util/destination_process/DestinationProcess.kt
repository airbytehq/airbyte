/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util.destination_process

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog

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
    fun run()

    fun sendMessage(message: AirbyteMessage)

    /** Return all messages the destination emitted since the last call to [readMessages]. */
    fun readMessages(): List<AirbyteMessage>

    /**
     * Wait for the destination to terminate, then return all messages it emitted since the last
     * call to [readMessages].
     */
    fun shutdown()
}

enum class TestDeploymentMode {
    CLOUD,
    OSS
}

interface DestinationProcessFactory {
    fun createDestinationProcess(
        command: String,
        config: ConfigurationSpecification? = null,
        catalog: ConfiguredAirbyteCatalog? = null,
        deploymentMode: TestDeploymentMode = TestDeploymentMode.OSS,
    ): DestinationProcess
}
