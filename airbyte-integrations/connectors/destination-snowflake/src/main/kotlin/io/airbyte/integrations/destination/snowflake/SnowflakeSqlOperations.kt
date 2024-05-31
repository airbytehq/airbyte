/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.DestinationConfig.Companion.instance
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperationsUtils.insertRawRecordsInSingleQuery
import io.airbyte.commons.exceptions.ConfigErrorException
import java.sql.SQLException
import java.util.*
import java.util.function.Consumer
import net.snowflake.client.jdbc.SnowflakeSQLException
import org.slf4j.Logger
import org.slf4j.LoggerFactory

open class SnowflakeSqlOperations {
    protected val schemaSet: MutableSet<String> = HashSet()

    @Throws(Exception::class)
    fun createSchemaIfNotExists(database: JdbcDatabase?, schemaName: String) {
        try {
            if (!schemaSet.contains(schemaName) && !isSchemaExists(database, schemaName)) {
                // 1s1t is assuming a lowercase airbyte_internal schema name, so we need to quote it
                database!!.execute(String.format("CREATE SCHEMA IF NOT EXISTS \"%s\";", schemaName))
                schemaSet.add(schemaName)
            }
        } catch (e: Exception) {
            throw checkForKnownConfigExceptions(e).orElseThrow { e }
        }
    }

    fun createTableQuery(schemaName: String?, tableName: String?): String? {
        val retentionPeriodDays = retentionPeriodDaysFromConfigSingleton
        return String.format(
            """
        CREATE TABLE IF NOT EXISTS "%s"."%s" (
          "%s" VARCHAR PRIMARY KEY,
          "%s" TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp(),
          "%s" TIMESTAMP WITH TIME ZONE DEFAULT NULL,
          "%s" VARIANT
        ) data_retention_time_in_days = %d;
        """.trimIndent(),
            schemaName,
            tableName,
            JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
            JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
            JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
            JavaBaseConstants.COLUMN_NAME_DATA,
            retentionPeriodDays
        )
    }

    @Throws(Exception::class)
    fun isSchemaExists(database: JdbcDatabase?, schemaName: String?): Boolean {
        try {
            database!!.unsafeQuery(JdbcSqlOperations.SHOW_SCHEMAS).use { results ->
                return results
                    .map { schemas: JsonNode -> schemas[JdbcSqlOperations.NAME].asText() }
                    .anyMatch { anObject: String? -> schemaName.equals(anObject) }
            }
        } catch (e: Exception) {
            throw checkForKnownConfigExceptions(e).orElseThrow { e }
        }
    }

    @Throws(SQLException::class)
    public fun insertRecordsInternal(
        database: JdbcDatabase,
        records: List<PartialAirbyteMessage>,
        schemaName: String?,
        tableName: String?
    ) {
        LOGGER.info("actual size of batch: {}", records.size)
        // Note that the column order is weird here - that's intentional, to avoid needing to change
        // SqlOperationsUtils.insertRawRecordsInSingleQuery to support a different column order.

        // snowflake query syntax:
        // requires selecting from a set of values in order to invoke the parse_json function.
        // INSERT INTO public.users (ab_id, data, emitted_at) SELECT column1, parse_json(column2),
        // column3
        // FROM VALUES
        // (?, ?, ?),
        // ...
        val insertQuery =
            String.format(
                "INSERT INTO \"%s\".\"%s\" (\"%s\", \"%s\", \"%s\") SELECT column1, parse_json(column2), column3 FROM VALUES\n",
                schemaName,
                tableName,
                JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
                JavaBaseConstants.COLUMN_NAME_DATA,
                JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT
            )
        val recordQuery = "(?, ?, ?),\n"
        insertRawRecordsInSingleQuery(insertQuery, recordQuery, database, records)
    }

    protected fun generateFilesList(files: List<String>): String {
        if (0 < files.size && files.size < MAX_FILES_IN_LOADING_QUERY_LIMIT) {
            // see
            // https://docs.snowflake.com/en/user-guide/data-load-considerations-load.html#lists-of-files
            val joiner = StringJoiner(",")
            files.forEach(
                Consumer { filename: String ->
                    joiner.add("'" + filename.substring(filename.lastIndexOf("/") + 1) + "'")
                }
            )
            return " files = ($joiner)"
        } else {
            return ""
        }
    }

    fun checkForKnownConfigExceptions(e: Exception?): Optional<ConfigErrorException> {
        if (e is SnowflakeSQLException && e.message!!.contains(NO_PRIVILEGES_ERROR_MESSAGE)) {
            return Optional.of(
                ConfigErrorException(
                    "Encountered Error with Snowflake Configuration: Current role does not have permissions on the target schema please verify your privileges",
                    e
                )
            )
        }
        if (e is SnowflakeSQLException && e.message!!.contains(IP_NOT_IN_WHITE_LIST_ERR_MSG)) {
            return Optional.of(
                ConfigErrorException(
                    """
              Snowflake has blocked access from Airbyte IP address. Please make sure that your Snowflake user account's
               network policy allows access from all Airbyte IP addresses. See this page for the list of Airbyte IPs:
               https://docs.airbyte.com/cloud/getting-started-with-airbyte-cloud#allowlist-ip-addresses and this page
               for documentation on Snowflake network policies: https://docs.snowflake.com/en/user-guide/network-policies
          
          """.trimIndent(),
                    e
                )
            )
        }
        return Optional.empty()
    }

    companion object {
        const val RETENTION_PERIOD_DAYS_CONFIG_KEY: String = "retention_period_days"

        private val LOGGER: Logger = LoggerFactory.getLogger(SnowflakeSqlOperations::class.java)
        private const val MAX_FILES_IN_LOADING_QUERY_LIMIT = 1000

        // This is an unfortunately fragile way to capture this, but Snowflake doesn't
        // provide a more specific permission exception error code
        private const val NO_PRIVILEGES_ERROR_MESSAGE = "but current role has no privileges on it"
        private const val IP_NOT_IN_WHITE_LIST_ERR_MSG = "not allowed to access Snowflake"

        private val retentionPeriodDaysFromConfigSingleton: Int
            /**
             * Sort of hacky. The problem is that SnowflakeSqlOperations is constructed in the
             * SnowflakeDestination constructor, but we don't have the JsonNode config until we try
             * to call check/getSerializedConsumer on the SnowflakeDestination. So we can't actually
             * inject the config normally. Instead, we just use the singleton object. :(
             */
            get() =
                getRetentionPeriodDays(instance!!.getNodeValue(RETENTION_PERIOD_DAYS_CONFIG_KEY))

        fun getRetentionPeriodDays(node: JsonNode?): Int {
            val retentionPeriodDays =
                if (node == null || node.isNull) {
                    1
                } else {
                    node.asInt()
                }
            return retentionPeriodDays
        }
    }
}
