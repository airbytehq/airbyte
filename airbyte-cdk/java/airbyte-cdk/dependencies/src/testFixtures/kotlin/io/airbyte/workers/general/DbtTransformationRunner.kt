/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.general

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.base.Strings
import com.google.common.collect.ImmutableMap
import io.airbyte.commons.io.LineGobbler
import io.airbyte.commons.logging.LoggingHelper
import io.airbyte.commons.logging.MdcScope
import io.airbyte.commons.resources.MoreResources
import io.airbyte.configoss.OperatorDbt
import io.airbyte.configoss.ResourceRequirements
import io.airbyte.workers.TestHarnessUtils
import io.airbyte.workers.exception.TestHarnessException
import io.airbyte.workers.normalization.NormalizationRunner
import io.airbyte.workers.process.Metadata
import io.airbyte.workers.process.ProcessFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Path
import java.util.*
import java.util.concurrent.TimeUnit
import org.apache.tools.ant.types.Commandline

private val LOGGER = KotlinLogging.logger {}

class DbtTransformationRunner(
    private val processFactory: ProcessFactory,
    private val normalizationRunner: NormalizationRunner
) : AutoCloseable {
    private lateinit var process: Process

    @Throws(Exception::class)
    fun start() {
        normalizationRunner.start()
    }

    /**
     * The docker image used by the DbtTransformationRunner is provided by the User, so we can't
     * ensure to have the right python, dbt, dependencies etc software installed to successfully run
     * our transform-config scripts (to translate Airbyte Catalogs into Dbt profiles file). Thus, we
     * depend on the NormalizationRunner to configure the dbt project with the appropriate
     * destination settings and pull the custom git repository into the workspace.
     *
     * Once the workspace folder/files is setup to run, we invoke the custom transformation command
     * as provided by the user to execute whatever extra transformation has been implemented.
     */
    @Throws(Exception::class)
    fun run(
        jobId: String,
        attempt: Int,
        jobRoot: Path,
        config: JsonNode?,
        resourceRequirements: ResourceRequirements?,
        dbtConfig: OperatorDbt
    ): Boolean {
        if (
            !normalizationRunner.configureDbt(
                jobId,
                attempt,
                jobRoot,
                config,
                resourceRequirements,
                dbtConfig
            )
        ) {
            return false
        }
        return transform(jobId, attempt, jobRoot, config, resourceRequirements, dbtConfig)
    }

    @Throws(Exception::class)
    fun transform(
        jobId: String,
        attempt: Int,
        jobRoot: Path,
        config: JsonNode?,
        resourceRequirements: ResourceRequirements?,
        dbtConfig: OperatorDbt
    ): Boolean {
        try {
            val files: Map<String?, String?> =
                ImmutableMap.of(
                    DBT_ENTRYPOINT_SH,
                    MoreResources.readResource("dbt_transformation_entrypoint.sh"),
                    "sshtunneling.sh",
                    MoreResources.readResource("sshtunneling.sh")
                )
            val dbtArguments: MutableList<String> = ArrayList()
            dbtArguments.add(DBT_ENTRYPOINT_SH)
            if (Strings.isNullOrEmpty(dbtConfig.dbtArguments)) {
                throw TestHarnessException("Dbt Arguments are required")
            }
            Collections.addAll(
                dbtArguments,
                *Commandline.translateCommandline(dbtConfig.dbtArguments)
            )
            val process =
                processFactory.create(
                    Metadata.CUSTOM_STEP,
                    jobId,
                    attempt,
                    jobRoot,
                    dbtConfig.dockerImage,
                    false,
                    false,
                    files,
                    "/bin/bash",
                    resourceRequirements,
                    null,
                    java.util.Map.of(
                        Metadata.JOB_TYPE_KEY,
                        Metadata.SYNC_JOB,
                        Metadata.SYNC_STEP_KEY,
                        Metadata.CUSTOM_STEP
                    ),
                    emptyMap(),
                    emptyMap(),
                    emptyMap(),
                    *dbtArguments.toTypedArray<String>()
                )
            this.process = process
            LineGobbler.gobble(
                process.inputStream,
                { msg: String -> LOGGER.info(msg) },
                CONTAINER_LOG_MDC_BUILDER
            )
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
        normalizationRunner.close()

        if (process == null) {
            return
        }

        LOGGER.debug("Closing dbt transformation process")
        TestHarnessUtils.gentleClose(process, 1, TimeUnit.MINUTES)
        if (process!!.isAlive || process!!.exitValue() != 0) {
            throw TestHarnessException("Dbt transformation process wasn't successful")
        }
    }

    companion object {

        private const val DBT_ENTRYPOINT_SH = "entrypoint.sh"
        private val CONTAINER_LOG_MDC_BUILDER: MdcScope.Builder =
            MdcScope.Builder()
                .setLogPrefix("dbt")
                .setPrefixColor(LoggingHelper.Color.PURPLE_BACKGROUND)
    }
}
