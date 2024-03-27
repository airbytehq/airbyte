/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.helper

import io.airbyte.workers.exception.TestHarnessException
import io.airbyte.workers.process.ProcessFactory
import java.io.BufferedReader
import java.io.IOException
import java.io.InputStreamReader
import java.nio.charset.StandardCharsets
import java.nio.file.Path

/** Should only be used by connector testing. */
object EntrypointEnvChecker {
    /**
     * @param processFactory any process factory
     * @param jobId used as input to processFactory.create
     * @param jobAttempt used as input to processFactory.create
     * @param jobRoot used as input to processFactory.create
     * @param imageName used as input to processFactory.create
     * @return the entrypoint in the env variable AIRBYTE_ENTRYPOINT
     * @throws RuntimeException if there is ambiguous output from the container
     */
    @Throws(IOException::class, InterruptedException::class, TestHarnessException::class)
    fun getEntrypointEnvVariable(
        processFactory: ProcessFactory,
        jobId: String,
        jobAttempt: Int,
        jobRoot: Path,
        imageName: String
    ): String? {
        val process =
            processFactory.create(
                "entrypoint-checker",
                jobId,
                jobAttempt,
                jobRoot,
                imageName,
                false,
                false,
                emptyMap(),
                "printenv",
                null,
                null,
                emptyMap(),
                emptyMap(),
                emptyMap(),
                emptyMap()
            )

        val stdout =
            BufferedReader(InputStreamReader(process!!.inputStream, StandardCharsets.UTF_8))

        var outputLine: String? = null

        var line = stdout.readLine()
        while ((line != null) && outputLine == null) {
            if (line.contains("AIRBYTE_ENTRYPOINT")) {
                outputLine = line
            }
            line = stdout.readLine()
        }

        process.waitFor()

        return if (outputLine != null) {
            val splits = outputLine.split("=".toRegex(), limit = 2).toTypedArray()
            if (splits.size != 2) {
                throw RuntimeException(
                    "String could not be split into multiple segments: $outputLine"
                )
            } else {
                splits[1].trim()
            }
        } else {
            null
        }
    }
}
