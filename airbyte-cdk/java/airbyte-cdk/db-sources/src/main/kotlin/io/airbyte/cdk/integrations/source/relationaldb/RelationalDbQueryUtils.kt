/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.SqlDatabase
import io.airbyte.commons.stream.AirbyteStreamUtils
import io.airbyte.commons.util.AutoCloseableIterator
import io.airbyte.commons.util.AutoCloseableIterators
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import java.util.*
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/** Utility class for methods to query a relational db. */
object RelationalDbQueryUtils {
    private val LOGGER: Logger = LoggerFactory.getLogger(RelationalDbQueryUtils::class.java)

    @JvmStatic
    fun getIdentifierWithQuoting(identifier: String, quoteString: String): String {
        // double-quoted values within a database name or column name should be wrapped with extra
        // quoteString
        return if (identifier.startsWith(quoteString) && identifier.endsWith(quoteString)) {
            quoteString + quoteString + identifier + quoteString + quoteString
        } else {
            quoteString + identifier + quoteString
        }
    }

    @JvmStatic
    fun enquoteIdentifierList(identifiers: List<String>, quoteString: String): String {
        val joiner = StringJoiner(",")
        for (identifier in identifiers) {
            joiner.add(getIdentifierWithQuoting(identifier, quoteString))
        }
        return joiner.toString()
    }

    /** @return fully qualified table name with the schema (if a schema exists) in quotes. */
    @JvmStatic
    fun getFullyQualifiedTableNameWithQuoting(
        nameSpace: String?,
        tableName: String,
        quoteString: String
    ): String {
        return (if (nameSpace == null || nameSpace.isEmpty())
            getIdentifierWithQuoting(tableName, quoteString)
        else
            getIdentifierWithQuoting(nameSpace, quoteString) +
                "." +
                getIdentifierWithQuoting(tableName, quoteString))
    }

    /** @return fully qualified table name with the schema (if a schema exists) without quotes. */
    @JvmStatic
    fun getFullyQualifiedTableName(schemaName: String?, tableName: String): String {
        return if (schemaName != null) "$schemaName.$tableName" else tableName
    }

    /** @return the input identifier with quotes. */
    @JvmStatic
    fun enquoteIdentifier(identifier: String?, quoteString: String?): String {
        return quoteString + identifier + quoteString
    }

    @JvmStatic
    fun <Database : SqlDatabase?> queryTable(
        database: Database,
        sqlQuery: String?,
        tableName: String?,
        schemaName: String?
    ): AutoCloseableIterator<JsonNode> {
        val airbyteStreamNameNamespacePair =
            AirbyteStreamUtils.convertFromNameAndNamespace(tableName, schemaName)
        return AutoCloseableIterators.lazyIterator(
            {
                try {
                    LOGGER.info("Queueing query: {}", sqlQuery)
                    val stream = database!!.unsafeQuery(sqlQuery)
                    return@lazyIterator AutoCloseableIterators.fromStream<JsonNode>(
                        stream,
                        airbyteStreamNameNamespacePair
                    )
                } catch (e: Exception) {
                    throw RuntimeException(e)
                }
            },
            airbyteStreamNameNamespacePair
        )
    }

    @JvmStatic
    fun logStreamSyncStatus(streams: List<ConfiguredAirbyteStream>, syncType: String?) {
        if (streams.isEmpty()) {
            LOGGER.info("No Streams will be synced via {}.", syncType)
        } else {
            LOGGER.info("Streams to be synced via {} : {}", syncType, streams.size)
            LOGGER.info("Streams: {}", prettyPrintConfiguredAirbyteStreamList(streams))
        }
    }

    fun prettyPrintConfiguredAirbyteStreamList(streamList: List<ConfiguredAirbyteStream>): String {
        return streamList.joinToString(", ") { s: ConfiguredAirbyteStream ->
            "${s.stream.namespace}.${s.stream.name}"
        }
    }

    class TableSizeInfo(tableSize: Long, avgRowLength: Long) {
        val tableSize: Long
        val avgRowLength: Long

        init {
            this.tableSize = tableSize
            this.avgRowLength = avgRowLength
        }
    }
}
