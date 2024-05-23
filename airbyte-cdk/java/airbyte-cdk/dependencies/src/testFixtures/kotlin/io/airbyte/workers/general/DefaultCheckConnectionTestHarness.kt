/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.general

import io.airbyte.commons.enums.Enums
import io.airbyte.commons.io.LineGobbler
import io.airbyte.commons.json.Jsons
import io.airbyte.configoss.*
import io.airbyte.protocol.models.AirbyteMessage
import io.airbyte.workers.TestHarnessUtils
import io.airbyte.workers.WorkerConstants
import io.airbyte.workers.exception.TestHarnessException
import io.airbyte.workers.helper.ConnectorConfigUpdater
import io.airbyte.workers.internal.AirbyteStreamFactory
import io.airbyte.workers.internal.DefaultAirbyteStreamFactory
import io.airbyte.workers.process.IntegrationLauncher
import java.nio.file.Path
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class DefaultCheckConnectionTestHarness
@JvmOverloads
constructor(
    private val integrationLauncher: IntegrationLauncher,
    private val connectorConfigUpdater: ConnectorConfigUpdater,
    private val streamFactory: AirbyteStreamFactory = DefaultAirbyteStreamFactory()
) : CheckConnectionTestHarness {
    private lateinit var process: Process

    @Throws(TestHarnessException::class)
    override fun run(input: StandardCheckConnectionInput, jobRoot: Path): ConnectorJobOutput {
        LineGobbler.startSection("CHECK")

        try {
            val inputConfig = input.connectionConfiguration
            val process =
                integrationLauncher.check(
                    jobRoot,
                    WorkerConstants.SOURCE_CONFIG_JSON_FILENAME,
                    Jsons.serialize(inputConfig)
                )
            this.process = process

            val jobOutput =
                ConnectorJobOutput().withOutputType(ConnectorJobOutput.OutputType.CHECK_CONNECTION)

            LineGobbler.gobble(process.errorStream, { msg: String -> LOGGER.error(msg) })

            val messagesByType = TestHarnessUtils.getMessagesByType(process, streamFactory, 30)
            val connectionStatus =
                messagesByType
                    .getOrDefault(AirbyteMessage.Type.CONNECTION_STATUS, ArrayList())
                    .stream()
                    .map { obj: AirbyteMessage -> obj.connectionStatus }
                    .findFirst()

            if (input.actorId != null && input.actorType != null) {
                val optionalConfigMsg =
                    TestHarnessUtils.getMostRecentConfigControlMessage(messagesByType)
                if (
                    optionalConfigMsg.isPresent &&
                        TestHarnessUtils.getDidControlMessageChangeConfig(
                            inputConfig,
                            optionalConfigMsg.get()
                        )
                ) {
                    when (input.actorType) {
                        ActorType.SOURCE ->
                            connectorConfigUpdater.updateSource(
                                input.actorId,
                                optionalConfigMsg.get().config
                            )
                        ActorType.DESTINATION ->
                            connectorConfigUpdater.updateDestination(
                                input.actorId,
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
            failureReason.ifPresent { failureReason: FailureReason ->
                jobOutput.failureReason = failureReason
            }

            val exitCode = process.exitValue()
            if (exitCode != 0) {
                LOGGER.warn("Check connection job subprocess finished with exit code {}", exitCode)
            }

            if (connectionStatus.isPresent) {
                val output =
                    StandardCheckConnectionOutput()
                        .withStatus(
                            Enums.convertTo(
                                connectionStatus.get().status,
                                StandardCheckConnectionOutput.Status::class.java
                            )
                        )
                        .withMessage(connectionStatus.get().message)
                LOGGER.info("Check connection job received output: {}", output)
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
            LOGGER.error("Unexpected error while checking connection: ", e)
            LineGobbler.endSection("CHECK")
            throw TestHarnessException("Unexpected error while getting checking connection.", e)
        }
    }

    override fun cancel() {
        TestHarnessUtils.cancelProcess(process)
    }

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(DefaultCheckConnectionTestHarness::class.java)
    }
}
