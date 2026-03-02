/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.config

import com.fasterxml.jackson.annotation.JsonAnySetter
import com.fasterxml.jackson.annotation.JsonGetter
import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.fasterxml.jackson.annotation.JsonSetter
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaArrayWithUniqueItems
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDefault
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.CONNECTOR_CONFIG_PREFIX
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.ssh.MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.micronaut.context.annotation.ConfigurationBuilder
import io.micronaut.context.annotation.ConfigurationProperties
import jakarta.inject.Singleton

/**
 * The object which is mapped to the Postgres source configuration JSON.
 *
 * Use [PostgresSourceConfiguration] instead wherever possible. This object also allows injecting
 * values through Micronaut properties, this is made possible by the classes named
 * `MicronautPropertiesFriendly.*`.
 */
@JsonSchemaTitle("Postgres Source Spec")
@JsonSchemaInject(
    json =
        """{"groups":[{"id":"db"},{"id":"auth"},{"id":"security","title":"Security"},{"id":"advanced","title":"Advanced"},{"id":"performance","title":"Performance"}]}"""
)
@JsonPropertyOrder(
    value =
        [
            "host",
            "port",
            "database",
            "schemas",
            "username",
            "password",
            "entra_service_principal_auth",
            "entra_tenant_id",
            "entra_client_id",
            "ssl_mode",
            "tunnel_method",
            "jdbc_url_params",
            "replication_method",
            "check_privileges",
            "checkpoint_target_interval_seconds",
            "max_db_connections",
        ],
)
@Singleton
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class PostgresSourceConfigurationSpecification : ConfigurationSpecification() {
    @JsonProperty("host")
    @JsonSchemaTitle("Host")
    @JsonSchemaInject(json = """{"order":1,"group":"db"}""")
    @JsonPropertyDescription("Hostname of the database.")
    lateinit var host: String

    @JsonProperty("port")
    @JsonSchemaTitle("Port")
    @JsonSchemaInject(json = """{"order":2,"minimum": 0,"maximum": 65536,"group":"db"}""")
    @JsonSchemaDefault("5432")
    @JsonPropertyDescription("Port of the database. Defaults to 5432.")
    var port: Int = 5432

    @JsonProperty("database")
    @JsonSchemaTitle("Database Name")
    @JsonPropertyDescription("The name of the database to connect to.")
    @JsonSchemaInject(json = """{"order":3,"group":"db"}""")
    lateinit var database: String

    @JsonProperty("username")
    @JsonSchemaTitle("Username")
    @JsonPropertyDescription("The username which is used to access the database.")
    @JsonSchemaInject(json = """{"order":4,"group":"auth"}""")
    lateinit var username: String

    @JsonProperty("password")
    @JsonSchemaTitle("Password")
    @JsonPropertyDescription("The password associated with the username.")
    @JsonSchemaInject(
        json = """{"order":5,"always_show":true,"airbyte_secret":true,"group":"auth"}"""
    )
    var password: String? = null

    @JsonProperty("entra_service_principal_auth")
    @JsonSchemaTitle("Azure Entra Service Principal Authentication")
    @JsonPropertyDescription(
        "Interpret password as a client secret for a Microsoft Entra service principal"
    )
    @JsonSchemaInject(json = """{"order":6,"group":"auth"}""")
    @JsonSchemaDefault("false")
    var servicePrincipalAuth: Boolean? = false

    @JsonProperty("entra_tenant_id")
    @JsonSchemaTitle("Azure Entra Tenant Id")
    @JsonPropertyDescription("If using Entra service principal, the ID of the tenant")
    @JsonSchemaInject(json = """{"order":7,"group":"auth"}""")
    var entraTenantId: String? = null

    @JsonProperty("entra_client_id")
    @JsonSchemaTitle("Azure Entra Client Id")
    @JsonPropertyDescription(
        "If using Entra service principal, the application ID of the service principal"
    )
    @JsonSchemaInject(json = """{"order":8,"group":"auth"}""")
    var entraClientId: String? = null

    @JsonProperty("schemas")
    @JsonSchemaTitle("Schemas")
    @JsonSchemaArrayWithUniqueItems("schemas")
    @JsonPropertyDescription(
        "The list of schemas to sync from. Defaults to public. Case sensitive."
    )
    @JsonSchemaInject(json = """{"order":9,"uniqueItems":true,"group":"db"}""")
    var schemas: List<String>? = listOf("public")

    @JsonProperty("jdbc_url_params")
    @JsonSchemaTitle("JDBC URL Parameters (Advanced)")
    @JsonPropertyDescription(
        "Additional properties to pass to the JDBC URL string when connecting to the database " +
            "formatted as 'key=value' pairs separated by the symbol '&'. " +
            "(example: key1=value1&key2=value2&key3=value3). " +
            "For more information read about " +
            "<a href=\"https://jdbc.postgresql.org/documentation/head/connect.html\">JDBC URL parameters</a>."
    )
    @JsonSchemaInject(
        json = """{"order":10,"group":"advanced","pattern_descriptor":"key1=value1&key2=value2"}"""
    )
    var jdbcUrlParams: String? = null

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "ssl_mode")
    var encryption = MicronautPropertiesFriendlyEncryptionSpecification()

    @JsonIgnore var encryptionJson: EncryptionSpecification? = null

    @JsonSetter("ssl_mode")
    fun setEncryptionValue(value: EncryptionSpecification) {
        encryptionJson = value
    }

    @JsonGetter("ssl_mode")
    @JsonSchemaTitle("SSL Mode")
    @JsonPropertyDescription(
        "The encryption method which is used when communicating with the database.",
    )
    @JsonSchemaInject(json = """{"order":8,"default":"require","group":"security"}""")
    fun getEncryptionValue(): EncryptionSpecification? = encryptionJson ?: encryption.asEncryption()

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "tunnel_method")
    val tunnelMethod = MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification()

    @JsonIgnore var tunnelMethodJson: SshTunnelMethodConfiguration? = null

    @JsonSetter("tunnel_method")
    fun setTunnelMethodValue(value: SshTunnelMethodConfiguration) {
        tunnelMethodJson = value
    }

    @JsonGetter("tunnel_method")
    @JsonSchemaTitle("SSH Tunnel Method")
    @JsonPropertyDescription(
        "Whether to initiate an SSH tunnel before connecting to the database, " +
            "and if so, which kind of authentication to use.",
    )
    @JsonSchemaInject(json = """{"order":11,"group":"security"}""")
    fun getTunnelMethodValue(): SshTunnelMethodConfiguration =
        tunnelMethodJson ?: tunnelMethod.asSshTunnelMethod()

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "replication_method")
    val replication_method = MicronautPropertiesFriendlyCursorConfigurationSpecification()

    @JsonIgnore var replicationMethodJson: IncrementalConfigurationSpecification? = null

    @JsonSetter("replication_method")
    fun setIncrementalConfigurationSpecificationValue(
        value: IncrementalConfigurationSpecification
    ) {
        replicationMethodJson = value
    }

    @JsonGetter("replication_method")
    @JsonSchemaTitle("Update Method")
    @JsonPropertyDescription("Configures how data is extracted from the database.")
    @JsonSchemaInject(json = """{"order":12,"display_type":"radio","group":"advanced"}""")
    fun getIncrementalConfigurationSpecificationValue(): IncrementalConfigurationSpecification =
        replicationMethodJson ?: replication_method.asIncrementalConfigurationSpecification()

    @JsonProperty("checkpoint_target_interval_seconds")
    @JsonSchemaTitle("Checkpoint Target Time Interval")
    @JsonSchemaInject(json = """{"order":15,"always_show":true,"group":"performance"}""")
    @JsonSchemaDefault("300")
    @JsonPropertyDescription("How often (in seconds) a stream should checkpoint, when possible.")
    var checkpointTargetIntervalSeconds: Int? = 300

    @JsonProperty("max_db_connections")
    @JsonSchemaTitle("Max Concurrent Queries to Database")
    @JsonSchemaInject(json = """{"order":16,"always_show":true,"group":"performance"}""")
    @JsonPropertyDescription(
        "Maximum number of concurrent queries to the database. Leave empty to let Airbyte optimize performance."
    )
    var maxDbConnections: Int? = null

    @JsonProperty("check_privileges")
    @JsonSchemaTitle("Check Table and Column Access Privileges")
    @JsonSchemaInject(json = """{"order":13,"always_show":true,"group":"performance"}""")
    @JsonSchemaDefault("true")
    @JsonPropertyDescription(
        "When this feature is enabled, during schema discovery the connector " +
            "will query each table or view individually to check access privileges " +
            "and inaccessible tables, views, or columns therein will be removed. " +
            "In large schemas, this might cause schema discovery to take too long, " +
            "in which case it might be advisable to disable this feature.",
    )
    var checkPrivileges: Boolean? = true

    @JsonIgnore var additionalPropertiesMap = mutableMapOf<String, Any>()

    @JsonAnySetter
    fun setAdditionalProperty(
        name: String,
        value: Any,
    ) {
        additionalPropertiesMap[name] = value
    }
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "mode")
@JsonSubTypes(
    JsonSubTypes.Type(value = EncryptionDisable::class, name = "disable"),
    JsonSubTypes.Type(value = EncryptionAllow::class, name = "allow"),
    JsonSubTypes.Type(value = EncryptionPrefer::class, name = "prefer"),
    JsonSubTypes.Type(value = EncryptionRequire::class, name = "require"),
    JsonSubTypes.Type(value = SslVerifyCertificate::class, name = "verify-ca"),
    JsonSubTypes.Type(value = SslVerifyFull::class, name = "verify-full"),
)
@JsonSchemaTitle("Encryption")
@JsonSchemaDescription("The encryption method which is used when communicating with the database.")
sealed interface EncryptionSpecification

@JsonSchemaTitle("disable")
@JsonSchemaDescription(
    "To force communication without encryption.",
)
data object EncryptionDisable : EncryptionSpecification

@JsonSchemaTitle("allow")
@JsonSchemaDescription(
    "To allow encrypted communication, but not require it.",
)
data object EncryptionAllow : EncryptionSpecification

@JsonSchemaTitle("prefer")
@JsonSchemaDescription(
    "To allow unencrypted communication only when the source doesn't support encryption.",
)
data object EncryptionPrefer : EncryptionSpecification

@JsonSchemaTitle("require")
@JsonSchemaDescription(
    "To always require encryption. Note: The connection will fail if the source doesn't support encryption.",
)
data object EncryptionRequire : EncryptionSpecification

@JsonSchemaTitle("verify-ca")
@JsonSchemaDescription(
    "To always require encryption and verify that the source has a valid SSL certificate."
)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class SslVerifyCertificate : EncryptionSpecification {
    @JsonProperty("ca_certificate", required = true)
    @JsonSchemaTitle("CA certificate")
    @JsonPropertyDescription(
        "CA certificate",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    lateinit var sslCertificate: String

    @JsonProperty("client_certificate", required = false)
    @JsonSchemaTitle("Client certificate File")
    @JsonPropertyDescription(
        "Client certificate (this is not a required field, but if you want to use it, you will need to add the Client key as well)",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var sslClientCertificate: String? = null

    @JsonProperty("client_key")
    @JsonSchemaTitle("Client Key")
    @JsonPropertyDescription(
        "Client key (this is not a required field, but if you want to use it, you will need to add the Client certificate as well)",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var sslClientKey: String? = null

    @JsonProperty("client_key_password")
    @JsonSchemaTitle("Client key password")
    @JsonPropertyDescription(
        "Password for keystorage. This field is optional. If you do not add it - the password will be generated automatically.",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var sslClientPassword: String? = null
}

@JsonSchemaTitle("verify-full")
@JsonSchemaDescription(
    "To always require encryption and verify that the source has a valid SSL certificate."
)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class SslVerifyFull : EncryptionSpecification {
    @JsonProperty("ca_certificate", required = true)
    @JsonSchemaTitle("CA certificate")
    @JsonPropertyDescription(
        "CA certificate",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    lateinit var sslCertificate: String

    @JsonProperty("client_certificate", required = false)
    @JsonSchemaTitle("Client certificate File")
    @JsonPropertyDescription(
        "Client certificate (this is not a required field, but if you want to use it, you will need to add the Client key as well)",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var sslClientCertificate: String? = null

    @JsonProperty("client_key")
    @JsonSchemaTitle("Client Key")
    @JsonPropertyDescription(
        "Client key (this is not a required field, but if you want to use it, you will need to add the Client certificate as well)",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var sslClientKey: String? = null

    @JsonProperty("client_key_password")
    @JsonSchemaTitle("Client key password")
    @JsonPropertyDescription(
        "Password for keystorage. This field is optional. If you do not add it - the password will be generated automatically.",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true,"multiline":true}""")
    var sslClientPassword: String? = null
}

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.ssl_mode")
class MicronautPropertiesFriendlyEncryptionSpecification {
    var mode: String = "require"
    var sslCertificate: String? = null

    @JsonValue
    fun asEncryption(): EncryptionSpecification =
        when (mode) {
            "disable" -> EncryptionDisable
            "allow" -> EncryptionAllow
            "prefer" -> EncryptionPrefer
            "require" -> EncryptionRequire
            "verify-ca" -> SslVerifyCertificate().also { it.sslCertificate = sslCertificate!! }
            "verify-full" -> SslVerifyFull().also { it.sslCertificate = sslCertificate!! }
            else -> throw ConfigErrorException("invalid value $mode")
        }
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "method")
@JsonSubTypes(
    JsonSubTypes.Type(value = CdcReplicationMethodConfigurationSpecification::class, name = "CDC"),
    JsonSubTypes.Type(
        value = XminReplicationMethodConfigurationSpecification::class,
        name = "Xmin"
    ),
    JsonSubTypes.Type(
        value = StandardReplicationMethodConfigurationSpecification::class,
        name = "Standard"
    ),
)
@JsonSchemaTitle("Update Method")
@JsonSchemaDescription("Configures how data is extracted from the database.")
sealed interface IncrementalConfigurationSpecification

@JsonSchemaTitle("Scan Changes with User Defined Cursor")
@JsonSchemaDescription(
    "Incrementally detects new inserts and updates using the " +
        "<a href=\"https://docs.airbyte.com/understanding-airbyte/connections/incremental-append/" +
        "#user-defined-cursor\">cursor column</a> chosen when configuring a connection " +
        "(e.g. created_at, updated_at).",
)
data object StandardReplicationMethodConfigurationSpecification :
    IncrementalConfigurationSpecification

@JsonSchemaTitle("Detect Changes with Xmin System Column")
@JsonSchemaDescription(
    "<i>Recommended</i> - Incrementally reads new inserts and updates via Postgres " +
        "<a href=\"https://docs.airbyte.com/integrations/sources/postgres/#xmin\">" +
        "Xmin system column</a>. Suitable for databases that have low transaction pressure."
)
data object XminReplicationMethodConfigurationSpecification : IncrementalConfigurationSpecification

@JsonSchemaTitle("Read Changes using Change Data Capture (CDC)")
@JsonSchemaDescription(
    "<i>Recommended</i> - " +
        "Incrementally reads new inserts, updates, and deletes using Postgres's <a href=" +
        "\"https://docs.airbyte.com/integrations/connectors/source-postgres#getting-started\"" +
        "> change data capture feature</a>. This must be enabled on your database.",
)
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "testing")
class CdcReplicationMethodConfigurationSpecification : IncrementalConfigurationSpecification {

    @JsonProperty("invalid_cdc_cursor_position_behavior")
    @JsonSchemaTitle("Invalid CDC Position Behavior (Advanced)")
    @JsonPropertyDescription(
        "Determines whether Airbyte should fail or re-sync data in case of an stale/invalid cursor value in the mined logs. If 'Fail sync' is chosen, a user will have to manually reset the connection before being able to continue syncing data. If 'Re-sync data' is chosen, Airbyte will automatically trigger a refresh but could lead to higher cloud costs and data loss.",
    )
    @JsonSchemaDefault("Fail sync")
    @JsonSchemaInject(json = """{"order":6,"enum":["Fail sync","Re-sync data"]}""")
    var invalidCdcCursorPositionBehavior: String? = "Fail sync"

    @JsonProperty("initial_load_timeout_hours")
    @JsonSchemaTitle("Initial Load Timeout in Hours (Advanced)")
    @JsonPropertyDescription(
        "The amount of time an initial load is allowed to continue for before catching up on CDC events.",
    )
    @JsonSchemaDefault("8")
    @JsonSchemaInject(json = """{"order":7,"min":4,"max":24}""")
    var initialLoadTimeoutHours: Int? = 8

    @JsonProperty("debezium_shutdown_timeout_seconds")
    @JsonSchemaTitle("Debezium Engine Shutdown Timeout in Seconds (Advanced)")
    @JsonPropertyDescription(
        "The amount of time to allow the Debezium Engine to shut down, in seconds.",
    )
    @JsonSchemaDefault("60")
    @JsonSchemaInject(json = """{"order":8,"min":1,"max":3600}""")
    var debeziumShutdownTimeoutSeconds: Int? = 60

    @JsonProperty("replication_slot", required = true)
    @JsonSchemaTitle("Replication Slot")
    @JsonPropertyDescription(
        "A plugin logical replication slot. Read about <a href=\\\"https://docs.airbyte.com/integrations/sources/postgres#step-3-create-replication-slot\\\">replication slots</a>."
    )
    @JsonSchemaInject(json = """{"order":1,"always_show":true, "minLength":1}""")
    lateinit var replicationSlot: String

    @JsonProperty("publication", required = true)
    @JsonSchemaTitle("Publication")
    @JsonPropertyDescription(
        "A Postgres publication used for consuming changes. Read about <a href=\\\"https://docs.airbyte.com/integrations/sources/postgres#step-4-create-publications-and-replication-identities-for-tables\\\">publications and replication identities</a>."
    )
    @JsonSchemaInject(json = """{"order":2,"always_show":true, "minLength":1}""")
    lateinit var publication: String

    @JsonProperty("initial_waiting_seconds")
    @JsonSchemaTitle("Initial Waiting Time in Seconds (Advanced)")
    @JsonPropertyDescription(
        "The amount of time the connector will wait when it launches to determine if there is new data to sync or not. Defaults to 1200 seconds. Valid range: 120 seconds to 2400 seconds. Read about <a href=\"https://docs.airbyte.com/integrations/sources/postgres/postgres-troubleshooting#advanced-setting-up-initial-cdc-waiting-time\">initial waiting time</a>."
    )
    @JsonSchemaDefault("1200")
    @JsonSchemaInject(json = """{"order":3,"min":120,"max":2400}""")
    var initialWaitingSeconds: Int? = 1200

    // WARNING: The British English spelling of "behaviour" was used in the old connector.
    //  We've updated the UI to use the American English spelling of "behavior".
    //  The json representation must remain unchanged to avoid needing a migration.
    @JsonProperty("lsn_commit_behaviour")
    @JsonSchemaTitle("LSN commit behavior")
    @JsonPropertyDescription(
        "Determines when Airbyte should flush the LSN of processed WAL logs in the source database. `After loading Data in the destination` is default. If `While reading Data` is selected, in case of a downstream failure (while loading data into the destination), next sync would result in a full sync."
    )
    @JsonSchemaDefault("After loading Data in the destination")
    @JsonSchemaInject(
        json =
            """{"order":4,"enum":[ "While reading Data", "After loading Data in the destination"]}"""
    )
    var lsnCommitBehavior: String? = "After loading Data in the destination"

    @JsonProperty("heartbeat_action_query")
    @JsonSchemaTitle("Debezium heartbeat query (Advanced)")
    @JsonPropertyDescription(
        "Specifies a query that the connector executes on the source database when the connector sends a heartbeat message. Please see the <a href=\"https://docs.airbyte.com/integrations/sources/postgres/postgres-troubleshooting#advanced-wal-disk-consumption-and-heartbeat-action-query\">setup guide</a> for how and when to configure this setting."
    )
    @JsonSchemaDefault("")
    @JsonSchemaInject(json = """{"order":5}""")
    var heartbeatActionQuery: String? = ""
}

@ConfigurationProperties("$CONNECTOR_CONFIG_PREFIX.cursor")
class MicronautPropertiesFriendlyCursorConfigurationSpecification {
    var cursorMethod: String = "user_defined"
    var invalidCdcCursorPositionBehavior: String? = null
    var initialLoadTimeoutHours: Int? = null
    var debeziumShutdownTimeoutSeconds: Int? = null

    fun asIncrementalConfigurationSpecification(): IncrementalConfigurationSpecification =
        when (cursorMethod) {
            "user_defined" -> StandardReplicationMethodConfigurationSpecification
            "cdc" ->
                CdcReplicationMethodConfigurationSpecification().also {
                    it.invalidCdcCursorPositionBehavior = invalidCdcCursorPositionBehavior
                    it.initialLoadTimeoutHours = initialLoadTimeoutHours
                    it.debeziumShutdownTimeoutSeconds = debeziumShutdownTimeoutSeconds
                }
            else -> throw ConfigErrorException("invalid value $cursorMethod")
        }
}
