/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import com.google.common.base.Preconditions
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Lists
import com.google.common.collect.Maps
import java.nio.file.Path

class AirbyteIntegrationLauncher(
    private val jobId: String,
    private val attempt: Int,
    private val imageName: String,
    private val processFactory: ProcessFactory,
    private val resourceRequirement: ResourceRequirements?,
    private val allowedHosts: AllowedHosts?,
    /**
     * If true, launcher will use a separated isolated pool to run the job.
     *
     * At this moment, we put custom connector jobs into an isolated pool.
     */
    private val useIsolatedPool: Boolean,
    private val featureFlags: FeatureFlags
) : IntegrationLauncher {
    @Throws(TestHarnessException::class)
    override fun spec(jobRoot: Path): Process {
        return processFactory.create(
            Metadata.SPEC_JOB,
            jobId,
            attempt,
            jobRoot,
            imageName,
            useIsolatedPool,
            false,
            emptyMap(),
            null,
            resourceRequirement,
            allowedHosts,
            java.util.Map.of(Metadata.JOB_TYPE_KEY, Metadata.SPEC_JOB),
            workerMetadata,
            emptyMap(),
            emptyMap(),
            "spec"
        )
    }

    @Throws(TestHarnessException::class)
    override fun check(jobRoot: Path, configFilename: String, configContents: String): Process {
        return processFactory.create(
            Metadata.CHECK_JOB,
            jobId,
            attempt,
            jobRoot,
            imageName,
            useIsolatedPool,
            false,
            ImmutableMap.of(configFilename, configContents),
            null,
            resourceRequirement,
            allowedHosts,
            java.util.Map.of(Metadata.JOB_TYPE_KEY, Metadata.CHECK_JOB),
            workerMetadata,
            emptyMap(),
            emptyMap(),
            "check",
            CONFIG,
            configFilename
        )
    }

    @Throws(TestHarnessException::class)
    override fun discover(jobRoot: Path, configFilename: String, configContents: String): Process {
        return processFactory.create(
            Metadata.DISCOVER_JOB,
            jobId,
            attempt,
            jobRoot,
            imageName,
            useIsolatedPool,
            false,
            ImmutableMap.of(configFilename, configContents),
            null,
            resourceRequirement,
            allowedHosts,
            java.util.Map.of(Metadata.JOB_TYPE_KEY, Metadata.DISCOVER_JOB),
            workerMetadata,
            emptyMap(),
            emptyMap(),
            "discover",
            CONFIG,
            configFilename
        )
    }

    @Throws(TestHarnessException::class)
    override fun read(
        jobRoot: Path,
        configFilename: String?,
        configContents: String?,
        catalogFilename: String?,
        catalogContents: String?,
        stateFilename: String?,
        stateContents: String?
    ): Process? {
        val arguments: MutableList<String> =
            Lists.newArrayList("read", CONFIG, configFilename, "--catalog", catalogFilename)

        val files: MutableMap<String?, String?> = HashMap()
        files[configFilename] = configContents
        files[catalogFilename] = catalogContents

        if (stateFilename != null) {
            arguments.add("--state")
            arguments.add(stateFilename)

            Preconditions.checkNotNull(stateContents)
            files[stateFilename] = stateContents
        }

        return processFactory.create(
            Metadata.READ_STEP,
            jobId,
            attempt,
            jobRoot,
            imageName,
            useIsolatedPool,
            false,
            files,
            null,
            resourceRequirement,
            allowedHosts,
            java.util.Map.of(
                Metadata.JOB_TYPE_KEY,
                Metadata.SYNC_JOB,
                Metadata.SYNC_STEP_KEY,
                Metadata.READ_STEP
            ),
            workerMetadata,
            emptyMap(),
            emptyMap(),
            *arguments.toTypedArray<String>()
        )
    }

    @Throws(TestHarnessException::class)
    override fun write(
        jobRoot: Path,
        configFilename: String,
        configContents: String,
        catalogFilename: String,
        catalogContents: String,
        additionalEnvironmentVariables: Map<String, String>
    ): Process? {
        val files: Map<String?, String?> =
            ImmutableMap.of(configFilename, configContents, catalogFilename, catalogContents)

        return processFactory.create(
            Metadata.WRITE_STEP,
            jobId,
            attempt,
            jobRoot,
            imageName,
            useIsolatedPool,
            true,
            files,
            null,
            resourceRequirement,
            allowedHosts,
            java.util.Map.of(
                Metadata.JOB_TYPE_KEY,
                Metadata.SYNC_JOB,
                Metadata.SYNC_STEP_KEY,
                Metadata.WRITE_STEP
            ),
            workerMetadata,
            emptyMap(),
            additionalEnvironmentVariables,
            "write",
            CONFIG,
            configFilename,
            "--catalog",
            catalogFilename
        )
    }

    private val workerMetadata: Map<String, String>
        get() = // We've managed to exceed the maximum number of parameters for Map.of(), so use a
            // builder + convert
            // back to hashmap
            Maps.newHashMap(
                ImmutableMap.builder<String, String>()
                    .put("WORKER_CONNECTOR_IMAGE", imageName)
                    .put("WORKER_JOB_ID", jobId)
                    .put("WORKER_JOB_ATTEMPT", attempt.toString())
                    .put(
                        EnvVariableFeatureFlags.AUTO_DETECT_SCHEMA,
                        featureFlags.autoDetectSchema().toString()
                    )
                    .put(
                        EnvVariableFeatureFlags.APPLY_FIELD_SELECTION,
                        featureFlags.applyFieldSelection().toString()
                    )
                    .put(
                        EnvVariableFeatureFlags.FIELD_SELECTION_WORKSPACES,
                        featureFlags.fieldSelectionWorkspaces()
                    )
                    .build()
            )

    companion object {
        private const val CONFIG = "--config"
    }
}
