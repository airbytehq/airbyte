/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.AIRBYTE_CLOUD_ENV
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/**
 * StarRocks destination connector configuration spec (OSS).
 *
 * Data plane = HTTP Stream Load (`http_port`, default 8030); control plane (DDL, `SELECT
 * current_version()`) = MySQL protocol (`port`, default 9030). See the connector's CONTRIBUTING.md
 * for the shared-data feature gating.
 */
@Singleton
@Requires(notEnv = [AIRBYTE_CLOUD_ENV])
class StarrocksSpecification : ConfigurationSpecification() {
    @get:JsonSchemaTitle("Host")
    @get:JsonPropertyDescription("FE host of the StarRocks cluster.")
    @get:JsonProperty("host")
    @get:JsonSchemaInject(json = """{"order": 0, "group": "connection"}""")
    val host: String = ""

    @get:JsonSchemaTitle("Query Port")
    @get:JsonPropertyDescription("MySQL-protocol port for queries/DDL. Default: 9030")
    @get:JsonProperty("port")
    @get:JsonSchemaInject(json = """{"order": 1, "default": 9030, "group": "connection"}""")
    val port: Int = 9030

    @get:JsonSchemaTitle("HTTP Port")
    @get:JsonPropertyDescription("FE HTTP port for Stream Load. Default: 8030")
    @get:JsonProperty("http_port")
    @get:JsonSchemaInject(json = """{"order": 2, "default": 8030, "group": "connection"}""")
    val httpPort: Int = 8030

    @get:JsonSchemaTitle("Username")
    @get:JsonPropertyDescription("Username to access the database.")
    @get:JsonProperty("username")
    @get:JsonSchemaInject(json = """{"order": 3, "default": "root", "group": "connection"}""")
    val username: String = "root"

    @get:JsonSchemaTitle("Password")
    @get:JsonPropertyDescription("Password associated with the username.")
    @get:JsonProperty("password")
    @get:JsonSchemaInject(json = """{"order": 4, "airbyte_secret": true, "group": "connection"}""")
    val password: String = ""

    @get:JsonSchemaTitle("Database")
    @get:JsonPropertyDescription("Name of the target database.")
    @get:JsonProperty("database")
    @get:JsonSchemaInject(json = """{"order": 5, "group": "connection"}""")
    val database: String = ""

    @get:JsonSchemaTitle("SSL")
    @get:JsonPropertyDescription("Use SSL for the MySQL-protocol connection.")
    @get:JsonProperty("ssl")
    @get:JsonSchemaInject(json = """{"order": 6, "default": false, "group": "security"}""")
    val ssl: Boolean = false

    @get:JsonSchemaTitle("Enable JSON")
    @get:JsonPropertyDescription(
        "Store object fields using the StarRocks JSON type instead of a JSON-encoded string. " +
            "Useful for sources with rich JSON columns (e.g. Postgres jsonb).",
    )
    @get:JsonProperty("enable_json")
    @get:JsonSchemaInject(json = """{"order": 11, "default": false, "group": "loading"}""")
    val enableJson: Boolean = false

    @get:JsonSchemaTitle("CDC Deletion Mode")
    @get:JsonPropertyDescription(
        "How to handle CDC deletes for deduped streams. 'Hard delete' removes the row from the " +
            "destination. 'Soft delete' keeps the row and marks it via the _ab_cdc_deleted_at column " +
            "(query WHERE _ab_cdc_deleted_at IS NULL for live rows).",
    )
    @get:JsonProperty("cdc_deletion_mode")
    @get:JsonSchemaInject(
        json =
            """{"order": 12, "default": "Hard delete", "enum": ["Hard delete", "Soft delete"], "group": "loading"}""",
    )
    val cdcDeletionMode: String = CdcDeletionMode.HARD_DELETE

    @get:JsonSchemaTitle("Load Format")
    @get:JsonPropertyDescription(
        "Stream Load body format. CSV is compact and high-throughput; JSON avoids CSV escaping edge " +
            "cases (e.g. a literal \\N string being stored as NULL), preserves large integer/decimal " +
            "precision, and supports request-body compression (CSV does not).",
    )
    @get:JsonProperty("load_format")
    @get:JsonSchemaInject(json = """{"order": 10, "group": "loading"}""")
    val loadFormat: LoadFormatSpec = CsvFormat()

    @get:JsonSchemaTitle("SSL Mode")
    @get:JsonPropertyDescription(
        "Certificate verification for the SSL (JDBC) connection when SSL is enabled. 'required' " +
            "encrypts but does not verify the server certificate (use for self-signed certs); " +
            "'verify_ca'/'verify_identity' verify the certificate against the JVM trust store.",
    )
    @get:JsonProperty("ssl_mode")
    @get:JsonSchemaInject(
        json =
            """{"order": 7, "default": "required", "enum": ["required", "verify_ca", "verify_identity"], "group": "security"}""",
    )
    val sslMode: String = SslMode.REQUIRED

    @get:JsonSchemaTitle("SSH Tunnel Method")
    @get:JsonPropertyDescription(
        "Whether to initiate an SSH tunnel (jump server / bastion) before connecting, and the auth " +
            "to use. The tunnel carries the JDBC control plane only — Stream Load's HTTP data plane " +
            "(with its FE->BE 307 redirect) cannot traverse a single local forward. When a tunnel is " +
            "configured you must also set the Load Method to 'SQL', which loads over this same JDBC " +
            "connection.",
    )
    @get:JsonProperty("tunnel_method")
    @get:JsonSchemaInject(json = """{"order": 8, "group": "security"}""")
    val tunnelMethod: SshTunnelMethodConfiguration = SshNoTunnelMethod

    @get:JsonSchemaTitle("Load Method")
    @get:JsonPropertyDescription(
        "How records are loaded. 'Stream Load' (default) is StarRocks' high-throughput HTTP bulk " +
            "load. 'SQL' loads over the JDBC connection with batched INSERT/DELETE — lower throughput, " +
            "but it works over an SSH tunnel and end-to-end SSL (the Stream Load HTTP data plane does " +
            "neither). Use 'SQL' when an SSH tunnel is configured. (The 'Load Format' option above " +
            "applies to Stream Load only.)",
    )
    @get:JsonProperty("load_method")
    @get:JsonSchemaInject(
        json =
            """{"order": 9, "default": "Stream Load", "enum": ["Stream Load", "SQL"], "group": "loading"}""",
    )
    val loadMethod: String = LoadMethod.STREAM_LOAD

    @get:JsonSchemaTitle("Replication Number")
    @get:JsonPropertyDescription(
        "Replicas per tablet for tables this connector creates (the StarRocks `replication_num` table " +
            "property). Leave unset to use the cluster default (normally 3) — correct for shared-data and " +
            "multi-BE shared-nothing clusters. Set to 1 for a single-BE shared-nothing cluster, which " +
            "otherwise rejects CREATE TABLE (\"replication num should be less than the number of available " +
            "BE\"). Applies only when tables are created; existing tables are left unchanged.",
    )
    @get:JsonProperty("replication_num")
    @get:JsonSchemaInject(json = """{"order": 13, "minimum": 1, "group": "advanced"}""")
    val replicationNum: Int? = null
}

object LoadMethod {
    const val STREAM_LOAD = "Stream Load"
    const val SQL = "SQL"

    /** Whether to load over JDBC (batched INSERT/DELETE) instead of HTTP Stream Load. */
    fun isSql(method: String): Boolean = method.equals(SQL, ignoreCase = true)
}

object CdcDeletionMode {
    const val HARD_DELETE = "Hard delete"
    const val SOFT_DELETE = "Soft delete"

    /** Whether the configured mode is soft delete (retain rows with the tombstone). */
    fun isSoftDelete(mode: String): Boolean = mode.equals(SOFT_DELETE, ignoreCase = true)
}

/**
 * Stream Load body format as a discriminated union, so the UI only offers compression under JSON
 * (StarRocks decompresses JSON request bodies only — there is no valid CSV+compression
 * combination).
 */
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "format_type")
@JsonSubTypes(
    JsonSubTypes.Type(value = CsvFormat::class, name = CsvFormat.TYPE),
    JsonSubTypes.Type(value = JsonFormat::class, name = JsonFormat.TYPE),
)
sealed interface LoadFormatSpec {
    @get:JsonProperty("format_type") val formatType: String
}

/** True when the format ships a JSON Stream Load body. */
val LoadFormatSpec.isJson: Boolean
    get() = this is JsonFormat

/** Compression algorithm for the format ("none" for CSV, which StarRocks cannot decompress). */
val LoadFormatSpec.compression: String
    get() = (this as? JsonFormat)?.compression ?: LoadCompression.NONE

@JsonSchemaTitle("CSV")
@JsonSchemaDescription(
    "Compact, high-throughput CSV body. Note: a literal `\\N` string is stored as NULL and very " +
        "large BIGINT/DECIMAL values can lose precision — use JSON if that matters.",
)
class CsvFormat : LoadFormatSpec {
    companion object {
        const val TYPE = "CSV"
    }

    override val formatType: String = TYPE
}

@JsonSchemaTitle("JSON")
@JsonSchemaDescription(
    "JSON body. Avoids CSV escaping edge cases, preserves large integer/decimal precision, and can " +
        "be compressed (CSV cannot — StarRocks only decompresses JSON request bodies).",
)
data class JsonFormat(
    @get:JsonSchemaTitle("Compression")
    @get:JsonPropertyDescription(
        "Compress the Stream Load request body to cut network traffic on large batches. Requires a " +
            "cluster >= 3.3.2 (else the connection check fails). 'zstd' compresses better than 'gzip' " +
            "at similar or lower CPU cost.",
    )
    @get:JsonProperty("compression")
    @get:JsonSchemaInject(
        json = """{"order": 1, "default": "none", "enum": ["none", "gzip", "zstd"]}"""
    )
    val compression: String = LoadCompression.NONE,
) : LoadFormatSpec {
    companion object {
        const val TYPE = "JSON"
    }

    override val formatType: String = TYPE
}

object LoadCompression {
    const val NONE = "none"
    const val GZIP = "gzip"
    const val ZSTD = "zstd"

    /** Whether any request-body compression is requested (only honored on the JSON load format). */
    fun isEnabled(mode: String): Boolean = !mode.equals(NONE, ignoreCase = true)
}

object SslMode {
    const val REQUIRED = "required"
    const val VERIFY_CA = "verify_ca"
    const val VERIFY_IDENTITY = "verify_identity"

    /** Maps the spec value to a MySQL connector-j `sslMode` (used only when ssl is enabled). */
    fun toConnectorJ(mode: String): String =
        when (mode.lowercase()) {
            VERIFY_CA -> "VERIFY_CA"
            VERIFY_IDENTITY -> "VERIFY_IDENTITY"
            else -> "REQUIRED"
        }
}

@Singleton
class StarrocksSpecificationExtension : DestinationSpecificationExtension {
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
            DestinationSpecificationExtension.Group("security", "Security & Tunnel"),
            DestinationSpecificationExtension.Group("loading", "Data Loading"),
            DestinationSpecificationExtension.Group("advanced", "Advanced"),
        )
}
