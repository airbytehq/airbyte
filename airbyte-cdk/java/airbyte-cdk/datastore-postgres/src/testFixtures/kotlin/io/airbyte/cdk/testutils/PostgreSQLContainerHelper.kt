/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.testutils

import java.io.IOException
import java.util.*
import org.testcontainers.containers.PostgreSQLContainer
import org.testcontainers.utility.MountableFile

object PostgreSQLContainerHelper {
    @JvmStatic
    fun runSqlScript(file: MountableFile?, db: PostgreSQLContainer<Nothing>) {
        try {
            val scriptPath = "/etc/" + UUID.randomUUID() + ".sql"
            db.copyFileToContainer(file, scriptPath)
            db.execInContainer(
                "psql",
                "-d",
                db.databaseName,
                "-U",
                db.username,
                "-a",
                "-f",
                scriptPath
            )
        } catch (e: InterruptedException) {
            throw RuntimeException(e)
        } catch (e: IOException) {
            throw RuntimeException(e)
        }
    }
}
