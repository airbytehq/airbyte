/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.Array
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.Struct
import io.airbyte.integrations.base.destination.typing_deduping.Union
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.SQLException
import java.util.*
import org.jooq.SQLDialect

private val log = KotlinLogging.logger {}

class RedshiftDestinationHandler(
    databaseName: String?,
    jdbcDatabase: JdbcDatabase,
    rawNamespace: String
) :
    JdbcDestinationHandler<RedshiftState>(
        databaseName,
        jdbcDatabase,
        rawNamespace,
        SQLDialect.DEFAULT
    ) {
    override fun createNamespaces(schemas: Set<String>) {
        TODO("Not yet implemented")
    }

    @Throws(Exception::class)
    override fun execute(sql: Sql) {
        val transactions = sql.transactions
        val queryId = UUID.randomUUID()
        for (transaction in transactions) {
            val transactionId = UUID.randomUUID()
            log.info(
                "Executing sql {}-{}: {}",
                queryId,
                transactionId,
                java.lang.String.join("\n", transaction)
            )
            val startTime = System.currentTimeMillis()

            try {
                // Original list is immutable, so copying it into a different list.
                val modifiedStatements: MutableList<String> = ArrayList()
                // This is required for Redshift to retrieve Json path query with upper case
                // characters, even after
                // specifying quotes.
                // see https://github.com/airbytehq/airbyte/issues/33900
                modifiedStatements.add("SET enable_case_sensitive_identifier to TRUE;\n")
                modifiedStatements.addAll(transaction)
                jdbcDatabase.executeWithinTransaction(modifiedStatements)
            } catch (e: SQLException) {
                log.error("Sql {}-{} failed", queryId, transactionId, e)
                // This is a big hammer for something that should be much more targetted, only when
                // executing the
                // DROP TABLE command.
                if (
                    e.message!!.contains("ERROR: cannot drop table") &&
                        e.message!!.contains("because other objects depend on it")
                ) {
                    throw ConfigErrorException(
                        "Failed to drop table without the CASCADE option. Consider changing the drop_cascade configuration parameter",
                        e
                    )
                }
                throw e
            }

            log.info(
                "Sql {}-{} completed in {} ms",
                queryId,
                transactionId,
                System.currentTimeMillis() - startTime
            )
        }
    }

    override fun toJdbcTypeName(airbyteType: AirbyteType): String {
        // This is mostly identical to the postgres implementation, but swaps jsonb to super
        if (airbyteType is AirbyteProtocolType) {
            return toJdbcTypeName(airbyteType)
        }
        return when (airbyteType.typeName) {
            Struct.TYPE,
            UnsupportedOneOf.TYPE,
            Array.TYPE -> "super"
            Union.TYPE -> toJdbcTypeName((airbyteType as Union).chooseType())
            else -> throw IllegalArgumentException("Unsupported AirbyteType: $airbyteType")
        }
    }

    override fun toDestinationState(json: JsonNode): RedshiftState {
        return RedshiftState(
            json.hasNonNull("needsSoftReset") && json["needsSoftReset"].asBoolean(),
            json.hasNonNull("isAirbyteMetaPresentInRaw") &&
                json["isAirbyteMetaPresentInRaw"].asBoolean()
        )
    }

    private fun toJdbcTypeName(airbyteProtocolType: AirbyteProtocolType): String {
        return when (airbyteProtocolType) {
            AirbyteProtocolType.STRING -> "varchar"
            AirbyteProtocolType.NUMBER -> "numeric"
            AirbyteProtocolType.INTEGER -> "int8"
            AirbyteProtocolType.BOOLEAN -> "bool"
            AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE -> "timestamptz"
            AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE -> "timestamp"
            AirbyteProtocolType.TIME_WITH_TIMEZONE -> "timetz"
            AirbyteProtocolType.TIME_WITHOUT_TIMEZONE -> "time"
            AirbyteProtocolType.DATE -> "date"
            AirbyteProtocolType.UNKNOWN -> "super"
        }
    }

    // Do not use SVV_TABLE_INFO to get isFinalTableEmpty.
    // See https://github.com/airbytehq/airbyte/issues/34357
}
