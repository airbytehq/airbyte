/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.spec

import com.fasterxml.jackson.annotation.JsonGetter
import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSetter
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.cdk.ssh.MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.micronaut.context.annotation.ConfigurationBuilder
import jakarta.inject.Singleton

@Singleton
@JsonSchemaTitle("Postgres Destination Specification")
@SuppressFBWarnings("NP_NONNULL_RETURN_VIOLATION")
class PostgresSpecification : ConfigurationSpecification() {
    @get:JsonSchemaTitle("Host")
    @get:JsonPropertyDescription("Hostname of the database.")
    @get:JsonProperty("host")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 0}""")
    val host: String = ""

    @get:JsonSchemaTitle("Port")
    @get:JsonPropertyDescription("Port of the database.")
    @get:JsonProperty("port")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 1, "minimum": 0, "maximum": 65536, "examples": ["5432"]}""")
    val port: Int = 5432

    @get:JsonSchemaTitle("Database Name")
    @get:JsonPropertyDescription("Name of the database.")
    @get:JsonProperty("database")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 2}""")
    val database: String = ""

    @get:JsonSchemaTitle("Default Schema")
    @get:JsonPropertyDescription(
        "The default schema tables are written. If not specified otherwise, the \"public\" schema will be used."
    )
    @get:JsonProperty("schema")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 3, "examples": ["public"], "default": "public"}""")
    val schema: String = "public"

    @get:JsonSchemaTitle("Username")
    @get:JsonPropertyDescription("Username to access the database.")
    @get:JsonProperty("username")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 4}""")
    val username: String = ""

    @get:JsonSchemaTitle("Password")
    @get:JsonPropertyDescription("Password associated with the username.")
    @get:JsonProperty("password")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 5, "airbyte_secret": true}""")
    val password: String? = null

    @get:JsonSchemaTitle("SSL Modes")
    @get:JsonPropertyDescription(
        """SSL connection modes.
  <b>disable</b> - Disables encryption of communication between Airbyte and destination database.
  <b>allow</b> - Enables encryption only when required by the destination database.
  <b>prefer</b> - Allows unencrypted connections only if the destination database does not support encryption.
  <b>require</b> - Always require encryption. If the destination database server does not support encryption, connection will fail.
  <b>verify-ca</b> - Always require encryption and verifies that the destination database server has a valid SSL certificate.
  <b>verify-full</b> - This is the most secure mode. Always require encryption and verifies the identity of the destination database server.
 See more information - <a href="https://jdbc.postgresql.org/documentation/head/ssl-client.html"> in the docs</a>."""
    )
    @get:JsonProperty("ssl_mode")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 6}""")
    val sslMode: SslMode? = null

    @get:JsonSchemaTitle("CDC deletion mode")
    @get:JsonPropertyDescription(
        """Whether to execute CDC deletions as hard deletes (i.e. propagate source deletions to the destination), or soft deletes (i.e. leave a tombstone record in the destination). Defaults to hard deletes.""",
    )
    @get:JsonProperty("cdc_deletion_mode", defaultValue = "Hard delete")
    @get:JsonSchemaInject(
        json = """{"group": "sync_behavior", "order": 7, "always_show": true}""",
    )
    val cdcDeletionMode: CdcDeletionMode? = null

    @get:JsonSchemaTitle("JDBC URL Params")
    @get:JsonPropertyDescription(
        """Additional properties to pass to the JDBC URL string when connecting to the database formatted as 'key=value' pairs separated by the symbol '&'. (example: key1=value1&key2=value2&key3=value3)."""
    )
    @get:JsonProperty("jdbc_url_params")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 8}""")
    val jdbcUrlParams: String? = null

    @get:JsonSchemaTitle("Airbyte Internal Schema Name")
    @get:JsonPropertyDescription(
        """Airbyte will use this schema for various internal tables. In legacy raw tables mode, the raw tables will be stored in this schema. Defaults to "airbyte_internal".""",
    )
    @get:JsonProperty("raw_data_schema")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 9}""")
    val internalTableSchema: String? = null

    @get:JsonSchemaTitle("Disable Final Tables. (WARNING! Unstable option; Columns in raw table schema might change between versions)")
    @get:JsonPropertyDescription(
        """Disable Writing Final Tables. WARNING! The data format in _airbyte_data is likely stable but there are no guarantees that other metadata columns will remain the same in future versions""",
    )
    @get:JsonProperty("disable_type_dedupe")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 10}""")
    @Suppress("RedundantNullableReturnType")
    val legacyRawTablesOnly: Boolean? = false

    @get:JsonSchemaTitle("Drop tables with CASCADE. (WARNING! Risk of unrecoverable data loss)")
    @get:JsonPropertyDescription(
        """Drop tables with CASCADE. WARNING! This will delete all data in all dependent objects (views, etc.). Use with caution. This option is intended for usecases which can easily rebuild the dependent objects."""
    )
    @get:JsonProperty("drop_cascade")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 11}""")
    @Suppress("RedundantNullableReturnType")
    val dropCascade: Boolean? = false

    @get:JsonSchemaTitle("Unconstrained numeric columns")
    @get:JsonPropertyDescription(
        """Create numeric columns as unconstrained DECIMAL instead of NUMBER(38, 9). This will allow increased precision in numeric values. (this is disabled by default for backwards compatibility, but is recommended to enable)"""
    )
    @get:JsonProperty("unconstrained_number")
    @get:JsonSchemaInject(json = """{"group": "connection", "order": 12}""")
    @Suppress("RedundantNullableReturnType")
    val unconstrainedNumber: Boolean? = false

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "tunnel_method")
    val tunnelMethod = MicronautPropertiesFriendlySshTunnelMethodConfigurationSpecification()

    @JsonIgnore var tunnelMethodJson: SshTunnelMethodConfiguration? = null

    @JsonSetter("tunnel_method")
    fun setTunnelMethodValue(value: SshTunnelMethodConfiguration?) {
        tunnelMethodJson = value
    }

    @JsonGetter("tunnel_method")
    @JsonSchemaTitle("SSH Tunnel Method")
    @JsonPropertyDescription(
        "Whether to initiate an SSH tunnel before connecting to the database, and if so, which kind of authentication to use.",
    )
    @JsonSchemaInject(json = """{"group": "connection", "order": 11}""")
    fun getTunnelMethodValue(): SshTunnelMethodConfiguration? =
        tunnelMethodJson ?: tunnelMethod.asSshTunnelMethod()
}

@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "mode")
@JsonSubTypes(
    JsonSubTypes.Type(value = SslModeDisable::class, name = SslModeDisable.MODE),
    JsonSubTypes.Type(value = SslModeAllow::class, name = SslModeAllow.MODE),
    JsonSubTypes.Type(value = SslModePrefer::class, name = SslModePrefer.MODE),
    JsonSubTypes.Type(value = SslModeRequire::class, name = SslModeRequire.MODE),
    JsonSubTypes.Type(value = SslModeVerifyCa::class, name = SslModeVerifyCa.MODE),
    JsonSubTypes.Type(value = SslModeVerifyFull::class, name = SslModeVerifyFull.MODE),
)
sealed interface SslMode {
    @get:JsonProperty("mode") val mode: String
}

@JsonSchemaTitle("disable")
@JsonSchemaDescription("Disable SSL.")
class SslModeDisable : SslMode {
    companion object {
        const val MODE = "disable"
    }
    override val mode: String = MODE
}

@JsonSchemaTitle("allow")
@JsonSchemaDescription("Allow SSL mode.")
class SslModeAllow : SslMode {
    companion object {
        const val MODE = "allow"
    }
    override val mode: String = MODE
}

@JsonSchemaTitle("prefer")
@JsonSchemaDescription("Prefer SSL mode.")
class SslModePrefer : SslMode {
    companion object {
        const val MODE = "prefer"
    }
    override val mode: String = MODE
}

@JsonSchemaTitle("require")
@JsonSchemaDescription("Require SSL mode.")
class SslModeRequire : SslMode {
    companion object {
        const val MODE = "require"
    }
    override val mode: String = MODE
}

@JsonSchemaTitle("verify-ca")
@JsonSchemaDescription("Verify-ca SSL mode.")
class SslModeVerifyCa : SslMode {
    companion object {
        const val MODE = "verify-ca"
    }
    override val mode: String = MODE
}

@JsonSchemaTitle("verify-full")
@JsonSchemaDescription("Verify-full SSL mode.")
class SslModeVerifyFull : SslMode {
    companion object {
        const val MODE = "verify-full"
    }
    override val mode: String = MODE
}

enum class CdcDeletionMode(@Suppress("unused") @get:JsonValue val cdcDeletionMode: String) {
    HARD_DELETE("Hard delete"),
    SOFT_DELETE("Soft delete"),
}

@Singleton
class PostgresSpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP,
        )
    override val supportsIncremental = true
    override val groups =
        listOf(
            DestinationSpecificationExtension.Group("connection", "Connection"),
            DestinationSpecificationExtension.Group("sync_behavior", "Sync Behavior"),
            DestinationSpecificationExtension.Group("advanced", "Advanced"),
        )
}
