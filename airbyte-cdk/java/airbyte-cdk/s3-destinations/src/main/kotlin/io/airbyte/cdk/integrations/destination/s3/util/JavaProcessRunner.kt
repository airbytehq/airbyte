/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.util

import io.airbyte.commons.io.LineGobbler
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.io.IOException
import java.util.*
import java.util.concurrent.TimeUnit

private val LOGGER = KotlinLogging.logger {}

object JavaProcessRunner {

    @Throws(IOException::class, InterruptedException::class)
    fun runProcess(path: String, run: Runtime, vararg commands: String?) {
        LOGGER.info { "Running process: ${listOf(*commands)}" }
        val pr =
            if (path == System.getProperty("user.dir")) run.exec(commands)
            else run.exec(commands, null, File(path))
        LineGobbler.gobble(`is` = pr.errorStream, { LOGGER.warn { it } })
        LineGobbler.gobble(`is` = pr.inputStream, { LOGGER.info { it } })
        if (!pr.waitFor(10, TimeUnit.MINUTES)) {
            pr.destroy()
            throw RuntimeException("Timeout while executing: " + commands.contentToString())
        }
    }
}
