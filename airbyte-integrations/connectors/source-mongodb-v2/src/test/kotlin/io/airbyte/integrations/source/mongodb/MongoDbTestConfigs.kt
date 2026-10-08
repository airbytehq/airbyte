/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfigurationSpecification

/**
 * Builds connector configurations for tests; shared by the check, discover, read and acceptance
 * suites.
 */
object MongoDbTestConfigs {
    fun config(
        connectionString: String,
        databases: List<String>,
        username: String? = null,
        password: String? = null,
        schemaEnforced: Boolean? = null,
        /** Extra root-level spec properties, e.g. `invalid_cdc_cursor_position_behavior`. */
        extraRootProperties: Map<String, Any> = emptyMap(),
    ): MongoDbSourceConfigurationSpecification {
        val databaseConfig: MutableMap<String, Any> =
            mutableMapOf(
                "cluster_type" to "SELF_MANAGED_REPLICA_SET",
                "connection_string" to connectionString,
                "databases" to databases,
            )
        username?.let { databaseConfig["username"] = it }
        password?.let { databaseConfig["password"] = it }
        schemaEnforced?.let { databaseConfig["schema_enforced"] = it }
        val json: String =
            Jsons.writeValueAsString(
                mapOf("database_config" to databaseConfig) + extraRootProperties
            )
        return Jsons.readValue(json, MongoDbSourceConfigurationSpecification::class.java)
    }
}
