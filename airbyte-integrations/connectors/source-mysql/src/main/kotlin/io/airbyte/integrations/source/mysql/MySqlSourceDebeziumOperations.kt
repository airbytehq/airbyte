/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.FloatNode
import com.fasterxml.jackson.databind.node.NullNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.fasterxml.jackson.databind.node.TextNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.data.DoubleCodec
import io.airbyte.cdk.data.FloatCodec
import io.airbyte.cdk.data.JsonCodec
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.FloatFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.AbortDebeziumWarmStartState
import io.airbyte.cdk.read.cdc.CdcPartitionReaderDebeziumOperations
import io.airbyte.cdk.read.cdc.CdcPartitionsCreatorDebeziumOperations
import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.read.cdc.DebeziumPropertiesBuilder
import io.airbyte.cdk.read.cdc.DebeziumRecordKey
import io.airbyte.cdk.read.cdc.DebeziumRecordValue
import io.airbyte.cdk.read.cdc.DebeziumSchemaHistory
import io.airbyte.cdk.read.cdc.DebeziumWarmStartState
import io.airbyte.cdk.read.cdc.DeserializedRecord
import io.airbyte.cdk.read.cdc.InvalidDebeziumWarmStartState
import io.airbyte.cdk.read.cdc.RelationalColumnCustomConverter
import io.airbyte.cdk.read.cdc.ResetDebeziumWarmStartState
import io.airbyte.cdk.read.cdc.ValidDebeziumWarmStartState
import io.airbyte.cdk.ssh.TunnelSession
import io.airbyte.cdk.util.Jsons
import io.debezium.connector.mysql.MySqlConnector
import io.debezium.connector.mysql.gtid.MySqlGtidSet
import io.debezium.document.DocumentReader
import io.debezium.document.DocumentWriter
import io.debezium.relational.history.HistoryRecord
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.math.BigDecimal
import java.sql.Connection
import java.sql.ResultSet
import java.sql.SQLSyntaxErrorException
import java.sql.Statement
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.util.zip.GZIPInputStream
import java.util.zip.GZIPOutputStream
import kotlin.random.Random
import kotlin.random.nextInt
import org.apache.kafka.connect.json.JsonConverterConfig
import org.apache.kafka.connect.source.SourceRecord
import org.apache.mina.util.Base64

@Singleton
class MySqlSourceDebeziumOperations(
    val jdbcConnectionFactory: JdbcConnectionFactory,
    val configuration: MySqlSourceConfiguration,
    random: Random = Random.Default,
) :
    CdcPartitionsCreatorDebeziumOperations<MySqlSourceCdcPosition>,
    CdcPartitionReaderDebeziumOperations<MySqlSourceCdcPosition> {
    private val log = KotlinLogging.logger {}
    private val cdcIncrementalConfiguration: CdcIncrementalConfiguration by lazy {
        configuration.incrementalConfiguration as CdcIncrementalConfiguration
    }

    @Suppress("UNCHECKED_CAST")
    override fun deserializeRecord(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue,
        stream: Stream,
    ): DeserializedRecord {
        val before: JsonNode = value.before
        val after: JsonNode = value.after
        val source: JsonNode = value.source
        val isDelete: Boolean = after.isNull
        // Use either `before` or `after` as the record data, depending on the nature of the change.
        val data: ObjectNode = (if (isDelete) before else after) as ObjectNode
        // Turn string representations of numbers into BigDecimals.

        val resultRow: NativeRecordPayload = mutableMapOf()
        for (field in stream.schema) {
            when (field.type.airbyteSchemaType) {
                LeafAirbyteSchemaType.INTEGER,
                LeafAirbyteSchemaType.NUMBER -> {
                    val textNode: TextNode? = data[field.id] as? TextNode
                    if (textNode != null) {
                        val bigDecimal = BigDecimal(textNode.textValue()).stripTrailingZeros()
                        data.put(field.id, bigDecimal)
                    }
                }
                LeafAirbyteSchemaType.JSONB -> {
                    val textNode: TextNode? = data[field.id] as? TextNode
                    if (textNode != null) {
                        data.set<JsonNode>(field.id, Jsons.readTree(textNode.textValue()))
                    }
                }
                LeafAirbyteSchemaType.BINARY -> {
                    val textNode: TextNode? = data[field.id] as? TextNode
                    if (textNode != null) {
                        val bytes: ByteArray =
                            Base64.decodeBase64(textNode.textValue().toByteArray())
                        data.set<JsonNode>(field.id, Jsons.binaryNode(bytes))
                    }
                }
                else -> {
                    /* no-op */
                }
            }
            data[field.id] ?: continue
            when (data[field.id]) {
                is NullNode -> {
                    resultRow[field.id] = FieldValueEncoder(null, NullCodec)
                }
                else -> {
                    val codec: JsonCodec<*> =
                        when (field.type) {
                            FloatFieldType ->
                                if (data[field.id] is FloatNode) FloatCodec else DoubleCodec
                            else -> field.type.jsonEncoder as JsonCodec<*>
                        }
                    @Suppress("UNCHECKED_CAST")
                    resultRow[field.id] =
                        FieldValueEncoder(
                            codec.decode(data[field.id]),
                            codec as JsonCodec<Any>,
                        )
                }
            }
        }
        // Set _ab_cdc_updated_at and _ab_cdc_deleted_at meta-field values.
        val transactionMillis: Long = source["ts_ms"].asLong()
        val transactionOffsetDateTime: OffsetDateTime =
            OffsetDateTime.ofInstant(Instant.ofEpochMilli(transactionMillis), ZoneOffset.UTC)
        resultRow[CommonMetaField.CDC_UPDATED_AT.id] =
            FieldValueEncoder(
                transactionOffsetDateTime,
                CommonMetaField.CDC_UPDATED_AT.type.jsonEncoder as JsonEncoder<Any>
            )

        resultRow[CommonMetaField.CDC_DELETED_AT.id] =
            FieldValueEncoder(
                if (isDelete) transactionOffsetDateTime else null,
                (if (isDelete) CommonMetaField.CDC_DELETED_AT.type.jsonEncoder else NullCodec)
                    as JsonEncoder<Any>
            )

        // Set _ab_cdc_log_file and _ab_cdc_log_pos meta-field values.
        val position = MySqlSourceCdcPosition(source["file"].asText(), source["pos"].asLong())

        resultRow[MySqlSourceCdcMetaFields.CDC_LOG_FILE.id] =
            FieldValueEncoder(
                position.fileName,
                MySqlSourceCdcMetaFields.CDC_LOG_FILE.type.jsonEncoder as JsonEncoder<Any>
            )

        resultRow[MySqlSourceCdcMetaFields.CDC_LOG_POS.id] =
            FieldValueEncoder(
                position.position.toDouble(),
                MySqlSourceCdcMetaFields.CDC_LOG_POS.type.jsonEncoder as JsonEncoder<Any>
            )

        // Set the _ab_cdc_cursor meta-field value.
        resultRow[MySqlSourceCdcMetaFields.CDC_CURSOR.id] =
            FieldValueEncoder(
                position.cursorValue,
                MySqlSourceCdcMetaFields.CDC_CURSOR.type.jsonEncoder as JsonEncoder<Any>
            )

        // Return a DeserializedRecord instance.
        return DeserializedRecord(resultRow, emptyMap())
    }

    override fun findStreamNamespace(key: DebeziumRecordKey, value: DebeziumRecordValue): String? =
        value.source["db"]?.asText()

    override fun findStreamName(key: DebeziumRecordKey, value: DebeziumRecordValue): String? =
        value.source["table"]?.asText()

    override fun deserializeState(
        opaqueStateValue: OpaqueStateValue,
    ): DebeziumWarmStartState {
        val debeziumState: UnvalidatedDeserializedState =
            try {
                deserializeStateUnvalidated(opaqueStateValue)
            } catch (e: Exception) {
                log.error(e) { "Error deserializing incumbent state value." }
                return AbortDebeziumWarmStartState(
                    "Error deserializing incumbent state value: ${e.message}"
                )
            }
        return validate(debeziumState)
    }

    /**
     * Checks if GTIDs from previously saved state (debeziumInput) are still valid on DB. And also
     * check if binlog exists or not.
     *
     * Validate is not supposed to perform on synthetic state.
     */
    private fun validate(debeziumState: UnvalidatedDeserializedState): DebeziumWarmStartState {
        val savedStateOffset: SavedOffset = parseSavedOffset(debeziumState)
        val (livePosition: MySqlSourceCdcPosition, gtidSet: String?) = queryPositionAndGtids()
        if (gtidSet.isNullOrEmpty() && !savedStateOffset.gtidSet.isNullOrEmpty()) {
            return abortCdcSync(
                "Connector used GTIDs previously, but MySQL server does not know of any GTIDs or they are not enabled"
            )
        }

        val originalSavedGtidSet = MySqlGtidSet(savedStateOffset.gtidSet)
        val availableGtidSet = MySqlGtidSet(gtidSet)

        // UUID reconciliation for seamless master <-> replica host swap.
        // Master/replica swaps, RDS failover, replica promotions, and operator state edits
        // can introduce UUID divergence between the saved CDC offset and the server's current
        // executed_gtid_set:
        //   - Auto-prune:  drop UUIDSets in saved whose UUID the server doesn't have (e.g. an
        //                  old replica's local-write UUID after swapping to master).
        //   - Auto-inject: add UUIDSets the server has but saved doesn't, at the server's
        //                  current known range (e.g. a new replica's local-write UUID first
        //                  time we sync from it). Trades backfill of those UUIDs for continuity.
        // When reconciliation changes the GTID set AND the saved binlog file isn't on the
        // current host, also reset the offset's file/pos to the oldest available binlog file at
        // pos=0. The CDK's lower/upper-bound cursor comparison uses
        // cursorValue = (fileExtension shl 32) or position; if the new host's binlog naming
        // differs, saved's encoded position can exceed live's and CdcPartitionsCreator would
        // silently declare "already caught up", exiting before Debezium fetches anything. The
        // oldest-file-at-pos-0 sentinel keeps lowerBound below upperBound. Debezium itself
        // resumes via GTID, so file/pos is just a CDK comparison input.
        //
        // If the saved file IS still on the host (same-host state edit, or topology change
        // that preserved binlog naming), leave file/pos alone — they were valid before and
        // resetting them to live would force lowerBound == upperBound and cause the same
        // silent-skip issue.
        val savedGtidSet: MySqlGtidSet =
            if (originalSavedGtidSet.isEmpty) {
                // GTID newly enabled or empty saved state — leave to the downstream binlog-file
                // check (after the purge gap check) to handle resume positioning.
                originalSavedGtidSet
            } else {
                val reconciledGtidString =
                    reconcileSavedGtidSet(originalSavedGtidSet, availableGtidSet)
                val reconciled = MySqlGtidSet(reconciledGtidString)
                if (reconciled != originalSavedGtidSet) {
                    val offsetValue: ObjectNode =
                        debeziumState.offset.wrapped.values.first() as ObjectNode
                    offsetValue.put("gtids", reconciledGtidString)
                    val existingLogFiles: List<String> = getBinaryLogFileNames()
                    val savedFileStillOnHost: Boolean =
                        existingLogFiles.contains(savedStateOffset.position.fileName)
                    if (!savedFileStillOnHost) {
                        val oldestFile: String =
                            existingLogFiles.firstOrNull() ?: livePosition.fileName
                        offsetValue.put("file", oldestFile)
                        offsetValue.put("pos", 0L)
                        log.warn {
                            "Reconciled saved CDC state to absorb a UUID drift event " +
                                "(master<->replica swap, RDS failover, or replica promotion). " +
                                "Original GTIDs=$originalSavedGtidSet, " +
                                "Server GTIDs=$availableGtidSet, " +
                                "Reconciled GTIDs=$reconciled. " +
                                "Saved binlog file ${savedStateOffset.position.fileName} not " +
                                "found on the current host; resetting cursor to oldest " +
                                "available file $oldestFile:0 so the CDK comparison does not " +
                                "short-circuit."
                        }
                    } else {
                        log.warn {
                            "Reconciled saved CDC state to absorb a UUID drift event " +
                                "(same-host state edit or topology change). " +
                                "Original GTIDs=$originalSavedGtidSet, " +
                                "Server GTIDs=$availableGtidSet, " +
                                "Reconciled GTIDs=$reconciled. " +
                                "Saved binlog file ${savedStateOffset.position.fileName} is " +
                                "still on the host; preserving cursor at " +
                                "${savedStateOffset.position.fileName}:" +
                                "${savedStateOffset.position.position} so the CDK partition " +
                                "fetches new events."
                        }
                    }
                }
                reconciled
            }

        if (!savedGtidSet.isContainedWithin(availableGtidSet)) {
            return abortCdcSync(
                "Connector last known GTIDs are $savedGtidSet, but MySQL server only has $availableGtidSet"
            )
        }

        // newGtidSet is gtids from server that hasn't been seen by this connector yet. If the set
        // exists, check that they are not purged, or we may lose those data.
        // Note: MySqlGtidSet.subtract() can throw a NullPointerException when the available
        // GTID set contains server UUIDs not present in the saved GTID set (e.g., after a
        // MySQL failover or topology change on managed MySQL). We catch this and treat it as
        // a CDC state invalidation requiring a sync abort/reset.
        val newGtidSet: MySqlGtidSet =
            try {
                availableGtidSet.subtract(savedGtidSet) as MySqlGtidSet
            } catch (e: NullPointerException) {
                log.warn(e) {
                    "GTID set subtraction failed due to mismatched server UUIDs. " +
                        "Available: $availableGtidSet, Saved: $savedGtidSet"
                }
                return abortCdcSync(
                    "MySQL server GTID set contains server UUIDs not present in saved CDC state. " +
                        "This typically occurs after a MySQL failover or topology change. " +
                        "Available GTIDs: $availableGtidSet, Saved GTIDs: $savedGtidSet"
                )
            }
        if (!newGtidSet.isEmpty) {
            val purgedGtidSet = queryPurgedIds()
            val remainingGtidSet: MySqlGtidSet =
                try {
                    newGtidSet.subtract(purgedGtidSet) as MySqlGtidSet
                } catch (e: NullPointerException) {
                    log.warn(e) {
                        "GTID set subtraction failed during purge check. " +
                            "New: $newGtidSet, Purged: $purgedGtidSet"
                    }
                    return abortCdcSync(
                        "MySQL server GTID set contains server UUIDs not present in saved CDC state. " +
                            "This typically occurs after a MySQL failover or topology change. " +
                            "New GTIDs: $newGtidSet, Purged GTIDs: $purgedGtidSet"
                    )
                }
            if (!purgedGtidSet.isEmpty && !remainingGtidSet.equals(newGtidSet)) {
                return abortCdcSync(
                    "Connector has not seen GTIDs $newGtidSet, but MySQL server has purged $purgedGtidSet"
                )
            }
        }
        // If the connector has saved GTID set, we will use that to validate and skip
        // binlog validation. GTID and binlog works in an independent way to ensure data
        // integrity where GTID is for storing transactions and binlog is for storing changes
        // in DB.
        if (savedGtidSet.isEmpty) {
            val existingLogFiles: List<String> = getBinaryLogFileNames()
            val found = existingLogFiles.contains(savedStateOffset.position.fileName)
            if (!found) {
                return abortCdcSync(
                    "Connector last known binlog file ${savedStateOffset.position.fileName} is not found in the server. Server has $existingLogFiles"
                )
            }
        }

        // Schema-history full rebuild (v7).
        //
        // Background: Airbyte source-mysql runs Debezium with snapshot.mode=recovery and never
        // issues SHOW CREATE TABLE itself. Schema history is built entirely from binlog DDL
        // events visible at sync time, which depends on the current host's binlog retention.
        // Any table whose CREATE TABLE pre-dates retention is permanently absent from history,
        // and the first row event for it crashes Debezium with "schema isn't known to this
        // connector". Master <-> replica swap is hostile to this because each host retains a
        // different binlog window.
        //
        // v6 attempted a coverage-based bootstrap (regex-match existing DDLs to find covered
        // table names, only synthesize CREATE TABLE for missing tables). That failed in
        // practice — the coverage regex either matched some incidental "CREATE TABLE X"
        // substring or the existing DDL for X was present but Debezium's parser silently
        // failed to register the table, leaving Debezium without a schema while v6 thought
        // the table was covered.
        //
        // v7 approach: stop trusting the existing schema history. Replace it entirely with a
        // fresh, complete set of CREATE TABLE statements pulled live via SHOW CREATE TABLE for
        // every table in information_schema for the configured database. Since SHOW CREATE
        // TABLE returns the *current* schema (post all historical ALTERs), this is
        // semantically equivalent to replaying all historical DDLs and ending at the latest
        // state. No information lost. Bounded size (N records, N = current table count).
        //
        // Safety: if information_schema or any SHOW CREATE TABLE call fails, fall back to
        // existing history rather than partial-replace. Worst-case v7 is no worse than v6.
        val rebuiltSchemaHistory: DebeziumSchemaHistory? =
            try {
                rebuildSchemaHistoryFromSource(
                    existing = debeziumState.schemaHistory,
                    referencePosition = savedStateOffset.position,
                )
            } catch (e: Exception) {
                log.warn(e) {
                    "Schema history rebuild failed; proceeding with existing history. " +
                        "${e.message}"
                }
                debeziumState.schemaHistory
            }
        return ValidDebeziumWarmStartState(debeziumState.offset, rebuiltSchemaHistory)
    }

    private val createTableHeadPattern: Regex =
        Regex("""CREATE\s+TABLE\s+(?!IF\s+NOT\s+EXISTS)""", RegexOption.IGNORE_CASE)

    private fun rebuildSchemaHistoryFromSource(
        existing: DebeziumSchemaHistory?,
        referencePosition: MySqlSourceCdcPosition,
    ): DebeziumSchemaHistory? {
        val existingSize: Int = existing?.wrapped?.size ?: 0

        val allTables: List<String> =
            try {
                queryAllTablesInDatabase()
            } catch (e: Exception) {
                log.warn(e) {
                    "v7 schema-history rebuild: could not query information_schema.tables for " +
                        "database '$databaseName'; falling back to existing history " +
                        "($existingSize record(s)). ${e.message}"
                }
                return existing
            }

        if (allTables.isEmpty()) {
            log.warn {
                "v7 schema-history rebuild: information_schema reported zero BASE TABLE rows " +
                    "for database '$databaseName'; falling back to existing history " +
                    "($existingSize record(s))."
            }
            return existing
        }

        log.warn {
            "v7 schema-history rebuild: information_schema reports ${allTables.size} table(s) " +
                "in '$databaseName'. Fetching SHOW CREATE TABLE for each to build a fresh " +
                "schema history (existing had $existingSize record(s)). Tables: $allTables"
        }

        val topicPrefix: String = DebeziumPropertiesBuilder.sanitizeTopicPrefix(databaseName)
        val now: Instant = Instant.now()
        val tsSec: Long = now.epochSecond
        val tsMs: Long = now.toEpochMilli()

        val freshRecords: MutableList<HistoryRecord> = mutableListOf()
        val failedTables: MutableList<String> = mutableListOf()

        for (table in allTables) {
            try {
                val ddl: String? = queryCreateTableDdl(table)
                if (ddl == null) {
                    failedTables.add(table)
                    log.warn {
                        "v7 schema-history rebuild: SHOW CREATE TABLE returned no rows for " +
                            "$databaseName.$table — unusual; will fall back to existing history."
                    }
                } else {
                    freshRecords.add(
                        buildBootstrapHistoryRecord(
                            topicPrefix = topicPrefix,
                            position = referencePosition,
                            tsSec = tsSec,
                            tsMs = tsMs,
                            tableName = table,
                            ddl = ddl,
                        )
                    )
                }
            } catch (e: Exception) {
                failedTables.add(table)
                log.warn(e) {
                    "v7 schema-history rebuild: SHOW CREATE TABLE failed for " +
                        "$databaseName.$table. ${e.message}"
                }
            }
        }

        if (failedTables.isNotEmpty()) {
            log.warn {
                "v7 schema-history rebuild: ${failedTables.size} table(s) failed to fetch DDL " +
                    "($failedTables); NOT replacing existing schema history to avoid losing " +
                    "schemas. Falling back to existing history ($existingSize record(s))."
            }
            return existing
        }

        log.warn {
            "v7 schema-history rebuild: successfully built ${freshRecords.size} fresh CREATE " +
                "TABLE record(s) for all tables. Replacing existing schema history " +
                "($existingSize record(s) -> ${freshRecords.size} record(s))."
        }

        return DebeziumSchemaHistory(freshRecords.toList())
    }

    private fun queryAllTablesInDatabase(): List<String> =
        jdbcConnectionFactory.get().use { connection: Connection ->
            val sql =
                "SELECT TABLE_NAME FROM information_schema.tables " +
                    "WHERE TABLE_SCHEMA = ? AND TABLE_TYPE = 'BASE TABLE'"
            connection.prepareStatement(sql).use { stmt ->
                stmt.setString(1, databaseName)
                stmt.executeQuery().use { rs: ResultSet ->
                    generateSequence { if (rs.next()) rs.getString(1) else null }.toList()
                }
            }
        }

    private fun queryCreateTableDdl(tableName: String): String? =
        jdbcConnectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { stmt: Statement ->
                val safeDb: String = databaseName.replace("`", "``")
                val safeTable: String = tableName.replace("`", "``")
                stmt.executeQuery("SHOW CREATE TABLE `$safeDb`.`$safeTable`").use {
                    rs: ResultSet ->
                    if (rs.next()) rs.getString(2) else null
                }
            }
        }

    private fun buildBootstrapHistoryRecord(
        topicPrefix: String,
        position: MySqlSourceCdcPosition,
        tsSec: Long,
        tsMs: Long,
        tableName: String,
        ddl: String,
    ): HistoryRecord {
        // Defensive: rewrite the bootstrap DDL to use CREATE TABLE IF NOT EXISTS so that, if our
        // coverage check missed an alias or rename and the table is in fact already known to
        // Debezium, the DDL parser treats it as a no-op rather than erroring on duplicate CREATE.
        val safeDdl: String =
            createTableHeadPattern.replaceFirst(ddl, "CREATE TABLE IF NOT EXISTS ")

        val sourceNode: ObjectNode =
            Jsons.objectNode().apply { put("server", topicPrefix) }
        val positionNode: ObjectNode =
            Jsons.objectNode().apply {
                put("ts_sec", tsSec)
                put("file", position.fileName)
                put("pos", position.position)
                put("snapshot", true)
            }
        val recordJson: ObjectNode =
            Jsons.objectNode().apply {
                set<JsonNode>("source", sourceNode)
                set<JsonNode>("position", positionNode)
                put("ts_ms", tsMs)
                put("databaseName", databaseName)
                put("ddl", safeDdl)
                set<JsonNode>("tableChanges", Jsons.arrayNode())
            }
        // Round-trip through Debezium's Document parser. Matches how existing schema history
        // records are constructed during deserialization (see deserializeStateUnvalidated).
        val document = DocumentReader.defaultReader().read(recordJson.toString())
        // tableName parameter is unused at runtime but is kept for log clarity in callers and
        // for documentation; databaseName is already in the record.
        require(tableName.isNotEmpty()) { "bootstrap table name must not be empty" }
        return HistoryRecord(document)
    }

    private fun abortCdcSync(reason: String): InvalidDebeziumWarmStartState =
        when (cdcIncrementalConfiguration.invalidCdcCursorPositionBehavior) {
            InvalidCdcCursorPositionBehavior.FAIL_SYNC ->
                AbortDebeziumWarmStartState(
                    "Saved offset no longer present on the server, please reset the connection, " +
                        "and then increase binlog retention and/or increase sync frequency. " +
                        "$reason."
                )
            InvalidCdcCursorPositionBehavior.RESET_SYNC ->
                ResetDebeziumWarmStartState(
                    "Saved offset no longer present on the server. $reason."
                )
        }

    private fun parseSavedOffset(debeziumState: UnvalidatedDeserializedState): SavedOffset {
        val position: MySqlSourceCdcPosition = position(debeziumState.offset)
        val gtidSet: String? = debeziumState.offset.wrapped.values.first()["gtids"]?.asText()
        return SavedOffset(position, gtidSet)
    }

    data class SavedOffset(val position: MySqlSourceCdcPosition, val gtidSet: String?)

    enum class CdcStateValidateResult {
        VALID,
        INVALID_ABORT,
        INVALID_RESET
    }

    override fun position(offset: DebeziumOffset): MySqlSourceCdcPosition =
        Companion.position(offset)

    override fun position(recordValue: DebeziumRecordValue): MySqlSourceCdcPosition? {
        val file: JsonNode = recordValue.source["file"]?.takeIf { it.isTextual } ?: return null
        val pos: JsonNode = recordValue.source["pos"]?.takeIf { it.isIntegralNumber } ?: return null
        return MySqlSourceCdcPosition(file.asText(), pos.asLong())
    }

    override fun position(sourceRecord: SourceRecord): MySqlSourceCdcPosition? {
        val offset: Map<String, *> = sourceRecord.sourceOffset()
        val file: Any = offset["file"] ?: return null
        val pos: Long = offset["pos"] as? Long ?: return null
        return MySqlSourceCdcPosition(file.toString(), pos)
    }

    override fun generateColdStartOffset(): DebeziumOffset {
        val (mySqlSourceCdcPosition: MySqlSourceCdcPosition, gtidSet: String?) =
            queryPositionAndGtids()
        val topicPrefixName: String = DebeziumPropertiesBuilder.sanitizeTopicPrefix(databaseName)
        val timestamp: Instant = Instant.now()
        val key: ArrayNode =
            Jsons.arrayNode().apply {
                add(databaseName)
                add(Jsons.objectNode().apply { put("server", topicPrefixName) })
            }
        val value: ObjectNode =
            Jsons.objectNode().apply {
                put("ts_sec", timestamp.epochSecond)
                put("file", mySqlSourceCdcPosition.fileName)
                put("pos", mySqlSourceCdcPosition.position)
                if (gtidSet != null) {
                    put("gtids", gtidSet)
                }
            }
        val offset = DebeziumOffset(mapOf(key to value))
        log.info { "Constructed synthetic $offset." }
        return offset
    }

    private fun queryPositionAndGtids(): Pair<MySqlSourceCdcPosition, String?> {
        jdbcConnectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { stmt: Statement ->
                try {
                    // Syntax for MySQL version < 8.4
                    return parseBinaryLogStatus(stmt, "SHOW MASTER STATUS")
                } catch (_: SQLSyntaxErrorException) {
                    // Syntax for MySQL version >= 8.4
                    return parseBinaryLogStatus(stmt, "SHOW BINARY LOG STATUS")
                }
            }
        }
    }

    private fun parseBinaryLogStatus(
        stmt: Statement,
        query: String
    ): Pair<MySqlSourceCdcPosition, String?> {
        stmt.executeQuery(query).use { rs: ResultSet ->
            if (!rs.next()) throw ConfigErrorException("No results for query: {{$query}}")
            val file = Field("File", StringFieldType)
            val pos = Field("Position", LongFieldType)
            val gtids = Field("Executed_Gtid_Set", StringFieldType)
            val mySqlSourceCdcPosition =
                MySqlSourceCdcPosition(
                    fileName = rs.getString(file.id)?.takeUnless { rs.wasNull() }
                            ?: throw ConfigErrorException(
                                "No value for ${file.id} in: {{$query}}",
                            ),
                    position = rs.getLong(pos.id).takeUnless { rs.wasNull() || it <= 0 }
                            ?: throw ConfigErrorException(
                                "No value for ${pos.id} in: {{$query}}",
                            ),
                )
            if (rs.metaData.columnCount <= 4) {
                // This value exists only in MySQL 5.6.5 or later.
                return mySqlSourceCdcPosition to null
            }
            val gtidSet: String? =
                rs.getString(gtids.id)
                    ?.takeUnless { rs.wasNull() || it.isBlank() }
                    ?.trim()
                    ?.replace("\n", "")
                    ?.replace("\r", "")
            return mySqlSourceCdcPosition to gtidSet
        }
    }

    private fun queryPurgedIds(): MySqlGtidSet {
        val purgedGtidField = Field("@@global.gtid_purged", StringFieldType)
        jdbcConnectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { stmt: Statement ->
                val sql = "SELECT @@global.gtid_purged"
                stmt.executeQuery(sql).use { rs: ResultSet ->
                    if (!rs.next()) throw ConfigErrorException("No results for query: $sql")
                    return MySqlGtidSet(rs.getString(purgedGtidField.id))
                }
            }
        }
    }

    private fun getBinaryLogFileNames(): List<String> {
        // Very old MySQL version (4.x) has different output of SHOW BINARY LOGS output.
        return jdbcConnectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { stmt: Statement ->
                val sql = "SHOW BINARY LOGS"
                stmt.executeQuery(sql).use { rs: ResultSet ->
                    generateSequence { if (rs.next()) rs.getString(1) else null }.toList()
                }
            }
        }
    }

    override fun generateColdStartProperties(streams: List<Stream>): Map<String, String> =
        DebeziumPropertiesBuilder()
            .with(commonProperties)
            // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-snapshot-mode
            // We use the recovery property cause using this mode will instruct Debezium to
            // construct the db schema history. Note that we used to use schema_only_recovery mode
            // instead, but this mode has been deprecated.
            .with("snapshot.mode", "recovery")
            .buildMap()

    override fun generateWarmStartProperties(streams: List<Stream>): Map<String, String> =
        DebeziumPropertiesBuilder().with(commonProperties).withStreams(streams).buildMap()

    override fun serializeState(
        offset: DebeziumOffset,
        schemaHistory: DebeziumSchemaHistory?
    ): OpaqueStateValue {
        val stateNode: ObjectNode = Jsons.objectNode()
        // Serialize offset.
        val offsetNode: JsonNode =
            Jsons.objectNode().apply {
                for ((k, v) in offset.wrapped) {
                    put(Jsons.writeValueAsString(k), Jsons.writeValueAsString(v))
                }
            }
        stateNode.set<JsonNode>(MYSQL_CDC_OFFSET, offsetNode)
        // Serialize schema history.
        if (schemaHistory != null) {
            val uncompressedString: String =
                schemaHistory.wrapped.joinToString(separator = "\n") {
                    DocumentWriter.defaultWriter().write(it.document())
                }
            if (uncompressedString.length <= MAX_UNCOMPRESSED_LENGTH) {
                stateNode.put(MYSQL_DB_HISTORY, uncompressedString)
            } else {
                stateNode.put(IS_COMPRESSED, true)
                val baos = ByteArrayOutputStream()
                val builder = StringBuilder()
                GZIPOutputStream(baos).writer(Charsets.UTF_8).use { it.write(uncompressedString) }

                builder.append("\"")
                builder.append(Base64.encodeBase64(baos.toByteArray()).toString(Charsets.UTF_8))
                builder.append("\"")

                stateNode.put(MYSQL_DB_HISTORY, builder.toString())
            }
        }
        return Jsons.objectNode().apply { set<JsonNode>(STATE, stateNode) }
    }

    val databaseName: String = configuration.namespaces.first()
    val serverID: Int = random.nextInt(MIN_SERVER_ID..MAX_SERVER_ID)

    val commonProperties: Map<String, String> by lazy {
        val tunnelSession: TunnelSession = jdbcConnectionFactory.ensureTunnelSession()
        val dbzPropertiesBuilder =
            DebeziumPropertiesBuilder()
                .withDefault()
                .withConnector(MySqlConnector::class.java)
                .withDebeziumName(databaseName)
                .withHeartbeats(configuration.debeziumHeartbeatInterval) // TEMP
                // This to make sure that binary data represented as a base64-encoded String.
                // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-binary-handling-mode
                .with("binary.handling.mode", "base64")
                // This is to make sure that numbers are represented as strings.
                .with("decimal.handling.mode", "string")
                // This is to make sure that temporal data is represented without loss of precision.
                .with("time.precision.mode", "adaptive_time_microseconds")
                // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-snapshot-mode
                .with("snapshot.mode", "when_needed")
                // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-snapshot-locking-mode
                // This is to make sure other database clients are allowed to write to a table while
                // Airbyte is taking a snapshot. There is a risk involved that if any database
                // client
                // makes a schema change then the sync might break
                .with("snapshot.locking.mode", "none")
                // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-include-schema-changes
                .with("include.schema.changes", "false")
                .with(
                    "connect.keep.alive.interval.ms",
                    configuration.debeziumKeepAliveInterval.toMillis().toString(),
                )
                .withDatabase(configuration.jdbcProperties)
                .withDatabase("hostname", tunnelSession.address.hostName)
                .withDatabase("port", tunnelSession.address.port.toString())
                .withDatabase("dbname", databaseName)
                .withDatabase("server.id", serverID.toString())
                .withDatabase("include.list", databaseName)
                .withOffset()
                .withSchemaHistory()
                .run {
                    val converters =
                        buildList<Class<out RelationalColumnCustomConverter>> {
                            if (!configuration.treatTinyint1AsInteger) {
                                add(MySqlSourceCdcBooleanConverter::class.java)
                            }
                            add(MySqlSourceCdcTemporalConverter::class.java)
                        }
                    withConverters(*converters.toTypedArray())
                }

        cdcIncrementalConfiguration.serverTimezone
            ?.takeUnless { it.isBlank() }
            ?.let { dbzPropertiesBuilder.withDatabase("connectionTimezone", it) }

        dbzPropertiesBuilder.buildMap()
    }

    companion object {
        // Constants defining a range for the random value picked for the database.server.id
        // Debezium property which uniquely identifies the binlog consumer.
        // https://debezium.io/documentation/reference/stable/connectors/mysql.html#mysql-property-database-server-id
        const val MIN_SERVER_ID = 5400
        const val MAX_SERVER_ID = 6400

        const val MAX_UNCOMPRESSED_LENGTH = 1024 * 1024
        const val STATE = "state"
        const val MYSQL_CDC_OFFSET = "mysql_cdc_offset"
        const val MYSQL_DB_HISTORY = "mysql_db_history"
        const val IS_COMPRESSED = "is_compressed"

        /**
         * The name of the Debezium property that contains the unique name for the Debezium
         * connector.
         */
        const val CONNECTOR_NAME_PROPERTY: String = "name"

        /** Configuration for offset state key/value converters. */
        val INTERNAL_CONVERTER_CONFIG: Map<String, String> =
            java.util.Map.of(JsonConverterConfig.SCHEMAS_ENABLE_CONFIG, false.toString())

        internal fun deserializeStateUnvalidated(
            opaqueStateValue: OpaqueStateValue
        ): UnvalidatedDeserializedState {
            val stateNode: ObjectNode = opaqueStateValue[STATE] as ObjectNode
            // Deserialize offset.
            val offsetNode: ObjectNode = stateNode[MYSQL_CDC_OFFSET] as ObjectNode
            val offsetMap: Map<JsonNode, JsonNode> =
                offsetNode
                    .fields()
                    .asSequence()
                    .map { (k, v) -> Jsons.readTree(k) to Jsons.readTree(v.textValue()) }
                    .toMap()
            if (offsetMap.size != 1) {
                throw RuntimeException("Offset object should have 1 key in $opaqueStateValue")
            }
            val offset = DebeziumOffset(offsetMap)
            // Deserialize schema history.
            val schemaNode: JsonNode =
                stateNode[MYSQL_DB_HISTORY] ?: return UnvalidatedDeserializedState(offset)
            val isCompressed: Boolean = stateNode[IS_COMPRESSED]?.asBoolean() ?: false
            val uncompressedString: String =
                if (isCompressed) {
                    val textValue: String = schemaNode.textValue()
                    val compressedBytes: ByteArray =
                        textValue.substring(1, textValue.length - 1).toByteArray(Charsets.UTF_8)
                    val decoded = Base64.decodeBase64(compressedBytes)
                    GZIPInputStream(ByteArrayInputStream(decoded)).reader(Charsets.UTF_8).readText()
                } else {
                    schemaNode.textValue()
                }
            val schemaHistoryList: List<HistoryRecord> =
                uncompressedString
                    .lines()
                    .filter { it.isNotBlank() }
                    .map { HistoryRecord(DocumentReader.defaultReader().read(it)) }
            return UnvalidatedDeserializedState(offset, DebeziumSchemaHistory(schemaHistoryList))
        }

        data class UnvalidatedDeserializedState(
            val offset: DebeziumOffset,
            val schemaHistory: DebeziumSchemaHistory? = null,
        )

        internal fun position(offset: DebeziumOffset): MySqlSourceCdcPosition {
            if (offset.wrapped.size != 1) {
                throw ConfigErrorException("Expected exactly 1 key in $offset")
            }
            val offsetValue: ObjectNode = offset.wrapped.values.first() as ObjectNode
            return MySqlSourceCdcPosition(offsetValue["file"].asText(), offsetValue["pos"].asLong())
        }

        /**
         * Reconcile a saved GTID set against the live server's executed GTID set.
         *
         * Returns a GTID string built from:
         *   - UUIDSets from `saved` whose UUID is also present on the server (kept verbatim).
         *   - UUIDSets from `available` whose UUID is absent from `saved` (auto-inject at the
         *     server's current known range; chooses continuity over backfill of those UUIDs).
         *
         * UUIDSets in `saved` whose UUID is absent from `available` are dropped (auto-prune).
         *
         * Iteration is intentionally over `getUUIDSets()` rather than `.toString()` parsing so
         * multi-interval UUIDSets (e.g. `uuid:1-10:20-30`) round-trip without re-merging gaps.
         */
        internal fun reconcileSavedGtidSet(
            saved: MySqlGtidSet,
            available: MySqlGtidSet,
        ): String {
            val availableUuids: Set<String> =
                available.uuidSets.asSequence().map { it.uuid }.toSet()
            val savedUuids: Set<String> =
                saved.uuidSets.asSequence().map { it.uuid }.toSet()
            val parts: MutableList<String> = mutableListOf()
            saved.uuidSets
                .asSequence()
                .filter { it.uuid in availableUuids }
                .forEach { parts.add(it.toString()) }
            available.uuidSets
                .asSequence()
                .filter { it.uuid !in savedUuids }
                .forEach { parts.add(it.toString()) }
            return parts.joinToString(",")
        }
    }
}
