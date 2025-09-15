/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.typing_deduping

import com.amazon.redshift.util.RedshiftException
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
    databaseName: String,
    jdbcDatabase: JdbcDatabase,
    rawNamespace: String
) :
    JdbcDestinationHandler<RedshiftState>(
        databaseName,
        jdbcDatabase,
        rawNamespace,
        SQLDialect.DEFAULT,
        generationHandler = RedshiftGenerationHandler(databaseName)
    ) {
    override fun createNamespaces(schemas: Set<String>) {
        // SHOW SCHEMAS will fail with a "schema ... does not exist" error
        // if any schema is deleted while the SHOW SCHEMAS query runs.
        // Run in a retry loop to mitigate this.
        // This is mostly useful for tests, where we create+drop many schemas.
        // Use up to 10 attempts since this is a fairly basic operation.
        val maxAttempts = 10
        for (i in 1..maxAttempts) {
            try {
                // plain SHOW SCHEMAS doesn't work, we have to specify the database name explicitly
                val existingSchemas =
                    jdbcDatabase.queryJsons("""SHOW SCHEMAS FROM DATABASE "$catalogName";""").map {
                        it["schema_name"].asText()
                    }
                schemas.forEach {
                    if (!existingSchemas.contains(it)) {
                        log.info { "Schema $it does not exist, proceeding to create it" }
                        jdbcDatabase.execute("""CREATE SCHEMA IF NOT EXISTS "$it";""")
                    }
                }
                break
            } catch (e: RedshiftException) {
                if (e.message == null) {
                    // No message, assume this is some different error and fail fast
                    throw e
                }

                // Can't smart cast, so use !! and temp var
                val message: String = e.message!!
                val isConcurrentSchemaDeletionError =
                    message.startsWith("ERROR: schema") && message.endsWith("does not exist")
                if (!isConcurrentSchemaDeletionError) {
                    // The error is not
                    // `ERROR: schema "sql_generator_test_akqywgsxqs" does not exist`
                    // so just fail fast
                    throw e
                }

                // Swallow the exception and go the next loop iteration.
                log.info {
                    "Encountered possibly transient nonexistent schema error during a SHOW SCHEMAS query. Retrying ($i/$maxAttempts attempts)"
                }
            }
        }
    }

    @Throws(Exception::class)
    override fun execute(sql: Sql) {
        execute(sql, logStatements = true)
    }

    /**
     * @param forceCaseSensitiveIdentifier Whether to enable `forceCaseSensitiveIdentifier` on all
     * transactions. This option is most useful for accessing fields within a `SUPER` value; for
     * accessing schemas/tables/columns, quoting the identifier is sufficient to force
     * case-sensitivity, so this option is not necessary.
     */
    fun execute(
        sql: Sql,
        logStatements: Boolean = true,
        forceCaseSensitiveIdentifier: Boolean = true
    ) {
        val transactions = sql.transactions
        val queryId = UUID.randomUUID()
        for (transaction in transactions) {
            val transactionId = UUID.randomUUID()
            if (logStatements) {
                log.info {
                    "Executing sql $queryId-$transactionId: ${transaction.joinToString("\n")}"
                }
            }
            val startTime = System.currentTimeMillis()

            try {
                // Original list is immutable, so copying it into a different list.
                val modifiedStatements: MutableList<String> = ArrayList()
                // This is required for Redshift to retrieve Json path query with upper case
                // characters, even after
                // specifying quotes.
                // see https://github.com/airbytehq/airbyte/issues/33900
                if (forceCaseSensitiveIdentifier) {
                    modifiedStatements.add("SET enable_case_sensitive_identifier to TRUE;\n")
                }
                modifiedStatements.addAll(transaction)
                if (modifiedStatements.size != 1) {
                    jdbcDatabase.executeWithinTransaction(
                        modifiedStatements,
                        logStatements = logStatements
                    )
                } else {
                    // Redshift doesn't allow some statements to run in a transaction at all,
                    // so handle the single-statement case specially.
                    jdbcDatabase.execute(modifiedStatements.first())
                }
            } catch (e: SQLException) {
                log.error(e) { "Sql $queryId-$transactionId failed" }
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

            log.info {
                "Sql $queryId-$transactionId completed in ${System.currentTimeMillis() - startTime} ms"
            }
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
                json["isAirbyteMetaPresentInRaw"].asBoolean(),
            json.hasNonNull("isGenerationIdPresent") && json["isGenerationIdPresent"].asBoolean(),
        )
    }

    fun query(sql: String): List<JsonNode> = jdbcDatabase.queryJsons(sql)

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
