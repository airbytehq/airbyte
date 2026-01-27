/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.read.querySingleValue
import io.airbyte.integrations.source.postgres.PostgresSourceJdbcConnectionFactory
import io.airbyte.integrations.source.postgres.config.CdcIncrementalConfiguration
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.debezium.connector.postgresql.connection.Lsn
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.SQLException

@Singleton
class ReplicationSlotManager(
    val config: PostgresSourceConfiguration,
    val connectionFactory: PostgresSourceJdbcConnectionFactory
) {

    private val log = KotlinLogging.logger {}
    private val cdcConfig: CdcIncrementalConfiguration by lazy {
        if (config.incrementalConfiguration !is CdcIncrementalConfiguration) {
            throw IllegalArgumentException(
                "Replication slot management is only applicable to CDC-enabled syncs",
            )
        }
        config.cdc as CdcIncrementalConfiguration
    }
    private val slot = cdcConfig.replicationSlot

    @Synchronized
    fun advanceLsn(lsn: Lsn) {
        log.info { getSlotInfo() }
        val logSequenceNumber = lsn.asLogSequenceNumber()
        val conn = connectionFactory.getReplication()
        val builder =
            conn.replicationAPI
                .replicationStream()
                .logical()
                .withSlotName("\"${cdcConfig.replicationSlot}\"")
                .withSlotOption("proto_version", 1)
                .withSlotOption("publication_names", cdcConfig.publication)
                .apply {
                    val serverVersionStr = conn.parameterStatuses["server_version"]
                    if (serverVersionStr == null) {
                        log.warn { "Unable to determine server version" }
                        return@apply
                    }
                    val serverVersion: Float
                    try {
                        serverVersion = serverVersionStr.toFloat()
                    } catch (e: NumberFormatException) {
                        log.warn(e) { "Unable to parse server version: '$serverVersionStr'" }
                        return@apply
                    }
                    if (serverVersion >= 14.0) {
                        withSlotOption("messages", true)
                    }
                }
                .withStartPosition(logSequenceNumber)
        log.info {
            "Attempting to commit up to $lsn (${lsn.asLong()}) to replication slot ${cdcConfig.replicationSlot}"
        }
        builder.start().use {
            try {
                it.forceUpdateStatus()
                it.setFlushedLSN(logSequenceNumber)
                it.setAppliedLSN(logSequenceNumber)
                it.forceUpdateStatus()
            } catch (e: SQLException) {
                throw TransientErrorException("Failed to commit LSN to replication slot", e)
            }
        }
        log.info {
            "Successfully committed $lsn (${lsn.asLong()}) to replication slot ${cdcConfig.replicationSlot}"
        }
        log.info { getSlotInfo() }
    }

    // ensure that the lsn is available
    fun validate(lsn: Lsn) {
        val slotInfo = getSlotInfo()
        if (slotInfo.restartLsn == null) {
            throw ConfigErrorException(
                "Replication slot '$slot' is not valid: " +
                    "wal_status = '${slotInfo.walStatus}', " +
                    "invalidation_reason = '${slotInfo.invalidationReason}'."
            )
        }
        if (slotInfo.confirmedFlushLsn != null) {
            if (slotInfo.confirmedFlushLsn > lsn) {
                throw ConfigErrorException(
                    "Replication slot '$slot' has advanced beyond the source's state LSN. " +
                        "Confirmed flush LSN: ${slotInfo.confirmedFlushLsn}, source LSN: $lsn."
                )
            }
            log.info {
                "Replication slot '$slot' is valid. " +
                    "Confirmed flush LSN: ${slotInfo.confirmedFlushLsn}, source state LSN: $lsn."
            }
        } else {
            // PG version < 9.6 doesn't have confirmed_flush_lsn: fall back to restart_lsn
            if (slotInfo.restartLsn > lsn) {
                throw ConfigErrorException(
                    "Replication slot '$slot' has advanced beyond the source's state LSN. " +
                        "Restart LSN: ${slotInfo.restartLsn}, source LSN: $lsn."
                )
            }
            log.info {
                "Replication slot '$slot' is valid. " +
                    "Restart LSN: ${slotInfo.restartLsn}, source state LSN: $lsn."
            }
        }
    }

    private data class ReplicationSlotInfo(
        val name: String,
        val xmin: Any?,
        val catalogXmin: Any?,
        val restartLsn: Lsn?,
        val confirmedFlushLsn: Lsn?,
        val walStatus: String?,
        val invalidationReason: String?,
    )

    private fun getSlotInfo(): ReplicationSlotInfo {
        val sql =
            """
            SELECT slot_name, xmin, catalog_xmin, restart_lsn, confirmed_flush_lsn, wal_status,
                invalidation_reason
            FROM pg_replication_slots
            WHERE plugin = 'pgoutput' AND slot_name = ? AND database = ?
        """.trimIndent()
        val slot = cdcConfig.replicationSlot
        return querySingleValue(
            jdbcConnectionFactory = connectionFactory,
            query = sql,
            bindParameters = { stmt ->
                stmt.setString(1, slot)
                stmt.setString(2, config.database)
            },
            withResultSet = { rs ->
                ReplicationSlotInfo(
                    name = rs.getString("slot_name"),
                    xmin = rs.getObject("xmin"),
                    catalogXmin = rs.getObject("catalog_xmin"),
                    restartLsn = rs.getString("restart_lsn")?.let { Lsn.valueOf(it) },
                    confirmedFlushLsn =
                        rs.getString("confirmed_flush_lsn")?.let { Lsn.valueOf(it) },
                    walStatus = rs.getString("wal_status"),
                    invalidationReason = rs.getString("invalidation_reason"),
                )
            },
            noResultsCase = {
                throw ConfigErrorException(
                    "Replication slot '$slot' not found using the query: $sql"
                )
            }
        )
    }
}
