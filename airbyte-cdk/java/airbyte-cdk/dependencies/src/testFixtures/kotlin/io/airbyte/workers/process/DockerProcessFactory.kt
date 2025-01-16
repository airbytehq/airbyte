/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.process

import com.google.common.annotations.VisibleForTesting
import com.google.common.base.Joiner
import com.google.common.base.Strings
import com.google.common.collect.Lists
import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.airbyte.commons.io.IOs
import io.airbyte.commons.io.LineGobbler
import io.airbyte.commons.map.MoreMaps
import io.airbyte.commons.resources.MoreResources
import io.airbyte.configoss.AllowedHosts
import io.airbyte.configoss.ResourceRequirements
import io.airbyte.workers.TestHarnessUtils
import io.airbyte.workers.exception.TestHarnessException
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.IOException
import java.nio.file.Files
import java.nio.file.Path
import java.util.*
import java.util.concurrent.TimeUnit
import java.util.function.Function
import org.apache.commons.lang3.StringUtils

private val LOGGER = KotlinLogging.logger {}

class DockerProcessFactory(
    private val workspaceRoot: Path,
    private val workspaceMountSource: String?,
    private val localMountSource: String?,
    private val fileTransferMountSource: Path?,
    private val networkName: String?,
    private val envMap: Map<String, String>
) : ProcessFactory {
    private val imageExistsScriptPath: Path

    /**
     * Used to construct a Docker process.
     *
     * @param workspaceRoot real root of workspace
     * @param workspaceMountSource workspace volume
     * @param localMountSource local volume
     * @param networkName docker network
     * @param envMap
     */
    init {
        imageExistsScriptPath = prepareImageExistsScript()
    }

    @Throws(TestHarnessException::class)
    override fun create(
        jobType: String?,
        jobId: String,
        attempt: Int,
        jobRoot: Path,
        imageName: String,
        usesIsolatedPool: Boolean,
        usesStdin: Boolean,
        files: Map<String?, String?>,
        entrypoint: String?,
        resourceRequirements: ResourceRequirements?,
        allowedHosts: AllowedHosts?,
        labels: Map<String?, String?>?,
        jobMetadata: Map<String, String>,
        internalToExternalPorts: Map<Int?, Int?>?,
        additionalEnvironmentVariables: Map<String, String>,
        vararg args: String
    ): Process {
        try {
            if (!checkImageExists(imageName)) {
                throw TestHarnessException("Could not find image: $imageName")
            }

            if (!jobRoot.toFile().exists()) {
                Files.createDirectory(jobRoot)
            }

            for ((key, value) in files) {
                IOs.writeFile(jobRoot, key, value)
            }

            // The image name is probably something like "airbyte/destination-foo:dev"
            // so try to get the "destination" substring
            val maybeConnectorType = imageName.removePrefix("airbyte/").substringBefore("-")
            // Platform launches connectors with workdir /source or /dest, depending on
            // the connector type.
            val workingDirectory =
                when (maybeConnectorType) {
                    "source" -> "/source"
                    "destination" -> "/dest"
                    else -> "/dest"
                }
            val cmd: MutableList<String> =
                Lists.newArrayList(
                    "docker",
                    "run",
                    "--rm",
                    "--init",
                    "-i",
                    "-w",
                    workingDirectory,
                    "--log-driver",
                    "none"
                )
            val containerName: String =
                ProcessFactory.Companion.createProcessName(
                    imageName,
                    jobType,
                    jobId,
                    attempt,
                    DOCKER_NAME_LEN_LIMIT
                )
            LOGGER.info(
                "Creating docker container = {} with resources {} and allowedHosts {}",
                containerName,
                resourceRequirements,
                allowedHosts
            )
            cmd.add("--name")
            cmd.add(containerName)
            cmd.addAll(localDebuggingOptions(containerName))

            if (networkName != null) {
                cmd.add("--network")
                cmd.add(networkName)
            }

            if (workspaceMountSource != null) {
                cmd.add("-v")
                cmd.add(String.format("%s:%s", workspaceMountSource, DATA_MOUNT_DESTINATION))
            }

            if (localMountSource != null) {
                cmd.add("-v")
                cmd.add(String.format("%s:%s", localMountSource, LOCAL_MOUNT_DESTINATION))
            }

            if (fileTransferMountSource != null) {
                cmd.add("-v")
                cmd.add(
                    "$fileTransferMountSource:${EnvVariableFeatureFlags.DEFAULT_AIRBYTE_STAGING_DIRECTORY}"
                )
                cmd.add("-e")
                cmd.add(
                    "${EnvVariableFeatureFlags.AIRBYTE_STAGING_DIRECTORY_PROPERTY_NAME}=${EnvVariableFeatureFlags.DEFAULT_AIRBYTE_STAGING_DIRECTORY}"
                )

                cmd.add("-e")
                cmd.add("${EnvVariableFeatureFlags.USE_FILE_TRANSFER}=true")
            }

            val allEnvMap = MoreMaps.merge(jobMetadata, envMap, additionalEnvironmentVariables)
            for ((key, value) in allEnvMap) {
                cmd.add("-e")
                cmd.add("$key=$value")
            }

            if (!entrypoint.isNullOrEmpty()) {
                cmd.add("--entrypoint")
                cmd.add(entrypoint)
            }
            if (resourceRequirements != null) {
                if (!Strings.isNullOrEmpty(resourceRequirements.cpuLimit)) {
                    cmd.add(String.format("--cpus=%s", resourceRequirements.cpuLimit))
                }
                if (!Strings.isNullOrEmpty(resourceRequirements.memoryRequest)) {
                    cmd.add(
                        String.format("--memory-reservation=%s", resourceRequirements.memoryRequest)
                    )
                }
                if (!Strings.isNullOrEmpty(resourceRequirements.memoryLimit)) {
                    cmd.add(String.format("--memory=%s", resourceRequirements.memoryLimit))
                }
            }

            cmd.add(imageName)
            cmd.addAll(args)

            LOGGER.info("Preparing command: {}", Joiner.on(" ").join(cmd))

            return ProcessBuilder(cmd).start()
        } catch (e: IOException) {
            throw TestHarnessException(e.message, e)
        }
    }

    private fun rebasePath(jobRoot: Path): Path {
        val relativePath = workspaceRoot.relativize(jobRoot)
        return DATA_MOUNT_DESTINATION.resolve(relativePath)
    }

    @VisibleForTesting
    @Throws(TestHarnessException::class)
    fun checkImageExists(imageName: String?): Boolean {
        try {
            val process = ProcessBuilder(imageExistsScriptPath.toString(), imageName).start()
            LineGobbler.gobble(process.errorStream, { msg: String -> LOGGER.error(msg) })
            LineGobbler.gobble(process.inputStream, { msg: String -> LOGGER.info(msg) })

            TestHarnessUtils.gentleClose(process, 10, TimeUnit.MINUTES)

            if (process.isAlive) {
                throw TestHarnessException("Process to check if image exists is stuck. Exiting.")
            } else {
                return process.exitValue() == 0
            }
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }

    companion object {

        private const val DOCKER_NAME_LEN_LIMIT = 128

        private val DATA_MOUNT_DESTINATION: Path = Path.of("/data")
        private val LOCAL_MOUNT_DESTINATION: Path = Path.of("/local")
        private const val IMAGE_EXISTS_SCRIPT = "image_exists.sh"

        private fun prepareImageExistsScript(): Path {
            try {
                val basePath = Files.createTempDirectory("scripts")
                val scriptContents = MoreResources.readResource(IMAGE_EXISTS_SCRIPT)
                val scriptPath = IOs.writeFile(basePath, IMAGE_EXISTS_SCRIPT, scriptContents)
                if (!scriptPath.toFile().setExecutable(true)) {
                    throw RuntimeException(
                        String.format("Could not set %s to executable", scriptPath)
                    )
                }
                return scriptPath
            } catch (e: IOException) {
                throw RuntimeException(e)
            }
        }

        /**
         * !! ONLY FOR DEBUGGING, SHOULD NOT BE USED IN PRODUCTION !! If you set the
         * DEBUG_CONTAINER_IMAGE environment variable, and it matches the image name of a spawned
         * container, this method will add the necessary params to connect a debugger. For example,
         * to enable this for `destination-bigquery` start the services locally with:
         * ```
         * ```
         * VERSION="dev"
         * ```
         * DEBUG_CONTAINER_IMAGE="destination-bigquery" docker compose -f docker-compose.yaml -f
         * docker-compose.debug.yaml up ``` Additionally you may have to update the image version of your
         * target image to 'dev' in the UI of your local airbyte platform. See the
         * `docker-compose.debug.yaml` file for more context.
         *
         * @param containerName the name of the container which could be debugged.
         * @return A list with debugging arguments or an empty list
         * ```
         */
        fun localDebuggingOptions(containerName: String): List<String> {
            val shouldAddDebuggerOptions =
                (Optional.ofNullable<String>(System.getenv("DEBUG_CONTAINER_IMAGE"))
                    .filter { cs: String -> StringUtils.isNotEmpty(cs) }
                    .map<Boolean>(
                        Function<String, Boolean> { imageName: String ->
                            ProcessFactory.Companion.extractShortImageName(containerName)
                                .startsWith(imageName!!)
                        }
                    )
                    .orElse(false) &&
                    Optional.ofNullable<String>(System.getenv("DEBUG_CONTAINER_JAVA_OPTS"))
                        .isPresent)
            return if (shouldAddDebuggerOptions) {
                java.util.List.of(
                    "-e",
                    "JAVA_TOOL_OPTIONS=" + System.getenv("DEBUG_CONTAINER_JAVA_OPTS"),
                    "-p5005:5005"
                )
            } else {
                emptyList<String>()
            }
        }
    }
}
