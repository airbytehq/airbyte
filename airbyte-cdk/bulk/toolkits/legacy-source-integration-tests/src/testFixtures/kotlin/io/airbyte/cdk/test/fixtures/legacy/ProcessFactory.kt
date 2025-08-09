/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import java.nio.file.Path
import java.util.*
import java.util.regex.Pattern
import org.apache.commons.lang3.RandomStringUtils

interface ProcessFactory {
    /**
     * Creates a ProcessBuilder to run a program in a new Process.
     *
     * @param jobType type of job to add to name for easier operational processes.
     * @param jobId job Id
     * @param attempt attempt Id
     * @param jobPath Workspace directory to run the process from.
     * @param imageName Docker image name to start the process from.
     * @param usesIsolatedPool whether to use isolated pool to run the jobs.
     * @param files File name to contents map that will be written into the working dir of the
     * process prior to execution.
     * @param entrypoint If not null, the default entrypoint program of the docker image can be
     * changed by this argument.
     * @param resourceRequirements CPU and RAM to assign to the created process.
     * @param labels Labels to assign to the created Kube pod, if any. Ignore for docker.
     * @param jobMetadata Job metadata that will be passed to the created process as environment
     * variables.
     * @param additionalEnvironmentVariables
     * @param args Arguments to pass to the docker image being run in the new process.
     * @return ProcessBuilder object to run the process.
     * @throws TestHarnessException
     */
    @Throws(TestHarnessException::class)
    fun create(
        jobType: String?,
        jobId: String,
        attempt: Int,
        jobPath: Path,
        imageName: String,
        usesIsolatedPool: Boolean,
        usesStdin: Boolean,
        files: Map<String?, String?>,
        entrypoint: String?,
        resourceRequirements: ResourceRequirements?,
        allowedHosts: AllowedHosts?,
        labels: Map<String?, String?>?,
        jobMetadata: Map<String, String>,
        portMapping: Map<Int?, Int?>?,
        additionalEnvironmentVariables: Map<String, String>,
        vararg args: String
    ): Process

    companion object {
        /**
         * Docker image names are by convention separated by slashes. The last portion is the
         * image's name. This is followed by a colon and a version number. e.g. airbyte/scheduler:v1
         * or gcr.io/my-project/image-name:v2.
         *
         * With these two facts, attempt to construct a unique process name with the image name
         * present that can be used by the factories implementing this interface for easier
         * operations.
         */
        fun createProcessName(
            fullImagePath: String,
            jobType: String?,
            jobId: String,
            attempt: Int,
            lenLimit: Int
        ): String {
            var imageName = extractShortImageName(fullImagePath)
            val randSuffix = RandomStringUtils.randomAlphabetic(5).lowercase(Locale.getDefault())
            val suffix = "$jobType-$jobId-$attempt-$randSuffix"

            var processName = "$imageName-$suffix"
            if (processName.length > lenLimit) {
                val extra = processName.length - lenLimit
                imageName = imageName.substring(extra)
                processName = "$imageName-$suffix"
            }

            // Kubernetes pod names must start with an alphabetic character while Docker names
            // accept
            // alphanumeric.
            // Use the stricter convention for simplicity.
            val m = ALPHABETIC.matcher(processName)
            // Since we add sync-UUID as a suffix a couple of lines up, there will always be a
            // substring
            // starting with an alphabetic character.
            // If the image name is a no-op, this function should always return `sync-UUID` at the
            // minimum.
            m.find()
            return processName.substring(m.start())
        }

        /**
         * Docker image names are by convention separated by slashes. The last portion is the
         * image's name. This is followed by a colon and a version number. e.g. airbyte/scheduler:v1
         * or gcr.io/my-project/my-project:v2.
         *
         * @param fullImagePath the image name with repository and version ex
         * gcr.io/my-project/image-name:v2
         * @return the image name without the repo and version, ex. image-name
         */
        fun extractShortImageName(fullImagePath: String): String {
            val noVersion =
                fullImagePath
                    .split(VERSION_DELIMITER.toRegex())
                    .dropLastWhile { it.isEmpty() }
                    .toTypedArray()[0]

            val nameParts =
                noVersion
                    .split(DOCKER_DELIMITER.toRegex())
                    .dropLastWhile { it.isEmpty() }
                    .toTypedArray()
            return nameParts[nameParts.size - 1]
        }

        const val VERSION_DELIMITER: String = ":"
        const val DOCKER_DELIMITER: String = "/"
        val ALPHABETIC: Pattern = Pattern.compile("[a-zA-Z]+")
    }
}
