/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql.config_spec

import com.fasterxml.jackson.annotation.*
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "method")
@JsonSubTypes(
    JsonSubTypes.Type(
        value = MsSqlServerCdcReplicationConfigurationSpecification::class,
        name = "CDC"
    ),
    JsonSubTypes.Type(
        value = MsSqlServerCursorBasedReplicationConfigurationSpecification::class,
        name = "STANDARD"
    ),
)
sealed interface MsSqlServerReplicationMethodConfigurationSpecification

@JsonSchemaTitle("Read Changes using Change Data Capture (CDC)")
@JsonSchemaDescription(
    "<i>Recommended</i> - Incrementally reads new inserts, updates, and deletes using the SQL Server's " +
        "<a href=\"https://docs.airbyte.com/integrations/sources/mssql/#change-data-capture-cdc\">" +
        "change data capture feature</a>. This must be enabled on your database."
)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class MsSqlServerCdcReplicationConfigurationSpecification :
    MsSqlServerReplicationMethodConfigurationSpecification {
    @JsonProperty("initial_waiting_seconds")
    @JsonSchemaTitle("Initial Waiting Time in Seconds (Advanced)")
    @JsonPropertyDescription(
        "The amount of time the connector will wait when it launches to determine if there is new data to sync or not. " +
            "Defaults to 300 seconds. Valid range: 120 seconds to 3600 seconds.",
    )
    @JsonSchemaInject(json = """{"order":1, "min":120, "max":3600, "default":300}""")
    var initialWaitingSeconds: Int? = DEFAULT_INITIAL_WAITING_SECONDS

    @JsonProperty("invalid_cdc_cursor_position_behavior")
    @JsonSchemaTitle("Invalid CDC position behavior (Advanced)")
    @JsonPropertyDescription(
        "Determines whether Airbyte should fail or re-sync data in case of an stale/invalid cursor value into the WAL. " +
            "If 'Fail sync' is chosen, a user will have to manually reset the connection before being able to continue syncing data. " +
            "If 'Re-sync data' is chosen, Airbyte will automatically trigger a refresh but could lead to higher cloud costs and data loss.",
    )
    @JsonSchemaInject(
        json = """{"order":2,"enum": ["Fail sync", "Re-sync data"], "default": "Fail sync"}"""
    )
    var invalidCdcCursorPositionBehavior: String? = "Fail sync"

    @JsonProperty("queue_size")
    @JsonSchemaTitle("Size of the queue (Advanced)")
    @JsonPropertyDescription(
        "The size of the internal queue. This may interfere with memory consumption and efficiency of the connector, please be careful.",
    )
    @JsonSchemaInject(json = """{"order":3, "min":1000, "max":10000, "default": 10000}""")
    var queueSize: Int? = 10000

    @JsonProperty("initial_load_timeout_hours")
    @JsonSchemaTitle("Initial Load Timeout in Hours (Advanced)")
    @JsonPropertyDescription(
        "The amount of time an initial load is allowed to continue for before catching up on CDC logs.",
    )
    @JsonSchemaInject(json = """{"order":4, "min":4, "max":24, "default": 8}""")
    var initialLoadTimeoutHours: Int? = 8

    companion object {
        const val DEFAULT_INITIAL_WAITING_SECONDS = 300
    }
}

@JsonSchemaTitle("Scan Changes with User Defined Cursor")
@JsonSchemaDescription(
    "Incrementally detects new inserts and updates using the " +
        "<a href=\"https://docs.airbyte.com/understanding-airbyte/connections/incremental-append/#user-defined-cursor\">" +
        "cursor column</a> chosen when configuring a connection (e.g. created_at, updated_at)."
)
class MsSqlServerCursorBasedReplicationConfigurationSpecification :
    MsSqlServerReplicationMethodConfigurationSpecification {}

class MsSqlServerMicronautPropertiesFriendlyMsSqlServerReplicationMethodConfiguration {
    val method: String = "CDC"
    @JsonValue
    fun asReplicationMethod(): MsSqlServerReplicationMethodConfigurationSpecification =
        when (method) {
            "CDC" -> MsSqlServerCdcReplicationConfigurationSpecification()
            "STANDARD" -> MsSqlServerCursorBasedReplicationConfigurationSpecification()
            else -> throw ConfigErrorException("invalid value $method")
        }
}
