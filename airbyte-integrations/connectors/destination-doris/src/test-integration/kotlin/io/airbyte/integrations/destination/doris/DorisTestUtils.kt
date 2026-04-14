/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.integrations.destination.doris.spec.DorisConfiguration
import io.airbyte.integrations.destination.doris.spec.DorisConfigurationFactory
import io.airbyte.integrations.destination.doris.spec.DorisSpecification
import java.sql.Connection

object DorisTestUtils {

    fun specToConfig(spec: ConfigurationSpecification): DorisConfiguration {
        return DorisConfigurationFactory()
            .makeWithOverrides(
                spec as DorisSpecification,
                mapOf(
                    "host" to DorisContainerHelper.getHost(),
                    "http_port" to DorisContainerHelper.getHttpPort().toString(),
                    "query_port" to DorisContainerHelper.getQueryPort().toString(),
                    "username" to DorisContainerHelper.getUsername(),
                    "password" to DorisContainerHelper.getPassword(),
                )
            )
    }

    fun getConnection(database: String? = null): Connection {
        return if (database != null) {
            DorisContainerHelper.getConnection(database)
        } else {
            DorisContainerHelper.getConnection()
        }
    }

    fun buildConfigJson(): String {
        return """
            {
                "host": "${DorisContainerHelper.getHost()}",
                "http_port": ${DorisContainerHelper.getHttpPort()},
                "query_port": ${DorisContainerHelper.getQueryPort()},
                "database": "test_db",
                "username": "${DorisContainerHelper.getUsername()}",
                "password": "${DorisContainerHelper.getPassword()}"
            }
            """.trimIndent()
    }
}
