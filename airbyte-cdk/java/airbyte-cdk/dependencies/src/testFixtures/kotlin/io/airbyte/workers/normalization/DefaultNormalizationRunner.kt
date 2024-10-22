/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.normalization

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.base.Strings
import com.google.common.collect.ImmutableMap
import io.airbyte.commons.io.IOs
import io.airbyte.commons.io.LineGobbler
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.logging.LoggingHelper
import io.airbyte.commons.logging.MdcScope
import io.airbyte.configoss.OperatorDbt
import io.airbyte.configoss.ResourceRequirements
import io.airbyte.protocol.models.AirbyteErrorTraceMessage
import io.airbyte.protocol.models.AirbyteMessage
import io.airbyte.protocol.models.AirbyteTraceMessage
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog
import io.airbyte.workers.TestHarnessUtils
import io.airbyte.workers.WorkerConstants
import io.airbyte.workers.exception.TestHarnessException
import io.airbyte.workers.process.Metadata
import io.airbyte.workers.process.ProcessFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Path
import java.util.*
import java.util.concurrent.TimeUnit
import java.util.function.Function
import java.util.stream.Collectors
import java.util.stream.Stream

private val LOGGER = KotlinLogging.logger {}

class DefaultNormalizationRunner(
    private val processFactory: ProcessFactory,
    private val normalizationImageName: String?,
    private val normalizationIntegrationType: String?
) : NormalizationRunner {
    private val streamFactory = NormalizationAirbyteStreamFactory(CONTAINER_LOG_MDC_BUILDER)
    private var airbyteMessagesByType: MutableMap<AirbyteMessage.Type, List<AirbyteMessage>> =
        HashMap()
    private var dbtErrorStack: String? = null

    private var process: Process? = null

    @Throws(Exception::class)
    override fun configureDbt(
        jobId: String,
        attempt: Int,
        jobRoot: Path,
        config: JsonNode?,
        resourceRequirements: ResourceRequirements?,
        dbtConfig: OperatorDbt
    ): Boolean {
        val files: Map<String?, String?> =
            ImmutableMap.of(
                WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME,
                Jsons.serialize(config)
            )
        val gitRepoUrl = dbtConfig.gitRepoUrl
        if (Strings.isNullOrEmpty(gitRepoUrl)) {
            throw TestHarnessException("Git Repo Url is required")
        }
        val gitRepoBranch = dbtConfig.gitRepoBranch
        return if (Strings.isNullOrEmpty(gitRepoBranch)) {
            runProcess(
                jobId,
                attempt,
                jobRoot,
                files,
                resourceRequirements,
                "configure-dbt",
                "--integration-type",
                normalizationIntegrationType!!.lowercase(Locale.getDefault()),
                "--config",
                WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME,
                "--git-repo",
                gitRepoUrl
            )
        } else {
            runProcess(
                jobId,
                attempt,
                jobRoot,
                files,
                resourceRequirements,
                "configure-dbt",
                "--integration-type",
                normalizationIntegrationType!!.lowercase(Locale.getDefault()),
                "--config",
                WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME,
                "--git-repo",
                gitRepoUrl,
                "--git-branch",
                gitRepoBranch
            )
        }
    }

    @Throws(Exception::class)
    override fun normalize(
        jobId: String,
        attempt: Int,
        jobRoot: Path,
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        resourceRequirements: ResourceRequirements?
    ): Boolean {
        val files: Map<String?, String?> =
            ImmutableMap.of(
                WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME,
                Jsons.serialize(config),
                WorkerConstants.DESTINATION_CATALOG_JSON_FILENAME,
                Jsons.serialize(catalog)
            )

        return runProcess(
            jobId,
            attempt,
            jobRoot,
            files,
            resourceRequirements,
            "run",
            "--integration-type",
            normalizationIntegrationType!!.lowercase(Locale.getDefault()),
            "--config",
            WorkerConstants.DESTINATION_CONFIG_JSON_FILENAME,
            "--catalog",
            WorkerConstants.DESTINATION_CATALOG_JSON_FILENAME
        )
    }

    @Throws(Exception::class)
    private fun runProcess(
        jobId: String,
        attempt: Int,
        jobRoot: Path,
        files: Map<String?, String?>,
        resourceRequirements: ResourceRequirements?,
        vararg args: String
    ): Boolean {
        try {
            LOGGER.info("Running with normalization version: {}", normalizationImageName)
            var process =
                processFactory.create(
                    Metadata.NORMALIZE_STEP,
                    jobId,
                    attempt,
                    jobRoot,
                    normalizationImageName!!, // custom connector does not use normalization
                    false,
                    false,
                    files,
                    null,
                    resourceRequirements,
                    null,
                    java.util.Map.of(
                        Metadata.JOB_TYPE_KEY,
                        Metadata.SYNC_JOB,
                        Metadata.SYNC_STEP_KEY,
                        Metadata.NORMALIZE_STEP
                    ),
                    emptyMap(),
                    emptyMap(),
                    emptyMap(),
                    *args
                )
            this.process = process

            process.inputStream.use { stdout ->
                // finds and collects any AirbyteMessages from stdout
                // also builds a list of raw dbt errors and stores in streamFactory
                airbyteMessagesByType =
                    streamFactory
                        .create(IOs.newBufferedReader(stdout))
                        .collect(
                            Collectors.groupingBy(Function { obj: AirbyteMessage -> obj.type })
                        )

                // picks up error logs from dbt
                dbtErrorStack = java.lang.String.join("\n", streamFactory.dbtErrors)
                if ("" != dbtErrorStack) {
                    val dbtTraceMessage =
                        AirbyteMessage()
                            .withType(AirbyteMessage.Type.TRACE)
                            .withTrace(
                                AirbyteTraceMessage()
                                    .withType(AirbyteTraceMessage.Type.ERROR)
                                    .withEmittedAt(System.currentTimeMillis().toDouble())
                                    .withError(
                                        AirbyteErrorTraceMessage()
                                            .withFailureType(
                                                AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR
                                            ) // TODO: decide on best FailureType for this
                                            .withMessage(
                                                "Normalization failed during the dbt run. This may indicate a problem with the data itself."
                                            ) // due to the lack of consistent defining features in
                                            // dbt errors we're injecting a breadcrumb to the
                                            // stacktrace so we can confidently identify all dbt
                                            // errors when parsing and sending to Sentry
                                            // see dbt error examples:
                                            // https://docs.getdbt.com/guides/legacy/debugging-errors for more context
                                            .withStackTrace("AirbyteDbtError: \n$dbtErrorStack")
                                    )
                            )

                    airbyteMessagesByType.putIfAbsent(
                        AirbyteMessage.Type.TRACE,
                        java.util.List.of(dbtTraceMessage)
                    )
                }
            }
            LineGobbler.gobble(
                process.errorStream,
                { msg: String -> LOGGER.error(msg) },
                CONTAINER_LOG_MDC_BUILDER
            )

            TestHarnessUtils.wait(process)

            return process.exitValue() == 0
        } catch (e: Exception) {
            // make sure we kill the process on failure to avoid zombies.
            process?.let { TestHarnessUtils.cancelProcess(process) }
            throw e
        }
    }

    @Throws(Exception::class)
    override fun close() {
        process?.let {
            LOGGER.info("Terminating normalization process...")
            TestHarnessUtils.gentleClose(it, 1, TimeUnit.MINUTES)

            /*
             * After attempting to close the process check the following:
             *
             * Did the process actually terminate? If "yes", did it do so nominally?
             */
            if (it.isAlive) {
                throw TestHarnessException(
                    "Normalization process did not terminate after 1 minute."
                )
            } else if (it.exitValue() != 0) {
                throw TestHarnessException(
                    "Normalization process did not terminate normally (exit code: " +
                        it.exitValue() +
                        ")"
                )
            } else {
                LOGGER.info("Normalization process successfully terminated.")
            }
        }
    }

    override val traceMessages: Stream<AirbyteTraceMessage>
        get() {
            if (airbyteMessagesByType[AirbyteMessage.Type.TRACE] != null) {
                return airbyteMessagesByType[AirbyteMessage.Type.TRACE]!!
                    .map { obj: AirbyteMessage -> obj.trace }
                    .stream()
            }
            return Stream.empty()
        }

    companion object {

        private val CONTAINER_LOG_MDC_BUILDER: MdcScope.Builder =
            MdcScope.Builder()
                .setLogPrefix("normalization")
                .setPrefixColor(LoggingHelper.Color.GREEN_BACKGROUND)
    }
}
