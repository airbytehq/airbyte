/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.util

import io.airbyte.commons.io.LineGobbler
import java.io.File
import java.io.IOException
import java.util.*
import java.util.concurrent.TimeUnit
import org.slf4j.Logger
import org.slf4j.LoggerFactory

object JavaProcessRunner {
    private val LOGGER: Logger = LoggerFactory.getLogger(JavaProcessRunner::class.java)

    @Throws(IOException::class, InterruptedException::class)
    fun runProcess(path: String, run: Runtime, vararg commands: String?) {
        LOGGER.info("Running process: " + Arrays.asList(*commands))
        val pr =
            if (path == System.getProperty("user.dir")) run.exec(commands)
            else run.exec(commands, null, File(path))
        LineGobbler.gobble(`is` = pr.errorStream, { LOGGER.warn(it) })
        LineGobbler.gobble(`is` = pr.inputStream, { LOGGER.info(it) })
        if (!pr.waitFor(10, TimeUnit.MINUTES)) {
            pr.destroy()
            throw RuntimeException("Timeout while executing: " + commands.contentToString())
        }
    }
}
