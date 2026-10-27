/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.check.CheckSectionHandler
import io.airbyte.cdk.check.CloudHostCheck
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.integrations.source.postgres.config.CdcIncrementalConfiguration
import io.airbyte.integrations.source.postgres.config.CdcReplicationMethodConfigurationSpecification
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationSpecification
import io.airbyte.integrations.source.postgres.config.SECTION_CONNECTION
import io.airbyte.integrations.source.postgres.config.SECTION_CREDENTIALS
import io.airbyte.integrations.source.postgres.config.SECTION_SYNC_METHOD
import io.airbyte.integrations.source.postgres.config.UserDefinedCursorIncrementalConfiguration
import io.airbyte.integrations.source.postgres.config.XminIncrementalConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.SQLException

/**
 * Section checks for the stepped setup form, see the `sections` declared by
 * [PostgresSourceConfigurationSpecification]. Each check validates the fields of its section and of
 * the sections before it, and nothing beyond:
 * - [SECTION_CONNECTION]: the server is reachable at host:port, through the SSH tunnel and with the
 *   SSL mode configured. No credentials are involved.
 * - [SECTION_CREDENTIALS]: the user can log into the database, which proves the server reachable
 *   once more, and the connector's check queries run.
 * - [SECTION_SYNC_METHOD]: the credentials check, plus the replication method's prerequisites on
 *   the server.
 * - The review section is the last one, so the CDK runs the full check for it.
 */
@Singleton
class PostgresSourceCheckSectionHandler(
    private val configFactory:
        SourceConfigurationFactory<
            PostgresSourceConfigurationSpecification,
            PostgresSourceConfiguration,
        >,
    private val checkQueries: JdbcCheckQueries,
    private val featureFlags: Set<FeatureFlag>,
) : CheckSectionHandler<PostgresSourceConfigurationSpecification> {
    private val log = KotlinLogging.logger {}

    override fun check(section: String, pojo: PostgresSourceConfigurationSpecification) {
        when (section) {
            SECTION_CONNECTION -> checkConnection(pojo)
            SECTION_CREDENTIALS -> checkCredentials(pojo)
            SECTION_SYNC_METHOD -> checkSyncMethod(pojo)
            else -> throw ConfigErrorException("Section '$section' has no section check.")
        }
    }

    /**
     * The server must be reachable at host:port, through the SSH tunnel if one is configured, and
     * accept the SSL mode. Credentials belong to the next section, so the probe logs in with
     * placeholder ones and takes an authentication failure as proof that the server was reached:
     * Postgres only rejects credentials once the TCP connection and the SSL negotiation succeeded.
     * The database name is part of this section as well but the server validates it after
     * authentication only; the credentials check covers it.
     */
    private fun checkConnection(pojo: PostgresSourceConfigurationSpecification) {
        val host: String = required(SECTION_CONNECTION, "host") { pojo.host }
        val probe =
            PostgresSourceConfigurationSpecification().apply {
                this.host = host
                port = pojo.port
                database = optional { pojo.database } ?: PROBE_DATABASE
                username = PROBE_USERNAME
                password = PROBE_PASSWORD
                jdbcUrlParams = pojo.jdbcUrlParams
                encryptionJson = pojo.getEncryptionValue()
                tunnelMethodJson = pojo.getTunnelMethodValue()
                additionalPropertiesMap = pojo.additionalPropertiesMap
            }
        val config: PostgresSourceConfiguration = configFactory.make(probe)
        validateNetworkSettings(config)
        log.info {
            "Probing the server at ${config.realHost}:${config.realPort} " +
                "with placeholder credentials."
        }
        try {
            JdbcConnectionFactory(config).get().close()
            log.info { "The server accepted the placeholder credentials; it is reachable." }
        } catch (e: SQLException) {
            val sqlState: String = e.sqlState ?: throw e
            if (
                sqlState.startsWith(SQLSTATE_CLASS_INVALID_AUTHORIZATION) ||
                    sqlState == SQLSTATE_INVALID_CATALOG_NAME
            ) {
                log.info {
                    "The server rejected the placeholder credentials (SQLSTATE $sqlState); " +
                        "it is reachable."
                }
                return
            }
            throw e
        }
    }

    /**
     * Everything the connection check needs, plus the database name and a user who can log into it.
     * The login proves the server reachable, so the placeholder probe is not repeated.
     */
    private fun checkCredentials(pojo: PostgresSourceConfigurationSpecification) {
        requireCredentials(SECTION_CREDENTIALS, pojo)
        val config: PostgresSourceConfiguration = configFactory.make(pojo)
        validateNetworkSettings(config)
        log.info {
            "Logging into database '${config.database}' as '${config.jdbcProperties["user"]}'."
        }
        JdbcConnectionFactory(config).get().use { conn: Connection ->
            checkQueries.executeAll(conn)
        }
    }

    /**
     * Everything the credentials check needs, plus the replication method's prerequisites on the
     * server: no xmin wraparound for Xmin; for CDC `wal_level = logical`, the replication slot and
     * the publication exist on this database, and the user may open a replication connection.
     */
    private fun checkSyncMethod(pojo: PostgresSourceConfigurationSpecification) {
        requireCredentials(SECTION_SYNC_METHOD, pojo)
        val replication = pojo.getIncrementalConfigurationSpecificationValue()
        if (replication is CdcReplicationMethodConfigurationSpecification) {
            required(SECTION_SYNC_METHOD, "replication_slot") { replication.replicationSlot }
            required(SECTION_SYNC_METHOD, "publication") { replication.publication }
        }
        val config: PostgresSourceConfiguration = configFactory.make(pojo)
        validateNetworkSettings(config)
        JdbcConnectionFactory(config).get().use { conn: Connection ->
            checkQueries.executeAll(conn)
            when (val incremental = config.incrementalConfiguration) {
                is XminIncrementalConfiguration -> {
                    if (PostgresSourceMetadataQuerier.dbNumWraparound(conn) > 0) {
                        throw ConfigErrorException(
                            PostgresSourceMetadataQuerier.xminWraparoundError,
                        )
                    }
                }
                is CdcIncrementalConfiguration -> checkCdcPrerequisites(conn, config, incremental)
                is UserDefinedCursorIncrementalConfiguration ->
                    log.info { "Cursor-based replication has no server-side prerequisite." }
            }
        }
    }

    private fun checkCdcPrerequisites(
        conn: Connection,
        config: PostgresSourceConfiguration,
        cdc: CdcIncrementalConfiguration,
    ) {
        val walLevel: String? =
            conn.createStatement().use { stmt ->
                stmt.executeQuery("SHOW wal_level").use { rs ->
                    if (rs.next()) rs.getString(1) else null
                }
            }
        if (walLevel != "logical") {
            throw ConfigErrorException(
                "CDC requires the server setting wal_level = logical; it is '$walLevel'.",
            )
        }
        val plugin: String =
            conn
                .prepareStatement(
                    "SELECT plugin FROM pg_replication_slots WHERE slot_name = ? AND database = ?",
                )
                .use { stmt ->
                    stmt.setString(1, cdc.replicationSlot)
                    stmt.setString(2, config.database)
                    stmt.executeQuery().use { rs ->
                        if (rs.next()) rs.getString("plugin") else null
                    }
                }
                ?: throw ConfigErrorException(
                    "Replication slot '${cdc.replicationSlot}' does not exist " +
                        "in database '${config.database}'.",
                )
        if (plugin != "pgoutput") {
            throw ConfigErrorException(
                "Replication slot '${cdc.replicationSlot}' uses the '$plugin' output plugin; " +
                    "Airbyte requires pgoutput.",
            )
        }
        val publicationExists: Boolean =
            conn.prepareStatement("SELECT 1 FROM pg_publication WHERE pubname = ?").use { stmt ->
                stmt.setString(1, cdc.publication)
                stmt.executeQuery().use { rs -> rs.next() }
            }
        if (!publicationExists) {
            throw ConfigErrorException(
                "Publication '${cdc.publication}' does not exist in database '${config.database}'.",
            )
        }
        // The replication connection READ opens first; it fails for a user without the
        // REPLICATION attribute (or the rds_replication role).
        log.info { "Opening a replication connection as '${config.jdbcProperties["user"]}'." }
        (PostgresSourceJdbcConnectionFactory(config).getReplication() as Connection).close()
    }

    /** The Cloud-only rules on the host and the encryption, which the full check applies too. */
    private fun validateNetworkSettings(config: PostgresSourceConfiguration) {
        CloudHostCheck.validate(config.realHost, config.sshTunnel, featureFlags)
        PostgresSourceMetadataQuerier.validateCloudSslConfiguration(config, featureFlags)
    }

    private fun requireCredentials(
        section: String,
        pojo: PostgresSourceConfigurationSpecification,
    ) {
        required(section, "host") { pojo.host }
        required(section, "database") { pojo.database }
        required(section, "username") { pojo.username }
        if (pojo.servicePrincipalAuth == true) {
            required(section, "entra_tenant_id") { pojo.entraTenantId }
            required(section, "entra_client_id") { pojo.entraClientId }
            required(section, "password") { pojo.password }
        }
    }

    /**
     * Reads a field of the partial configuration; an unset `lateinit`, a null or a blank value
     * becomes a [ConfigErrorException] naming the field and the section which needs it.
     */
    private fun <V : Any> required(section: String, name: String, read: () -> V?): V {
        val value: V? = optional(read)
        if (value == null || (value is String && value.isBlank())) {
            throw ConfigErrorException("The '$section' section check requires the '$name' field.")
        }
        return value
    }

    private fun <V : Any> optional(read: () -> V?): V? =
        try {
            read()
        } catch (_: UninitializedPropertyAccessException) {
            null
        }

    companion object {
        const val PROBE_USERNAME = "airbyte_connection_check"
        const val PROBE_PASSWORD = "airbyte_connection_check"
        const val PROBE_DATABASE = "postgres"

        /** SQLSTATE class 28: invalid_authorization_specification, invalid_password. */
        const val SQLSTATE_CLASS_INVALID_AUTHORIZATION = "28"
        /** SQLSTATE 3D000: the database does not exist, reported after authentication. */
        const val SQLSTATE_INVALID_CATALOG_NAME = "3D000"
    }
}
