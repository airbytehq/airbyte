/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.jdbc

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.annotations.VisibleForTesting
import com.google.common.collect.ImmutableList
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Sets
import datadog.trace.api.Trace
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.JdbcCompatibleSourceOperations
import io.airbyte.cdk.db.SqlDatabase
import io.airbyte.cdk.db.factory.DataSourceFactory.close
import io.airbyte.cdk.db.factory.DataSourceFactory.create
import io.airbyte.cdk.db.jdbc.AirbyteRecordData
import io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_NAME
import io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_SIZE
import io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE
import io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE_NAME
import io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_DECIMAL_DIGITS
import io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_IS_NULLABLE
import io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_SCHEMA_NAME
import io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_TABLE_NAME
import io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_COLUMN_NAME
import io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_DATABASE_NAME
import io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_DATA_TYPE
import io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_SCHEMA_NAME
import io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_SIZE
import io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_TABLE_NAME
import io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_TYPE_NAME
import io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_DECIMAL_DIGITS
import io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_IS_NULLABLE
import io.airbyte.cdk.db.jdbc.JdbcConstants.KEY_SEQ
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.db.jdbc.JdbcUtils.getFullyQualifiedTableName
import io.airbyte.cdk.db.jdbc.StreamingJdbcDatabase
import io.airbyte.cdk.db.jdbc.streaming.JdbcStreamingQueryConfig
import io.airbyte.cdk.integrations.base.Source
import io.airbyte.cdk.integrations.source.jdbc.dto.JdbcPrivilegeDto
import io.airbyte.cdk.integrations.source.relationaldb.AbstractDbSource
import io.airbyte.cdk.integrations.source.relationaldb.CursorInfo
import io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils
import io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.enquoteIdentifier
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager
import io.airbyte.commons.functional.CheckedConsumer
import io.airbyte.commons.functional.CheckedFunction
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.stream.AirbyteStreamUtils
import io.airbyte.commons.util.AutoCloseableIterator
import io.airbyte.commons.util.AutoCloseableIterators
import io.airbyte.protocol.models.CommonField
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import java.sql.Connection
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.sql.SQLException
import java.util.*
import java.util.function.Consumer
import java.util.function.Function
import java.util.function.Predicate
import java.util.function.Supplier
import java.util.stream.Collectors
import javax.sql.DataSource
import org.apache.commons.lang3.tuple.ImmutablePair
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * This class contains helper functions and boilerplate for implementing a source connector for a
 * relational DB source which can be accessed via JDBC driver. If you are implementing a connector
 * for a relational DB which has a JDBC driver, make an effort to use this class.
 */
// This is onoly here because spotbugs complains about aggregatePrimateKeys and I wasn't able to
// figure out what it's complaining about
@SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
abstract class AbstractJdbcSource<Datatype>(
    driverClass: String,
    @JvmField val streamingQueryConfigProvider: Supplier<JdbcStreamingQueryConfig>,
    sourceOperations: JdbcCompatibleSourceOperations<Datatype>
) : AbstractDbSource<Datatype, JdbcDatabase>(driverClass), Source {
    @JvmField val sourceOperations: JdbcCompatibleSourceOperations<Datatype>

    override var quoteString: String? = null
    @JvmField val dataSources: MutableCollection<DataSource> = ArrayList()

    init {
        this.sourceOperations = sourceOperations
    }

    override fun queryTableFullRefresh(
        database: JdbcDatabase,
        columnNames: List<String>,
        schemaName: String?,
        tableName: String,
        syncMode: SyncMode,
        cursorField: Optional<String>
    ): AutoCloseableIterator<AirbyteRecordData> {
        AbstractDbSource.LOGGER.info("Queueing query for table: {}", tableName)
        val airbyteStream = AirbyteStreamUtils.convertFromNameAndNamespace(tableName, schemaName)
        return AutoCloseableIterators.lazyIterator<AirbyteRecordData>(
            Supplier<AutoCloseableIterator<AirbyteRecordData>> {
                try {
                    val stream =
                        database.unsafeQuery(
                            { connection: Connection ->
                                AbstractDbSource.LOGGER.info(
                                    "Preparing query for table: {}",
                                    tableName
                                )
                                val fullTableName: String =
                                    RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting(
                                        schemaName,
                                        tableName,
                                        quoteString!!
                                    )

                                val wrappedColumnNames =
                                    getWrappedColumnNames(
                                        database,
                                        connection,
                                        columnNames,
                                        schemaName,
                                        tableName
                                    )
                                val sql =
                                    java.lang.StringBuilder(
                                        String.format(
                                            "SELECT %s FROM %s",
                                            wrappedColumnNames,
                                            fullTableName
                                        )
                                    )
                                // if the connector emits intermediate states, the incremental query
                                // must be sorted by the cursor
                                // field
                                if (
                                    syncMode == SyncMode.INCREMENTAL && stateEmissionFrequency > 0
                                ) {
                                    val quotedCursorField: String =
                                        enquoteIdentifier(cursorField.get(), quoteString)
                                    sql.append(String.format(" ORDER BY %s ASC", quotedCursorField))
                                }

                                val preparedStatement = connection.prepareStatement(sql.toString())
                                AbstractDbSource.LOGGER.info(
                                    "Executing query for table {}: {}",
                                    tableName,
                                    preparedStatement
                                )
                                preparedStatement
                            },
                            sourceOperations::convertDatabaseRowToAirbyteRecordData
                        )
                    return@Supplier AutoCloseableIterators.fromStream<AirbyteRecordData>(
                        stream,
                        airbyteStream
                    )
                } catch (e: SQLException) {
                    throw java.lang.RuntimeException(e)
                }
            },
            airbyteStream
        )
    }

    /**
     * Configures a list of operations that can be used to check the connection to the source.
     *
     * @return list of consumers that run queries for the check command.
     */
    @Trace(operationName = AbstractDbSource.Companion.CHECK_TRACE_OPERATION_NAME)
    @Throws(Exception::class)
    override fun getCheckOperations(
        config: JsonNode?
    ): List<CheckedConsumer<JdbcDatabase, Exception>> {
        return ImmutableList.of(
            CheckedConsumer { database: JdbcDatabase ->
                LOGGER.info(
                    "Attempting to get metadata from the database to see if we can connect."
                )
                database.bufferedResultSetQuery(
                    CheckedFunction { connection: Connection -> connection.metaData.catalogs },
                    CheckedFunction { queryResult: ResultSet? ->
                        sourceOperations.rowToJson(queryResult!!)
                    }
                )
            }
        )
    }

    private fun getCatalog(database: SqlDatabase): String? {
        return (if (database.sourceConfig!!.has(JdbcUtils.DATABASE_KEY))
            database.sourceConfig!![JdbcUtils.DATABASE_KEY].asText()
        else null)
    }

    @Throws(Exception::class)
    override fun discoverInternal(
        database: JdbcDatabase,
        schema: String?
    ): List<TableInfo<CommonField<Datatype>>> {
        val internalSchemas: Set<String?> = HashSet(excludedInternalNameSpaces)
        LOGGER.info("Internal schemas to exclude: {}", internalSchemas)
        val tablesWithSelectGrantPrivilege =
            getPrivilegesTableForCurrentUser<JdbcPrivilegeDto>(database, schema)
        return database
            .bufferedResultSetQuery<JsonNode>( // retrieve column metadata from the database
                { connection: Connection ->
                    connection.metaData.getColumns(getCatalog(database), schema, null, null)
                }, // store essential column metadata to a Json object from the result set about
                // each column
                { resultSet: ResultSet -> this.getColumnMetadata(resultSet) }
            )
            .stream()
            .filter(
                excludeNotAccessibleTables(internalSchemas, tablesWithSelectGrantPrivilege)
            ) // group by schema and table name to handle the case where a table with the same name
            // exists in
            // multiple schemas.
            .collect(
                Collectors.groupingBy<JsonNode, ImmutablePair<String, String>>(
                    Function<JsonNode, ImmutablePair<String, String>> { t: JsonNode ->
                        ImmutablePair.of<String, String>(
                            t.get(INTERNAL_SCHEMA_NAME).asText(),
                            t.get(INTERNAL_TABLE_NAME).asText()
                        )
                    }
                )
            )
            .values
            .stream()
            .map<TableInfo<CommonField<Datatype>>> { fields: List<JsonNode> ->
                TableInfo<CommonField<Datatype>>(
                    nameSpace = fields[0].get(INTERNAL_SCHEMA_NAME).asText(),
                    name = fields[0].get(INTERNAL_TABLE_NAME).asText(),
                    fields =
                        fields
                            .stream() // read the column metadata Json object, and determine its
                            // type
                            .map { f: JsonNode ->
                                val datatype = sourceOperations.getDatabaseFieldType(f)
                                val jsonType = getAirbyteType(datatype)
                                LOGGER.debug(
                                    "Table {} column {} (type {}[{}], nullable {}) -> {}",
                                    fields[0].get(INTERNAL_TABLE_NAME).asText(),
                                    f.get(INTERNAL_COLUMN_NAME).asText(),
                                    f.get(INTERNAL_COLUMN_TYPE_NAME).asText(),
                                    f.get(INTERNAL_COLUMN_SIZE).asInt(),
                                    f.get(INTERNAL_IS_NULLABLE).asBoolean(),
                                    jsonType
                                )
                                object :
                                    CommonField<Datatype>(
                                        f.get(INTERNAL_COLUMN_NAME).asText(),
                                        datatype
                                    ) {}
                            }
                            .collect(Collectors.toList<CommonField<Datatype>>()),
                    cursorFields = extractCursorFields(fields)
                )
            }
            .collect(Collectors.toList<TableInfo<CommonField<Datatype>>>())
    }

    private fun extractCursorFields(fields: List<JsonNode>): List<String> {
        return fields
            .stream()
            .filter { field: JsonNode ->
                isCursorType(sourceOperations.getDatabaseFieldType(field))
            }
            .map<String>(
                Function<JsonNode, String> { field: JsonNode ->
                    field.get(INTERNAL_COLUMN_NAME).asText()
                }
            )
            .collect(Collectors.toList<String>())
    }

    protected fun excludeNotAccessibleTables(
        internalSchemas: Set<String?>,
        tablesWithSelectGrantPrivilege: Set<JdbcPrivilegeDto>?
    ): Predicate<JsonNode> {
        return Predicate<JsonNode> { jsonNode: JsonNode ->
            if (tablesWithSelectGrantPrivilege!!.isEmpty()) {
                return@Predicate isNotInternalSchema(jsonNode, internalSchemas)
            }
            (tablesWithSelectGrantPrivilege.stream().anyMatch { e: JdbcPrivilegeDto ->
                e.schemaName == jsonNode.get(INTERNAL_SCHEMA_NAME).asText()
            } &&
                tablesWithSelectGrantPrivilege.stream().anyMatch { e: JdbcPrivilegeDto ->
                    e.tableName == jsonNode.get(INTERNAL_TABLE_NAME).asText()
                } &&
                !internalSchemas.contains(jsonNode.get(INTERNAL_SCHEMA_NAME).asText()))
        }
    }

    // needs to override isNotInternalSchema for connectors that override
    // getPrivilegesTableForCurrentUser()
    protected open fun isNotInternalSchema(
        jsonNode: JsonNode,
        internalSchemas: Set<String?>
    ): Boolean {
        return !internalSchemas.contains(jsonNode.get(INTERNAL_SCHEMA_NAME).asText())
    }

    /**
     * @param resultSet Description of a column available in the table catalog.
     * @return Essential information about a column to determine which table it belongs to and its
     * type.
     */
    @Throws(SQLException::class)
    private fun getColumnMetadata(resultSet: ResultSet): JsonNode {
        val fieldMap =
            ImmutableMap.builder<
                    String, Any
                >() // we always want a namespace, if we cannot get a schema, use db name.
                .put(
                    INTERNAL_SCHEMA_NAME,
                    if (resultSet.getObject(JDBC_COLUMN_SCHEMA_NAME) != null)
                        resultSet.getString(JDBC_COLUMN_SCHEMA_NAME)
                    else resultSet.getObject(JDBC_COLUMN_DATABASE_NAME)
                )
                .put(INTERNAL_TABLE_NAME, resultSet.getString(JDBC_COLUMN_TABLE_NAME))
                .put(INTERNAL_COLUMN_NAME, resultSet.getString(JDBC_COLUMN_COLUMN_NAME))
                .put(INTERNAL_COLUMN_TYPE, resultSet.getString(JDBC_COLUMN_DATA_TYPE))
                .put(INTERNAL_COLUMN_TYPE_NAME, resultSet.getString(JDBC_COLUMN_TYPE_NAME))
                .put(INTERNAL_COLUMN_SIZE, resultSet.getInt(JDBC_COLUMN_SIZE))
                .put(INTERNAL_IS_NULLABLE, resultSet.getString(JDBC_IS_NULLABLE))
        if (resultSet.getString(JDBC_DECIMAL_DIGITS) != null) {
            fieldMap.put(INTERNAL_DECIMAL_DIGITS, resultSet.getString(JDBC_DECIMAL_DIGITS))
        }
        return Jsons.jsonNode(fieldMap.build())
    }

    @Throws(Exception::class)
    public override fun discoverInternal(
        database: JdbcDatabase
    ): List<TableInfo<CommonField<Datatype>>> {
        return discoverInternal(database, null)
    }

    public override fun getAirbyteType(columnType: Datatype): JsonSchemaType {
        return sourceOperations.getAirbyteType(columnType)
    }

    @VisibleForTesting
    @JvmRecord
    data class PrimaryKeyAttributesFromDb(
        val streamName: String,
        val primaryKey: String,
        val keySequence: Int
    )

    override fun discoverPrimaryKeys(
        database: JdbcDatabase,
        tableInfos: List<TableInfo<CommonField<Datatype>>>
    ): Map<String, MutableList<String>> {
        LOGGER.info(
            "Discover primary keys for tables: " +
                tableInfos
                    .stream()
                    .map { obj: TableInfo<CommonField<Datatype>> -> obj.name }
                    .collect(Collectors.toSet())
        )
        try {
            // Get all primary keys without specifying a table name
            val tablePrimaryKeys =
                aggregatePrimateKeys(
                    database.bufferedResultSetQuery<PrimaryKeyAttributesFromDb>(
                        { connection: Connection ->
                            connection.metaData.getPrimaryKeys(getCatalog(database), null, null)
                        },
                        { r: ResultSet ->
                            val schemaName: String =
                                if (r.getObject(JDBC_COLUMN_SCHEMA_NAME) != null)
                                    r.getString(JDBC_COLUMN_SCHEMA_NAME)
                                else r.getString(JDBC_COLUMN_DATABASE_NAME)
                            val streamName =
                                getFullyQualifiedTableName(
                                    schemaName,
                                    r.getString(JDBC_COLUMN_TABLE_NAME)
                                )
                            val primaryKey: String = r.getString(JDBC_COLUMN_COLUMN_NAME)
                            val keySeq: Int = r.getInt(KEY_SEQ)
                            PrimaryKeyAttributesFromDb(streamName, primaryKey, keySeq)
                        }
                    )
                )
            if (!tablePrimaryKeys.isEmpty()) {
                return tablePrimaryKeys
            }
        } catch (e: SQLException) {
            LOGGER.debug(
                String.format(
                    "Could not retrieve primary keys without a table name (%s), retrying",
                    e
                )
            )
        }
        // Get primary keys one table at a time
        return tableInfos
            .stream()
            .collect(
                Collectors.toMap<TableInfo<CommonField<Datatype>>, String, MutableList<String>>(
                    Function<TableInfo<CommonField<Datatype>>, String> {
                        tableInfo: TableInfo<CommonField<Datatype>> ->
                        getFullyQualifiedTableName(tableInfo.nameSpace, tableInfo.name)
                    },
                    Function<TableInfo<CommonField<Datatype>>, MutableList<String>> toMap@{
                        tableInfo: TableInfo<CommonField<Datatype>> ->
                        val streamName =
                            getFullyQualifiedTableName(tableInfo.nameSpace, tableInfo.name)
                        try {
                            val primaryKeys =
                                aggregatePrimateKeys(
                                    database.bufferedResultSetQuery<PrimaryKeyAttributesFromDb>(
                                        { connection: Connection ->
                                            connection.metaData.getPrimaryKeys(
                                                getCatalog(database),
                                                tableInfo.nameSpace,
                                                tableInfo.name
                                            )
                                        },
                                        { r: ResultSet ->
                                            PrimaryKeyAttributesFromDb(
                                                streamName,
                                                r.getString(JDBC_COLUMN_COLUMN_NAME),
                                                r.getInt(KEY_SEQ)
                                            )
                                        }
                                    )
                                )
                            return@toMap primaryKeys.getOrDefault(
                                streamName,
                                mutableListOf<String>()
                            )
                        } catch (e: SQLException) {
                            LOGGER.error(
                                String.format(
                                    "Could not retrieve primary keys for %s: %s",
                                    streamName,
                                    e
                                )
                            )
                            return@toMap mutableListOf<String>()
                        }
                    }
                )
            )
    }

    public override fun isCursorType(type: Datatype): Boolean {
        return sourceOperations.isCursorType(type)
    }

    override fun queryTableIncremental(
        database: JdbcDatabase,
        columnNames: List<String>,
        schemaName: String?,
        tableName: String,
        cursorInfo: CursorInfo,
        cursorFieldType: Datatype
    ): AutoCloseableIterator<AirbyteRecordData> {
        AbstractDbSource.LOGGER.info("Queueing query for table: {}", tableName)
        val airbyteStream = AirbyteStreamUtils.convertFromNameAndNamespace(tableName, schemaName)
        return AutoCloseableIterators.lazyIterator(
            {
                try {
                    val stream =
                        database.unsafeQuery(
                            { connection: Connection ->
                                AbstractDbSource.LOGGER.info(
                                    "Preparing query for table: {}",
                                    tableName
                                )
                                val fullTableName: String =
                                    RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting(
                                        schemaName,
                                        tableName,
                                        quoteString!!
                                    )
                                val quotedCursorField: String =
                                    enquoteIdentifier(cursorInfo.cursorField, quoteString)
                                val operator: String
                                if (cursorInfo.cursorRecordCount <= 0L) {
                                    operator = ">"
                                } else {
                                    val actualRecordCount =
                                        getActualCursorRecordCount(
                                            connection,
                                            fullTableName,
                                            quotedCursorField,
                                            cursorFieldType,
                                            cursorInfo.cursor
                                        )
                                    AbstractDbSource.LOGGER.info(
                                        "Table {} cursor count: expected {}, actual {}",
                                        tableName,
                                        cursorInfo.cursorRecordCount,
                                        actualRecordCount
                                    )
                                    operator =
                                        if (actualRecordCount == cursorInfo.cursorRecordCount) {
                                            ">"
                                        } else {
                                            ">="
                                        }
                                }
                                val wrappedColumnNames =
                                    getWrappedColumnNames(
                                        database,
                                        connection,
                                        columnNames,
                                        schemaName,
                                        tableName
                                    )
                                val sql =
                                    StringBuilder(
                                        String.format(
                                            "SELECT %s FROM %s WHERE %s %s ?",
                                            wrappedColumnNames,
                                            fullTableName,
                                            quotedCursorField,
                                            operator
                                        )
                                    )
                                // if the connector emits intermediate states, the incremental query
                                // must be sorted by the cursor
                                // field
                                if (stateEmissionFrequency > 0) {
                                    sql.append(String.format(" ORDER BY %s ASC", quotedCursorField))
                                }
                                val preparedStatement = connection.prepareStatement(sql.toString())
                                AbstractDbSource.LOGGER.info(
                                    "Executing query for table {}: {}",
                                    tableName,
                                    preparedStatement
                                )
                                sourceOperations.setCursorField(
                                    preparedStatement,
                                    1,
                                    cursorFieldType,
                                    cursorInfo.cursor!!
                                )
                                preparedStatement
                            },
                            sourceOperations::convertDatabaseRowToAirbyteRecordData
                        )
                    return@lazyIterator AutoCloseableIterators.fromStream<AirbyteRecordData>(
                        stream,
                        airbyteStream
                    )
                } catch (e: SQLException) {
                    throw RuntimeException(e)
                }
            },
            airbyteStream
        )
    }

    protected fun getCountColumnName(): String {
        return "record_count"
    }

    /** Some databases need special column names in the query. */
    @Throws(SQLException::class)
    protected fun getWrappedColumnNames(
        database: JdbcDatabase?,
        connection: Connection?,
        columnNames: List<String>,
        schemaName: String?,
        tableName: String?
    ): String? {
        return RelationalDbQueryUtils.enquoteIdentifierList(columnNames, quoteString!!)
    }

    @Throws(SQLException::class)
    protected fun getActualCursorRecordCount(
        connection: Connection,
        fullTableName: String?,
        quotedCursorField: String?,
        cursorFieldType: Datatype,
        cursor: String?
    ): Long {
        val columnName = getCountColumnName()
        val cursorRecordStatement: PreparedStatement
        if (cursor == null) {
            val cursorRecordQuery =
                String.format(
                    "SELECT COUNT(*) AS %s FROM %s WHERE %s IS NULL",
                    columnName,
                    fullTableName,
                    quotedCursorField
                )
            cursorRecordStatement = connection.prepareStatement(cursorRecordQuery)
        } else {
            val cursorRecordQuery =
                String.format(
                    "SELECT COUNT(*) AS %s FROM %s WHERE %s = ?",
                    columnName,
                    fullTableName,
                    quotedCursorField
                )
            cursorRecordStatement = connection.prepareStatement(cursorRecordQuery)

            sourceOperations.setCursorField(cursorRecordStatement, 1, cursorFieldType, cursor)
        }
        val resultSet = cursorRecordStatement.executeQuery()
        return if (resultSet.next()) {
            resultSet.getLong(columnName)
        } else {
            0L
        }
    }

    @Throws(SQLException::class)
    public override fun createDatabase(sourceConfig: JsonNode): JdbcDatabase {
        return createDatabase(sourceConfig, JdbcDataSourceUtils.DEFAULT_JDBC_PARAMETERS_DELIMITER)
    }

    @Throws(SQLException::class)
    fun createDatabase(sourceConfig: JsonNode, delimiter: String): JdbcDatabase {
        val jdbcConfig = toDatabaseConfig(sourceConfig)
        val connectionProperties =
            JdbcDataSourceUtils.getConnectionProperties(sourceConfig, delimiter)
        // Create the data source
        val dataSource =
            create(
                if (jdbcConfig!!.has(JdbcUtils.USERNAME_KEY))
                    jdbcConfig[JdbcUtils.USERNAME_KEY].asText()
                else null,
                if (jdbcConfig.has(JdbcUtils.PASSWORD_KEY))
                    jdbcConfig[JdbcUtils.PASSWORD_KEY].asText()
                else null,
                driverClassName,
                jdbcConfig[JdbcUtils.JDBC_URL_KEY].asText(),
                connectionProperties,
                getConnectionTimeout(connectionProperties!!)
            )
        // Record the data source so that it can be closed.
        dataSources.add(dataSource)

        val database: JdbcDatabase =
            StreamingJdbcDatabase(dataSource, sourceOperations, streamingQueryConfigProvider)

        quoteString =
            (if (quoteString == null) database.metaData.identifierQuoteString else quoteString)
        database.sourceConfig = sourceConfig
        database.databaseConfig = jdbcConfig
        return database
    }

    /**
     * {@inheritDoc}
     *
     * @param database database instance
     * @param catalog schema of the incoming messages.
     * @throws SQLException
     */
    @Throws(SQLException::class)
    override fun logPreSyncDebugData(database: JdbcDatabase, catalog: ConfiguredAirbyteCatalog?) {
        LOGGER.info(
            "Data source product recognized as {}:{}",
            database.metaData.databaseProductName,
            database.metaData.databaseProductVersion
        )
    }

    override fun close() {
        dataSources.forEach(
            Consumer { d: DataSource? ->
                try {
                    close(d)
                } catch (e: Exception) {
                    LOGGER.warn("Unable to close data source.", e)
                }
            }
        )
        dataSources.clear()
    }

    protected fun identifyStreamsToSnapshot(
        catalog: ConfiguredAirbyteCatalog,
        stateManager: StateManager
    ): List<ConfiguredAirbyteStream> {
        val alreadySyncedStreams = stateManager.cdcStateManager.initialStreamsSynced
        if (
            alreadySyncedStreams!!.isEmpty() &&
                (stateManager.cdcStateManager.cdcState?.state == null)
        ) {
            return emptyList()
        }

        val allStreams = AirbyteStreamNameNamespacePair.fromConfiguredCatalog(catalog)

        val newlyAddedStreams: Set<AirbyteStreamNameNamespacePair> =
            HashSet(Sets.difference(allStreams, alreadySyncedStreams))

        return catalog.streams
            .stream()
            .filter { c: ConfiguredAirbyteStream -> c.syncMode == SyncMode.INCREMENTAL }
            .filter { stream: ConfiguredAirbyteStream ->
                newlyAddedStreams.contains(
                    AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.stream)
                )
            }
            .map { `object`: ConfiguredAirbyteStream -> Jsons.clone(`object`) }
            .collect(Collectors.toList())
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(AbstractJdbcSource::class.java)

        /**
         * Aggregate list of @param entries of StreamName and PrimaryKey and
         *
         * @return a map by StreamName to associated list of primary keys
         */
        @VisibleForTesting
        fun aggregatePrimateKeys(
            entries: List<PrimaryKeyAttributesFromDb>
        ): Map<String, MutableList<String>> {
            val result: MutableMap<String, MutableList<String>> = HashMap()
            entries
                .stream()
                .sorted(Comparator.comparingInt(PrimaryKeyAttributesFromDb::keySequence))
                .forEach { entry: PrimaryKeyAttributesFromDb ->
                    if (!result.containsKey(entry.streamName)) {
                        result[entry.streamName] = ArrayList()
                    }
                    result[entry.streamName]!!.add(entry.primaryKey)
                }
            return result
        }
    }
}
