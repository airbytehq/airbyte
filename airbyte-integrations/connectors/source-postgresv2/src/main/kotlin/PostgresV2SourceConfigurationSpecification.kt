/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgresv2

import com.fasterxml.jackson.annotation.JsonGetter
import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.fasterxml.jackson.annotation.JsonSetter
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonTypeName
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaArrayWithUniqueItems
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDefault
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.airbyte.cdk.command.ConfigurationSpecification
import io.micronaut.context.annotation.ConfigurationBuilder
import io.micronaut.context.annotation.ConfigurationProperties
import jakarta.inject.Singleton

@JsonSchemaTitle("Postgres Source Spec")
@JsonPropertyOrder(
    value =
        [
            "host",
            "port",
            "database",
            "username",
            "password",
            "schemas",
        ],
)
@Singleton
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class PostgresV2SourceConfigurationSpecification : ConfigurationSpecification() {

    @JsonProperty("host")
    @JsonSchemaTitle("Host")
    @JsonSchemaInject(json = """{"order":0, "group": "db"}""")
    @JsonPropertyDescription("Hostname of the database.")
    lateinit var host: String

    @JsonProperty("port")
    @JsonSchemaTitle("Port")
    @JsonSchemaInject(json = """{"order":1, "minimum":0, "maximum":65536, "examples": ["5432"], "group": "db"}""")
    @JsonSchemaDefault("5432")
    @JsonPropertyDescription("Port of the database.")
    var port: Int = 5432

    @JsonProperty("database")
    @JsonSchemaTitle("Database Name")
    @JsonSchemaInject(json = """{"order":2, "group": "db"}""")
    @JsonPropertyDescription("Name of the database.")
    lateinit var database: String

    @JsonProperty("schemas")
    @JsonSchemaTitle("Schemas")
    @JsonSchemaArrayWithUniqueItems("schemas")
    @JsonSchemaInject(json = """{"order":3, "uniqueItems":true, "minItems": 0, "uniqueItems": true, "default": ["public"], "group": "db"}""")
    @JsonPropertyDescription("The list of schemas (case sensitive) to sync from. Defaults to public.")
    var schemas: List<String>? = listOf("public")

    @JsonProperty("username")
    @JsonSchemaTitle("Username")
    @JsonSchemaInject(json = """{"order":4, "group": "auth"}""")
    @JsonPropertyDescription("Username to access the database.")
    lateinit var username: String

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonSchemaInject(json = """{"order":5,"airbyte_secret":true,"always_show":true, "group": "auth"}""")
    @JsonPropertyDescription("Password associated with the username.")
    var password: String? = null

    @JsonProperty("jdbc_url_params")
    @JsonSchemaTitle("JDBC URL Parameters (Advanced)")
    @JsonSchemaInject(json = """{"order":6, "pattern_descriptor": "key1=value1&key2=value2", "group": "advanced"}""")
    @JsonPropertyDescription("Additional properties to pass to the JDBC URL string when connecting to the database formatted as 'key=value' pairs separated by the symbol '&'. (Eg. key1=value1&key2=value2&key3=value3). For more information read about <a href=\"https://jdbc.postgresql.org/documentation/head/connect.html\">JDBC URL parameters</a>.")
    var jdbcUrlParams: String? = null

    // todo (cgardens) - this is a cop out and needs to be tweaked to make real java objects.
    @JsonProperty("ssl_mode")
    @JsonSchemaTitle("SSL Modes")
    @JsonSchemaInject(
        json = """
    {
        "order": 8,
        "group": "security",
        "oneOf": [
            {
                "title": "disable",
                "description": "Disables encryption of communication between Airbyte and source database.",
                "required": ["mode"],
                "properties": {
                    "mode": {
                        "type": "string",
                        "const": "disable",
                        "order": 0
                    }
                },
                "additionalProperties": true
            },
            {
                "title": "allow",
                "description": "Enables encryption only when required by the source database.",
                "required": ["mode"],
                "properties": {
                    "mode": {
                        "type": "string",
                        "const": "allow",
                        "order": 0
                    }
                },
                "additionalProperties": true
            },
            {
                "title": "prefer",
                "description": "Allows unencrypted connection only if the source database does not support encryption.",
                "required": ["mode"],
                "properties": {
                    "mode": {
                        "type": "string",
                        "const": "prefer",
                        "order": 0
                    }
                },
                "additionalProperties": true
            },
            {
                "title": "require",
                "description": "Always require encryption. If the source database server does not support encryption, connection will fail.",
                "required": ["mode"],
                "properties": {
                    "mode": {
                        "type": "string",
                        "const": "require",
                        "order": 0
                    }
                },
                "additionalProperties": true
            },
            {
                "title": "verify-ca",
                "description": "Always require encryption and verifies that the source database server has a valid SSL certificate.",
                "required": ["mode", "ca_certificate"],
                "properties": {
                    "mode": {
                        "type": "string",
                        "const": "verify-ca",
                        "order": 0
                    },
                    "ca_certificate": {
                        "type": "string",
                        "title": "CA Certificate",
                        "description": "CA certificate",
                        "airbyte_secret": true,
                        "multiline": true,
                        "order": 1
                    },
                    "client_certificate": {
                        "type": "string",
                        "title": "Client Certificate",
                        "description": "Client certificate",
                        "airbyte_secret": true,
                        "always_show": true,
                        "multiline": true,
                        "order": 2
                    },
                    "client_key": {
                        "type": "string",
                        "title": "Client Key",
                        "description": "Client key",
                        "airbyte_secret": true,
                        "always_show": true,
                        "multiline": true,
                        "order": 3
                    },
                    "client_key_password": {
                        "type": "string",
                        "title": "Client key password",
                        "description": "Password for keystorage. If you do not add it - the password will be generated automatically.",
                        "airbyte_secret": true,
                        "order": 4
                    }
                },
                "additionalProperties": true
            },
            {
                "title": "verify-full",
                "description": "This is the most secure mode. Always require encryption and verifies the identity of the source database server.",
                "required": ["mode", "ca_certificate"],
                "properties": {
                    "mode": {
                        "type": "string",
                        "const": "verify-full",
                        "order": 0
                    },
                    "ca_certificate": {
                        "type": "string",
                        "title": "CA Certificate",
                        "description": "CA certificate",
                        "airbyte_secret": true,
                        "multiline": true,
                        "order": 1
                    },
                    "client_certificate": {
                        "type": "string",
                        "title": "Client Certificate",
                        "description": "Client certificate",
                        "airbyte_secret": true,
                        "always_show": true,
                        "multiline": true,
                        "order": 2
                    },
                    "client_key": {
                        "type": "string",
                        "title": "Client Key",
                        "description": "Client key",
                        "airbyte_secret": true,
                        "always_show": true,
                        "multiline": true,
                        "order": 3
                    },
                    "client_key_password": {
                        "type": "string",
                        "title": "Client key password",
                        "description": "Password for keystorage. If you do not add it - the password will be generated automatically.",
                        "airbyte_secret": true,
                        "order": 4
                    }
                },
                "additionalProperties": true
            }
        ]
    }
    """
    )
    @JsonPropertyDescription("SSL connection modes. \n  Read more <a href=\"https://jdbc.postgresql.org/documentation/head/ssl-client.html\"> in the docs</a>.")
    var sslMode: String? = null

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "replication_method")
    var replicationMethod = MicronautPropertiesFriendlyIncrementalConfigurationSpecification()

    @JsonIgnore var replicationMethodJson: IncrementalConfigurationSpecification? = null

    @JsonSetter("replication_method")
    fun setIncrementalValue(value: IncrementalConfigurationSpecification) {
        replicationMethodJson = value
    }

    @JsonGetter("replication_method")
    @JsonSchemaTitle("Update Method")
    @JsonPropertyDescription("Configures how data is extracted from the database.")
    @JsonSchemaInject(json = """{"order":9,"display_type":"radio","default":"CDC", "group": "advanced"}""")
    fun getIncrementalValue(): IncrementalConfigurationSpecification =
        replicationMethodJson ?: replicationMethod.asCursorMethodConfiguration()


    @JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "method")
    @JsonSubTypes(
        JsonSubTypes.Type(value = Cdc::class, name = "CDC"),
        JsonSubTypes.Type(value = Xmin::class, name = "XMIN"),
        JsonSubTypes.Type(value = Standard::class, name = "STANDARD")
    )
    @JsonSchemaTitle("Update Method")
    @JsonSchemaDescription("Configures how data is extracted from the database.")
    sealed interface IncrementalConfigurationSpecification

    @JsonTypeName("CDC")
    @JsonSchemaDescription("<i>Recommended</i> - Incrementally reads new inserts, updates, and deletes using the Postgres <a href=\"https://docs.airbyte.com/integrations/sources/postgres/#cdc\">write-ahead log (WAL)</a>. This needs to be configured on the source database itself. Recommended for tables of any size.")
    @JsonSchemaTitle("Read Changes using Write-Ahead Log (CDC)")
    @JsonSchemaInject(json = """{"additionalProperties":true}""")
    class Cdc : IncrementalConfigurationSpecification {

        @JsonProperty("method")
        @JsonSchemaInject(json = """{"const":"CDC","order":2}""")
        @JsonPropertyDescription("This field is fixed to 'CDC' for this replication method.")
        val method: String = "CDC"

        @JsonProperty("plugin")
        @JsonSchemaTitle("Plugin")
        @JsonSchemaInject(json = """{"order":2, "enum": ["pgoutput"], "default": "pgoutput"}""")
        @JsonPropertyDescription("A logical decoding plugin installed on the PostgreSQL server.")
        val plugin: String? = "pgoutput"

        @JsonProperty("replication_slot")
        @JsonSchemaTitle("Replication Slot")
        @JsonSchemaInject(json = """{"order":3}""")
        @JsonPropertyDescription("A plugin logical replication slot. Read about <a href=\"https://docs.airbyte.com/integrations/sources/postgres#step-3-create-replication-slot\">replication slots</a>.")
        val replicationSlot: String = ""

        @JsonProperty("publication")
        @JsonSchemaTitle("Publication")
        @JsonSchemaInject(json = """{"order":4}""")
        @JsonPropertyDescription("A Postgres publication used for consuming changes. Read about <a href=\"https://docs.airbyte.com/integrations/sources/postgres#step-4-create-publications-and-replication-identities-for-tables\">publications and replication identities</a>.")
        val publication: String = ""

        @JsonProperty("initial_waiting_seconds")
        @JsonSchemaTitle("Initial Waiting Time in Seconds (Advanced)")
        @JsonSchemaInject(json = """{"order":5,"min":120,"max":2400,"default":1200}""")
        @JsonPropertyDescription("The amount of time the connector will wait when it launches to determine if there is new data to sync or not. Defaults to 1200 seconds. Valid range: 120 seconds to 2400 seconds. Read about <a href=\"https://docs.airbyte.com/integrations/sources/postgres/postgres-troubleshooting#advanced-setting-up-initial-cdc-waiting-time\">initial waiting time</a>.")
        val initialWaitingSeconds: Int? = 1200

        @JsonProperty("queue_size")
        @JsonSchemaTitle("Size of the queue (Advanced)")
        @JsonSchemaInject(json = """{"order":6,"min":1000,"max":10000,"default":10000}""")
        @JsonPropertyDescription("The size of the internal queue. This may interfere with memory consumption and efficiency of the connector, please be careful.")
        val queueSize: Int? = 10000

        @JsonProperty("lsn_commit_behaviour")
        @JsonSchemaTitle("LSN commit behaviour")
        @JsonSchemaInject(json = """{"order":7, "enum":["While reading Data","After loading Data in the destination"], "default":"After loading Data in the destination"}""")
        @JsonPropertyDescription("Determines when Airbyte should flush the LSN of processed WAL logs in the source database. `After loading Data in the destination` is default. If `While reading Data` is selected, in case of a downstream failure (while loading data into the destination), next sync would result in a full sync.")
        val lsnCommitBehaviour: String? = "After loading Data in the destination"

        @JsonProperty("heartbeat_action_query")
        @JsonSchemaTitle("Debezium heartbeat query (Advanced)")
        @JsonSchemaInject(json = """{"order":8, "default": ""}""")
        @JsonPropertyDescription("Specifies a query that the connector executes on the source database when the connector sends a heartbeat message. Please see the <a href=\"https://docs.airbyte.com/integrations/sources/postgres/postgres-troubleshooting#advanced-wal-disk-consumption-and-heartbeat-action-query\">setup guide</a> for how and when to configure this setting.")
        val heartbeatActionQuery: String? = ""

        @JsonProperty("invalid_cdc_cursor_position_behavior")
        @JsonSchemaTitle("Invalid CDC position behavior (Advanced)")
        @JsonSchemaInject(json = """{"order":9,"enum":["Fail sync","Re-sync data"],"default":"Fail sync"}""")
        @JsonPropertyDescription("Determines whether Airbyte should fail or re-sync data in case of an stale/invalid cursor value into the WAL. If 'Fail sync' is chosen, a user will have to manually reset the connection before being able to continue syncing data. If 'Re-sync data' is chosen, Airbyte will automatically trigger a refresh but could lead to higher cloud costs and data loss.")
        var invalidCdcCursorPositionBehavior: String? = "Fail sync"

        @JsonProperty("initial_load_timeout_hours")
        @JsonSchemaTitle("Initial Load Timeout in Hours (Advanced)")
        @JsonSchemaInject(json = """{"order":10,"min":4,"max":24,"default":8}""")
        @JsonPropertyDescription("The amount of time an initial load is allowed to continue for before catching up on CDC logs.")
        val initialLoadTimeoutHours: Int? = 8
    }


    @JsonTypeName("Xmin")
    @JsonSchemaDescription("<i>Recommended</i> - Incrementally reads new inserts and updates via Postgres <a href=\"https://docs.airbyte.com/integrations/sources/postgres/#xmin\">Xmin system column</a>. Suitable for databases that have low transaction pressure.")
    @JsonSchemaTitle("Detect Changes with Xmin System Column")
    class Xmin : IncrementalConfigurationSpecification {
        @JsonProperty("method")
        @JsonSchemaInject(json = """{"const":"Xmin","order":1}""")
        val method: String = "Xmin"
    }

    @JsonTypeName("Standard")
    @JsonSchemaDescription("Incrementally detects new inserts and updates using the <a href=\"https://docs.airbyte.com/understanding-airbyte/connections/incremental-append/#user-defined-cursor\">cursor column</a> chosen when configuring a connection (e.g. created_at, updated_at).")
    @JsonSchemaTitle("Scan Changes with User Defined Cursor")
    class Standard : IncrementalConfigurationSpecification {
        @JsonProperty("method")
        @JsonSchemaInject(json = """{"const":"Standard","order":2}""")
        val method: String = "Standard"
    }

    @ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.replication_method")
    class MicronautPropertiesFriendlyIncrementalConfigurationSpecification {
        var method: String? = "CDC"

        fun asCursorMethodConfiguration(): IncrementalConfigurationSpecification =
            when (method) {
                "STANDARD" -> Standard()
                "CDC" -> Cdc()
                "XMIN" -> Xmin()
                else -> throw ConfigErrorException("invalid value $method")
            }
    }

}
