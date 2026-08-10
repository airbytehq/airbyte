/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.fixtures.legacy

import io.airbyte.protocol.models.v0.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Path

private val LOGGER = KotlinLogging.logger {}

class DefaultCheckConnectionTestHarness
@JvmOverloads
constructor(
    private val integrationLauncher: IntegrationLauncher,
    private val connectorConfigUpdater: ConnectorConfigUpdater,
    private val streamFactory: AirbyteStreamFactory = DefaultAirbyteStreamFactory()
) : CheckConnectionTestHarness {
    private lateinit var process: Process

    @Throws(TestHarnessException::class)
    override fun run(inputType: StandardCheckConnectionInput, jobRoot: Path): ConnectorJobOutput {
        LineGobbler.startSection("CHECK")

        try {
            val inputConfig = inputType.connectionConfiguration!!
            val process =
                integrationLauncher.check(
                    jobRoot,
                    WorkerConstants.SOURCE_CONFIG_JSON_FILENAME,
                    Jsons.serialize(inputConfig)
                )
            this.process = process

            val jobOutput =
                ConnectorJobOutput().withOutputType(ConnectorJobOutput.OutputType.CHECK_CONNECTION)

            LineGobbler.gobble(process.errorStream, { msg: String -> LOGGER.error { msg } })

            val messagesByType = TestHarnessUtils.getMessagesByType(process, streamFactory, 30)
            val connectionStatus =
                messagesByType
                    .getOrDefault(AirbyteMessage.Type.CONNECTION_STATUS, ArrayList())
                    .map { obj: AirbyteMessage -> obj.connectionStatus }
                    .firstOrNull()

            if (inputType.actorId != null && inputType.actorType != null) {
                val optionalConfigMsg =
                    TestHarnessUtils.getMostRecentConfigControlMessage(messagesByType)
                if (
                    optionalConfigMsg.isPresent &&
                        TestHarnessUtils.getDidControlMessageChangeConfig(
                            inputConfig,
                            optionalConfigMsg.get()
                        )
                ) {
                    when (inputType.actorType!!) {
                        ActorType.SOURCE ->
                            connectorConfigUpdater.updateSource(
                                inputType.actorId,
                                optionalConfigMsg.get().config
                            )
                        ActorType.DESTINATION ->
                            connectorConfigUpdater.updateDestination(
                                inputType.actorId,
                                optionalConfigMsg.get().config
                            )
                    }
                    jobOutput.connectorConfigurationUpdated = true
                }
            }

            val failureReason =
                TestHarnessUtils.getJobFailureReasonFromMessages(
                    ConnectorJobOutput.OutputType.CHECK_CONNECTION,
                    messagesByType
                )
            failureReason.ifPresent { jobOutput.failureReason = it }

            val exitCode = process.exitValue()
            if (exitCode != 0) {
                LOGGER.warn { "Check connection job subprocess finished with exit code $exitCode" }
            }

            if (connectionStatus != null) {
                val output =
                    StandardCheckConnectionOutput()
                        .withStatus(
                            Enums.convertTo(
                                connectionStatus.status,
                                StandardCheckConnectionOutput.Status::class.java
                            )
                        )
                        .withMessage(connectionStatus.message)
                LOGGER.info { "Check connection job received output: $output" }
                jobOutput.checkConnection = output
            } else if (failureReason.isEmpty) {
                TestHarnessUtils.throwWorkerException(
                    "Error checking connection status: no status nor failure reason were outputted",
                    process
                )
            }
            LineGobbler.endSection("CHECK")
            return jobOutput
        } catch (e: Exception) {
            LOGGER.error(e) { "Unexpected error while checking connection: " }
            LineGobbler.endSection("CHECK")
            throw TestHarnessException("Unexpected error while getting checking connection.", e)
        }
    }

    override fun cancel() {
        TestHarnessUtils.cancelProcess(process)
    }
}
