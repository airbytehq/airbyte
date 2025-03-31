/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import io.airbyte.protocol.models.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Path

private val LOGGER = KotlinLogging.logger {}

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

    companion object {}
}
