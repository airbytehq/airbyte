/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks

import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.destination.databricks.model.DatabricksConnectorConfig
import java.nio.file.Files
import java.nio.file.Path

fun main() {

    // TODO: Delete this class before merge, random testings were done with this main

    println("Dummy runner working")
    val out =
        Files.readString(
            Path.of(
                "airbyte-integrations/connectors/destination-databricks/secrets/oauth_config.json"
            )
        )
    println(out)
    val connectorConfig = DatabricksConnectorConfig.deserialize(Jsons.deserialize(out))
    val datasource = ConnectorClientsFactory.createDataSource(connectorConfig)
    val connection = datasource.connection
    connection.use {
        val resultSet =
            it.createStatement()
                .executeQuery("select * from integration_tests.airbyte_internal.parquet_staging;")
        resultSet.use { rs ->
            val columnCount: Int = rs.metaData.columnCount
            while (rs.next()) {
                var row = ""
                for (i in 1..columnCount) {
                    row += rs.getString(i) + ", "
                }
                println(row)
            }
        }
    }

    val workspaceClient =
        ConnectorClientsFactory.createWorkspaceClient(
            connectorConfig.hostname,
            connectorConfig.authentication
        )
    val directoryEntries =
        workspaceClient
            .files()
            .listDirectoryContents("/Volumes/integration_tests/airbyte_internal/raw_staging")
    for (entry in directoryEntries) {
        println(entry.name)
    }
}
