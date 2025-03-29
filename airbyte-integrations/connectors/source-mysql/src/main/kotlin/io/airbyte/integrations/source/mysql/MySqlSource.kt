/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.AirbyteSourceRunner
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.Paths

private val log = KotlinLogging.logger {}
object MySqlSource {
    @JvmStatic
    fun main(args: Array<String>) {
        log.info { "total space: ${File("/").totalSpace}. Free: ${File("/").freeSpace}. usable: ${File("/").usableSpace}" }
        log.info { "total space: ${File("/staging/files").totalSpace}. Free: ${File("/staging/files").freeSpace}. usable: ${File("/staging/files").usableSpace}" }
        try {
            val folder: Path = Paths.get("/staging/files")
            val size = Files.walk(folder)
                .filter { Files.isRegularFile(it) }
                .mapToLong { it.toFile().length() }
                .sum()
            log.info { "Total size of files in /staging/files: $size bytes" }
        } catch (_: Exception) {
            log.info { "Error calculating total size of files in /staging/files" }
        }
        args.forEachIndexed { index, arg ->
            log.info { "***$index $arg" }
            if (index in listOf(2, 4, 6)) {
                log.info { (File(arg).readText()) }
            }

        }
        AirbyteSourceRunner.run(*args)
    }
}
