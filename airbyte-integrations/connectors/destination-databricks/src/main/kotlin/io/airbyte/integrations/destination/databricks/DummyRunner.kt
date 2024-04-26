/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks

import com.databricks.client.jdbc.DataSource
import com.databricks.client.jdbc.Driver
import com.databricks.sdk.WorkspaceClient
import com.databricks.sdk.core.DatabricksConfig
import java.sql.Connection

fun main() {

    // TODO: Delete this class, random testings were done with this main

    println("Dummy runner working")
    fun createConnection(): Connection {
        val className = Driver::class.java.canonicalName
        Class.forName(className)
        val datasource = DataSource()
        datasource.setURL("<JDBC_URL>")
        return datasource.connection
    }

    val connection = createConnection()
    val resultSet =
        connection
            .createStatement()
            .executeQuery("select * from integration_tests.airbyte_internal.parquet_staging;")
    println(resultSet)

    val config =
        DatabricksConfig()
            .setAuthType("pat")
            .setHost("https://dbc-6aebf761-f8d6.cloud.databricks.com")
            .setToken("<PAT>")
    val workspaceClient = WorkspaceClient(config)
    val directoryEntries =
        workspaceClient
            .files()
            .listDirectoryContents("/Volumes/integration_tests/airbyte_internal/raw_staging")
    for (entry in directoryEntries) {
        println(entry.name)
    }
}
