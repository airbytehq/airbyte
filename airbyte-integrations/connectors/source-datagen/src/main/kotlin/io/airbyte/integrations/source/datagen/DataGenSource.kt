/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.datagen

import io.airbyte.cdk.AirbyteSourceRunner
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import kotlin.collections.forEachIndexed

private val log = KotlinLogging.logger {}

object DataGenSource {
    @JvmStatic
    fun main(args: Array<String>) {
        // TODO: Remove before merging
        args.forEachIndexed { index, arg ->
            log.info { "***$index $arg" }
            if (index in listOf(2, 4, 6)) {
                log.info { (File(arg).readText()) }
            }
        }
        val rootPath = "/Users/sophie.c/dev/airbytestuff/secrets"
        val configPath = "$rootPath/config.json"
        val catalogPath = "$rootPath/catalog.json"
        val statePath = "$rootPath/state.json"
        val checkArgs = arrayOf("--check", "--config", configPath)
        val discoverArgs = arrayOf("--discover", "--config", configPath)
        val readArgs = arrayOf("--read", "--config", configPath, "--catalog", catalogPath)

        AirbyteSourceRunner.run(*args)
    }
}
