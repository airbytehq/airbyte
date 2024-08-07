/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.jdbc.ColumnDefinition
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler.Companion.fromIsNullableIsoString
import io.airbyte.integrations.base.destination.typing_deduping.BaseDestinationV1V2Migrator
import io.airbyte.integrations.base.destination.typing_deduping.CollectionUtils.containsAllIgnoreCase
import io.airbyte.integrations.base.destination.typing_deduping.NamespacedTableName
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.destination.snowflake.SnowflakeDatabaseUtils.fromIsNullableSnowflakeString
import io.airbyte.integrations.destination.snowflake.caching.CacheManager
import java.util.*
import lombok.SneakyThrows

@SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
class SnowflakeV1V2Migrator(
    private val namingConventionTransformer: NamingConventionTransformer,
    private val database: JdbcDatabase,
    private val databaseName: String
) : BaseDestinationV1V2Migrator<TableDefinition>() {
    @SneakyThrows
    @Throws(Exception::class)
    override fun doesAirbyteInternalNamespaceExist(streamConfig: StreamConfig?): Boolean {

//        val useDatabaseQuery = String.format(
//            """
//                USE DATABASE %s;
//            """.trimIndent(),
//            databaseName
//        )
//        database.execute(useDatabaseQuery)

        val showSchemaQuery = String.format(
            """
                SHOW SCHEMAS LIKE '%s' IN DATABASE %s;

            """.trimIndent(),
            streamConfig!!.id.rawNamespace,
            databaseName
        )

        return database.queryJsons(
            showSchemaQuery
        ).isNotEmpty()


//        return database
//            .queryJsons(
//                """
//                SELECT SCHEMA_NAME
//                FROM information_schema.schemata
//                WHERE schema_name = ?
//                AND catalog_name = ?;
//
//                """.trimIndent(),
//                streamConfig!!.id.rawNamespace,
//                databaseName
//            )
//            .isNotEmpty()


//            val testQuery = String.format(
//                """
//                    USE DATABASE %s;
//                    SHOW SCHEMAS LIKE '%s';
//
//                """.trimIndent(),
//                databaseName,
//                namespaces[0],
//            )


//        return CacheManager.queryJsons(database,
//                """
//                SELECT SCHEMA_NAME
//                FROM information_schema.schemata
//                WHERE schema_name = ?
//                AND catalog_name = ?;
//
//                """.trimIndent(),
//                streamConfig!!.id.rawNamespace,
//                databaseName
//            )
//            .isNotEmpty()

/*
        return database.queryJsons(
            String.format(
                """
                    USE DATABASE "%s"; 
                    SHOW SCHEMAS LIKE "%s";
            
                """.trimIndent(),
                databaseName,
                streamConfig!!.id.rawNamespace,
            ),
        ).isNotEmpty()

 */

//        return CacheManager.queryJsons(database,
//                """
//                    USE DATABASE ?;
//                    SHOW SCHEMAS LIKE ?;
//                """.trimIndent(),
//                databaseName,
//                streamConfig!!.id.rawNamespace
//            )
//            .isNotEmpty()

    }

    override fun schemaMatchesExpectation(
        existingTable: TableDefinition,
        columns: Collection<String>
    ): Boolean {
        return containsAllIgnoreCase(existingTable.columns.keys, columns)
    }

    @SneakyThrows
    @Throws(Exception::class)
    override fun getTableIfExists(
        namespace: String?,
        tableName: String?
    ): Optional<TableDefinition> {
        // TODO this looks similar to SnowflakeDestinationHandler#findExistingTables, with a twist;
        // databaseName not upper-cased and rawNamespace and rawTableName as-is (no uppercase).
        // The obvious database.getMetaData().getColumns() solution doesn't work, because JDBC
        // translates
        // VARIANT as VARCHAR


        val showColumnsQuery =
            String.format(

                """
                        SHOW COLUMNS IN TABLE %s.%s.%s;
                                """.trimIndent(),
                databaseName,
                namespace,
                tableName
            )

        val showColumnsResult = database.queryJsons(
            showColumnsQuery)

        println("showColumnsResult=" + showColumnsResult)

        val columns = showColumnsResult
            .stream()
            .collect(
                { LinkedHashMap() },
                { map: java.util.LinkedHashMap<String, ColumnDefinition>, row: JsonNode ->
                    map[row["column_name"].asText()] =
                        ColumnDefinition(
                            row["column_name"].asText(),
                            row["data_type"].asText(),
                            0,
                            fromIsNullableSnowflakeString(row["null?"].asText())
                        )
                },
                {
                    obj: java.util.LinkedHashMap<String, ColumnDefinition>,
                    m: java.util.LinkedHashMap<String, ColumnDefinition>? ->
                    obj.putAll(m!!)
                }
            )

        println("columns=" + columns)

        return if (columns.isEmpty()) {
            Optional.empty()
        } else {
            Optional.of(TableDefinition(columns))
        }


        /*
        val useDatabaseQuery = String.format(
            """
                USE DATABASE %s; 
            """.trimIndent(),
            databaseName
        )
        database.execute(useDatabaseQuery)

        val useSchemaQuery = String.format(
            """
                USE SCHEMA %s; 
            """.trimIndent(),
            namespace!!
        )
        database.execute(useSchemaQuery)

        val showColumnsQuery =
            String.format(

                """
                      
                        -- Show columns in the specified table
                        SHOW COLUMNS IN TABLE %s;

                        -- Process and filter the results
                        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                        FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
                        WHERE TABLE_CATALOG = %s
                          AND TABLE_SCHEMA = %s
                          AND TABLE_NAME = %s
                        ORDER BY ORDINAL_POSITION;

                                """.trimIndent(),

                tableName!!,
                databaseName,
                namespace,
                tableName
            )

        val columns = database.queryJsons(
            showColumnsQuery)
            .stream()
            .collect(
                { LinkedHashMap() },
                { map: java.util.LinkedHashMap<String, ColumnDefinition>, row: JsonNode ->
                    map[row["COLUMN_NAME"].asText()] =
                        ColumnDefinition(
                            row["COLUMN_NAME"].asText(),
                            row["DATA_TYPE"].asText(),
                            0,
                            fromIsNullableIsoString(row["IS_NULLABLE"].asText())
                        )
                },
                {
                    obj: java.util.LinkedHashMap<String, ColumnDefinition>,
                    m: java.util.LinkedHashMap<String, ColumnDefinition>? ->
                    obj.putAll(m!!)
                }
            )


        return if (columns.isEmpty()) {
            Optional.empty()
        } else {
            Optional.of(TableDefinition(columns))
        }

        */


        /*
        val columns =
            database
                .queryJsons(
                    """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_catalog = ?
              AND table_schema = ?
              AND table_name = ?
            ORDER BY ordinal_position;
            
            """.trimIndent(),
                    databaseName,
                    namespace!!,
                    tableName!!
                )
                .stream()
                .collect(
                    { LinkedHashMap() },
                    { map: java.util.LinkedHashMap<String, ColumnDefinition>, row: JsonNode ->
                        map[row["COLUMN_NAME"].asText()] =
                            ColumnDefinition(
                                row["COLUMN_NAME"].asText(),
                                row["DATA_TYPE"].asText(),
                                0,
                                fromIsNullableIsoString(row["IS_NULLABLE"].asText())
                            )
                    },
                    {
                        obj: java.util.LinkedHashMap<String, ColumnDefinition>,
                        m: java.util.LinkedHashMap<String, ColumnDefinition>? ->
                        obj.putAll(m!!)
                    }
                )
        return if (columns.isEmpty()) {
            Optional.empty()
        } else {
            Optional.of(TableDefinition(columns))
        }

         */


        //val columns =
        /*
        database
            .queryJsons(
                """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_catalog = ?
          AND table_schema = ?
          AND table_name = ?
        ORDER BY ordinal_position;

        """.trimIndent(),
                databaseName,
                namespace!!,
                tableName!!
            )

         */

        /*
        val columns = CacheManager.queryJsons(database,
                            """
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_catalog = ?
                          AND table_schema = ?
                          AND table_name = ?
                        ORDER BY ordinal_position;
                        
                        """.trimIndent(),
                            databaseName,
                            namespace!!,
                            tableName!!)
            */

        /*
                val columns = CacheManager.queryJsons(database,
                    """
                        -- Switch to the correct database and schema
                        USE DATABASE ?;
                        USE SCHEMA ?;

                        -- Show columns in the specified table
                        SHOW COLUMNS IN TABLE ?;

                        -- Process and filter the results
                        SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                        FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
                        WHERE TABLE_CATALOG = ?
                          AND TABLE_SCHEMA = ?
                          AND TABLE_NAME = ?
                        ORDER BY ORDINAL_POSITION;

                                """.trimIndent(),
                                databaseName,
                                namespace!!,
                                tableName!!,
                                databaseName,
                                namespace,
                                tableName)
                    */


    }


    override fun convertToV1RawName(streamConfig: StreamConfig): NamespacedTableName {
// The implicit upper-casing happens for this in the SqlGenerator
        @Suppress("deprecation")
        val tableName = namingConventionTransformer.getRawTableName(streamConfig.id.originalName)
        return NamespacedTableName(
            namingConventionTransformer.getIdentifier(streamConfig.id.originalNamespace),
            tableName,
        )
    }

    @Throws(Exception::class)
    override fun doesValidV1RawTableExist(namespace: String?, tableName: String?): Boolean {
// Previously we were not quoting table names and they were being implicitly upper-cased.
// In v2 we preserve cases
        return super.doesValidV1RawTableExist(
            namespace!!.uppercase(Locale.getDefault()),
            tableName!!.uppercase(Locale.getDefault()),
        )
    }
}
