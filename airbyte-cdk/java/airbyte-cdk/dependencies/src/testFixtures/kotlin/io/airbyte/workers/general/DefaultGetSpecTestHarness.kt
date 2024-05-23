/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.general

import io.airbyte.commons.io.LineGobbler
import io.airbyte.configoss.ConnectorJobOutput
import io.airbyte.configoss.FailureReason
import io.airbyte.configoss.JobGetSpecConfig
import io.airbyte.protocol.models.AirbyteMessage
import io.airbyte.workers.TestHarnessUtils
import io.airbyte.workers.exception.TestHarnessException
import io.airbyte.workers.internal.AirbyteStreamFactory
import io.airbyte.workers.internal.DefaultAirbyteStreamFactory
import io.airbyte.workers.process.IntegrationLauncher
import java.nio.file.Path
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class DefaultGetSpecTestHarness
@JvmOverloads
constructor(
    private val integrationLauncher: IntegrationLauncher,
    private val streamFactory: AirbyteStreamFactory = DefaultAirbyteStreamFactory()
) : GetSpecTestHarness {
    private lateinit var process: Process

    @Throws(TestHarnessException::class)
    override fun run(config: JobGetSpecConfig, jobRoot: Path): ConnectorJobOutput {
        try {
            val process = integrationLauncher.spec(jobRoot)
            this.process = process

            val jobOutput = ConnectorJobOutput().withOutputType(ConnectorJobOutput.OutputType.SPEC)
            LineGobbler.gobble(process!!.errorStream, { msg: String -> LOGGER.error(msg) })

            val messagesByType = TestHarnessUtils.getMessagesByType(process, streamFactory, 30)

            val spec =
                messagesByType
                    .getOrDefault(AirbyteMessage.Type.SPEC, ArrayList())!!
                    .map { obj: AirbyteMessage -> obj.spec }
                    .firstOrNull()

            val failureReason =
                TestHarnessUtils.getJobFailureReasonFromMessages(
                    ConnectorJobOutput.OutputType.SPEC,
                    messagesByType
                )
            failureReason!!.ifPresent { failureReason: FailureReason ->
                jobOutput.failureReason = failureReason
            }

            val exitCode = process!!.exitValue()
            if (exitCode != 0) {
                LOGGER.warn("Spec job subprocess finished with exit code {}", exitCode)
            }

            if (spec != null) {
                jobOutput.spec = spec
            } else if (failureReason.isEmpty) {
                TestHarnessUtils.throwWorkerException(
                    "Integration failed to output a spec struct and did not output a failure reason",
                    process
                )
            }

            return jobOutput
        } catch (e: Exception) {
            throw TestHarnessException(
                String.format("Error while getting spec from image %s", config.dockerImage),
                e
            )
        }
    }

    override fun cancel() {
        TestHarnessUtils.cancelProcess(process)
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(DefaultGetSpecTestHarness::class.java)
    }
}
