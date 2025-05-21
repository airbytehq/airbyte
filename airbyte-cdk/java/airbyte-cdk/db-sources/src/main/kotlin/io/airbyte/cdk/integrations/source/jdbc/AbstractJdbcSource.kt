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
import io.airbyte.cdk.integrations.source.relationaldb.InitialLoadHandler
import io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils
import io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.enquoteIdentifier
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateIterator
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateMessageProducer
import io.airbyte.cdk.integrations.source.relationaldb.state.StateEmitFrequency
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.functional.CheckedConsumer
import io.airbyte.commons.functional.CheckedFunction
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.stream.AirbyteStreamUtils
import io.airbyte.commons.util.AutoCloseableIterator
import io.airbyte.commons.util.AutoCloseableIterators
import io.airbyte.protocol.models.CommonField
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.airbyte.protocol.models.v0.SyncMode.*
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.sql.SQLException
import java.time.Duration
import java.time.Instant
import java.util.*
import java.util.function.Consumer
import java.util.function.Function
import java.util.function.Predicate
import java.util.function.Supplier
import java.util.stream.Collectors
import javax.sql.DataSource
import org.apache.commons.lang3.tuple.ImmutablePair

private val LOGGER = KotlinLogging.logger {}
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
    sourceOperations: JdbcCompatibleSourceOperations<Datatype>,
) : AbstractDbSource<Datatype, JdbcDatabase>(driverClass), Source {
    @JvmField val sourceOperations: JdbcCompatibleSourceOperations<Datatype>

    override var quoteString: String? = null
    @JvmField val dataSources: MutableCollection<DataSource> = ArrayList()

    init {
        this.sourceOperations = sourceOperations
    }

    open fun supportResumableFullRefresh(
        database: JdbcDatabase,
        airbyteStream: ConfiguredAirbyteStream
    ): Boolean {
        return false
    }

    override fun discover(config: JsonNode): AirbyteCatalog {
        var catalog = super.discover(config)
        var database = createDatabase(config)
        catalog.streams.forEach(
            Consumer { stream: AirbyteStream ->
                stream.isResumable =
                    supportResumableFullRefresh(
                        database,
                        CatalogHelpers.toDefaultConfiguredStream(stream)
                    )
            }
        )
        return catalog
    }

    open fun getInitialLoadHandler(
        database: JdbcDatabase,
        airbyteStream: ConfiguredAirbyteStream,
        catalog: ConfiguredAirbyteCatalog?,
        stateManager: StateManager?
    ): InitialLoadHandler<Datatype>? {
        return null
    }

    override fun getFullRefreshStream(
        database: JdbcDatabase,
        airbyteStream: ConfiguredAirbyteStream,
        catalog: ConfiguredAirbyteCatalog?,
        stateManager: StateManager?,
        namespace: String,
        selectedDatabaseFields: List<String>,
        table: TableInfo<CommonField<Datatype>>,
        emittedAt: Instant,
        syncMode: SyncMode,
        cursorField: Optional<String>
    ): AutoCloseableIterator<AirbyteMessage> {
        if (supportResumableFullRefresh(database, airbyteStream) && syncMode == FULL_REFRESH) {
            val initialLoadHandler =
                getInitialLoadHandler(database, airbyteStream, catalog, stateManager)
                    ?: throw IllegalStateException(
                        "Must provide initialLoadHandler for resumable full refresh."
                    )
            return augmentWithStreamStatus(
                airbyteStream,
                initialLoadHandler.getIteratorForStream(
                    airbyteStream,
                    table,
                    Instant.now(),
                    Optional.empty()
                )
            )
        }

        // If flag is off, fall back to legacy non-resumable refresh
        var iterator =
            super.getFullRefreshStream(
                database,
                airbyteStream,
                catalog,
                stateManager,
                namespace,
                selectedDatabaseFields,
                table,
                emittedAt,
                syncMode,
                cursorField,
            )

        if (airbyteStream.syncMode == FULL_REFRESH) {
            var defaultProducer = getSourceStateProducerForNonResumableFullRefreshStream(database)
            if (defaultProducer != null) {
                iterator =
                    AutoCloseableIterators.transform(
                        { autoCloseableIterator: AutoCloseableIterator<AirbyteMessage> ->
                            SourceStateIterator(
                                autoCloseableIterator,
                                airbyteStream,
                                defaultProducer,
                                StateEmitFrequency(stateEmissionFrequency.toLong(), Duration.ZERO)
                            )
                        },
                        iterator,
                        AirbyteStreamUtils.convertFromNameAndNamespace(
                            airbyteStream.stream.name,
                            airbyteStream.stream.namespace
                        )
                    )
            }
        }

        return when (airbyteStream.syncMode) {
            FULL_REFRESH -> augmentWithStreamStatus(airbyteStream, iterator)
            else -> iterator
        }
    }

    protected open fun getSourceStateProducerForNonResumableFullRefreshStream(
        database: JdbcDatabase
    ): SourceStateMessageProducer<AirbyteMessage>? {
        return null
    }

    open fun augmentWithStreamStatus(
        airbyteStream: ConfiguredAirbyteStream,
        streamItrator: AutoCloseableIterator<AirbyteMessage>
    ): AutoCloseableIterator<AirbyteMessage> {
        // no-op
        return streamItrator
    }

    override fun queryTableFullRefresh(
        database: JdbcDatabase,
        columnNames: List<String>,
        schemaName: String?,
        tableName: String,
        syncMode: SyncMode,
        cursorField: Optional<String>
    ): AutoCloseableIterator<AirbyteRecordData> {
        LOGGER.info { "Queueing query for table: $tableName" }
        val airbyteStream = AirbyteStreamUtils.convertFromNameAndNamespace(tableName, schemaName)
        return AutoCloseableIterators.lazyIterator<AirbyteRecordData>(
            Supplier<AutoCloseableIterator<AirbyteRecordData>> {
                try {
                    val stream =
                        database.unsafeQuery(
                            { connection: Connection ->
                                LOGGER.info { "Preparing query for table: $tableName" }
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
                                        "SELECT $wrappedColumnNames FROM $fullTableName"
                                    )
                                // if the connector emits intermediate states, the incremental query
                                // must be sorted by the cursor
                                // field
                                if (syncMode == INCREMENTAL && stateEmissionFrequency > 0) {
                                    val quotedCursorField: String =
                                        enquoteIdentifier(cursorField.get(), quoteString)
                                    sql.append(" ORDER BY $quotedCursorField ASC")
                                }

                                val preparedStatement = connection.prepareStatement(sql.toString())
                                LOGGER.info {
                                    "Executing query for table $tableName: $preparedStatement"
                                }
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
     * Checks that current user can SELECT from the tables in the schemas. We can override this
     * function if it takes too long to finish for a particular database source connector.
     */
    @Throws(Exception::class)
    protected open fun checkUserHasPrivileges(config: JsonNode?, database: JdbcDatabase) {
        var schemas = ArrayList<String>()
        if (config!!.has(JdbcUtils.SCHEMAS_KEY) && config[JdbcUtils.SCHEMAS_KEY].isArray) {
            for (schema in config[JdbcUtils.SCHEMAS_KEY]) {
                schemas.add(schema.asText())
            }
        }
        // if UI has schemas specified, check if the user has select access to any table
        if (schemas.isNotEmpty()) {
            for (schema in schemas) {
                LOGGER.info {
                    "Checking if the user can perform select to any table in schema: $schema"
                }
                val tablesOfSchema = database.metaData.getTables(null, schema, "%", null)
                if (tablesOfSchema.next()) {
                    var privileges =
                        getPrivilegesTableForCurrentUser<JdbcPrivilegeDto>(database, schema)
                    if (privileges.isEmpty()) {
                        LOGGER.info { "No table from schema $schema is accessible for the user." }
                        throw ConfigErrorException(
                            "User lacks privileges to SELECT from any of the tables in schema $schema"
                        )
                    }
                } else {
                    LOGGER.info { "Schema $schema does not contain any table." }
                }
            }
        } else {
            LOGGER.info {
                "No schema has been provided at the moment, skip table permission check."
            }
        }
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
                LOGGER.info {
                    "Attempting to get metadata from the database to see if we can connect."
                }
                database.bufferedResultSetQuery(
                    CheckedFunction { connection: Connection -> connection.metaData.catalogs },
                    CheckedFunction { queryResult: ResultSet ->
                        sourceOperations.rowToJson(queryResult)
                    },
                )
            },
            CheckedConsumer { database: JdbcDatabase -> checkUserHasPrivileges(config, database) },
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
        val internalSchemas: Set<String> = HashSet(excludedInternalNameSpaces)
        LOGGER.info { "Internal schemas to exclude: $internalSchemas" }
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
            .filter(
                excludeNotAccessibleTables(internalSchemas, tablesWithSelectGrantPrivilege)::test
            ) // group by schema and table name to handle the case where a table with the same name
            // exists in
            // multiple schemas.
            .groupBy { t: JsonNode ->
                ImmutablePair.of<String, String>(
                    t.get(INTERNAL_SCHEMA_NAME).asText(),
                    t.get(INTERNAL_TABLE_NAME).asText()
                )
            }
            .values
            .map { fields: List<JsonNode> -> jsonFieldListToTableInfo(fields) }
    }

    private fun extractCursorFields(fields: List<JsonNode>): List<String> {
        return fields
            .filter { field: JsonNode ->
                isCursorType(sourceOperations.getDatabaseFieldType(field))
            }
            .map { it.get(INTERNAL_COLUMN_NAME).asText() }
    }

    protected fun excludeNotAccessibleTables(
        internalSchemas: Set<String>,
        tablesWithSelectGrantPrivilege: Set<JdbcPrivilegeDto>?
    ): Predicate<JsonNode> {
        return Predicate<JsonNode> { jsonNode: JsonNode ->
            if (tablesWithSelectGrantPrivilege!!.isEmpty()) {
                return@Predicate isNotInternalSchema(jsonNode, internalSchemas)
            }
            (tablesWithSelectGrantPrivilege.any { e: JdbcPrivilegeDto ->
                e.schemaName == jsonNode.get(INTERNAL_SCHEMA_NAME).asText()
            } &&
                tablesWithSelectGrantPrivilege.any { e: JdbcPrivilegeDto ->
                    e.tableName == jsonNode.get(INTERNAL_TABLE_NAME).asText()
                } &&
                !internalSchemas.contains(jsonNode.get(INTERNAL_SCHEMA_NAME).asText()))
        }
    }

    // needs to override isNotInternalSchema for connectors that override
    // getPrivilegesTableForCurrentUser()
    protected open fun isNotInternalSchema(
        jsonNode: JsonNode,
        internalSchemas: Set<String>
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
        LOGGER.info { "Discover primary keys for tables: ${tableInfos.map { it.name }}" }
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
            LOGGER.debug { "Could not retrieve primary keys without a table name ($e), retrying" }
        }
        // Get primary keys one table at a time
        return tableInfos
            .stream()
            .collect(
                Collectors.toMap(
                    { tableInfo: TableInfo<CommonField<Datatype>> ->
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
                            LOGGER.error { "Could not retrieve primary keys for $streamName: $e" }
                            return@toMap mutableListOf<String>()
                        }
                    }
                )
            )
    }

    override fun discoverTable(
        database: JdbcDatabase,
        schema: String,
        tableName: String
    ): TableInfo<CommonField<Datatype>>? {
        LOGGER.info { "Discover table: $schema.$tableName" }
        return database
            .bufferedResultSetQuery<JsonNode>(
                { connection: Connection ->
                    connection.metaData.getColumns(getCatalog(database), schema, tableName, null)
                },
                { resultSet: ResultSet -> this.getColumnMetadata(resultSet) }
            )
            .groupBy { t: JsonNode ->
                ImmutablePair.of<String, String>(
                    t.get(INTERNAL_SCHEMA_NAME).asText(),
                    t.get(INTERNAL_TABLE_NAME).asText()
                )
            }
            .values
            .map { fields: List<JsonNode> -> jsonFieldListToTableInfo(fields) }
            .filter { ti: TableInfo<CommonField<Datatype>> -> ti.name == tableName }
            .firstOrNull()
    }

    private fun jsonFieldListToTableInfo(fields: List<JsonNode>): TableInfo<CommonField<Datatype>> {
        return TableInfo<CommonField<Datatype>>(
            nameSpace = fields[0].get(INTERNAL_SCHEMA_NAME).asText(),
            name = fields[0].get(INTERNAL_TABLE_NAME).asText(),
            fields =
                fields
                    // read the column metadata Json object, and determine its
                    // type
                    .map { f: JsonNode ->
                        val datatype = sourceOperations.getDatabaseFieldType(f)
                        val jsonType = getAirbyteType(datatype)
                        LOGGER.debug {
                            "Table ${fields[0].get(INTERNAL_TABLE_NAME).asText()} column ${f.get(INTERNAL_COLUMN_NAME).asText()}" +
                                "(type ${f.get(INTERNAL_COLUMN_TYPE_NAME).asText()}[${f.get(INTERNAL_COLUMN_SIZE).asInt()}], " +
                                "nullable ${f.get(INTERNAL_IS_NULLABLE).asBoolean()}) -> $jsonType"
                        }
                        object :
                            CommonField<Datatype>(f.get(INTERNAL_COLUMN_NAME).asText(), datatype) {}
                    },
            cursorFields = extractCursorFields(fields)
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
        LOGGER.info { "Queueing query for table: $tableName" }
        val airbyteStream = AirbyteStreamUtils.convertFromNameAndNamespace(tableName, schemaName)
        return AutoCloseableIterators.lazyIterator(
            {
                try {
                    val stream =
                        database.unsafeQuery(
                            { connection: Connection ->
                                LOGGER.info { "Preparing query for table: $tableName" }

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
                                    LOGGER.info {
                                        "Table $tableName cursor count: expected ${cursorInfo.cursorRecordCount}, actual $actualRecordCount"
                                    }
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
                                LOGGER.info {
                                    "Executing query for table $tableName: $preparedStatement"
                                }
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
    protected open fun getWrappedColumnNames(
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
                "SELECT COUNT(*) AS $columnName FROM $fullTableName WHERE $quotedCursorField IS NULL"
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
    public override fun createDatabase(config: JsonNode): JdbcDatabase {
        return createDatabase(config, JdbcDataSourceUtils.DEFAULT_JDBC_PARAMETERS_DELIMITER)
    }

    @Throws(SQLException::class)
    fun createDatabase(sourceConfig: JsonNode, delimiter: String): JdbcDatabase {
        val jdbcConfig = toDatabaseConfig(sourceConfig)
        val connectionProperties =
            JdbcDataSourceUtils.getConnectionProperties(sourceConfig, delimiter)
        // Create the data source
        val dataSource =
            create(
                if (jdbcConfig.has(JdbcUtils.USERNAME_KEY))
                    jdbcConfig[JdbcUtils.USERNAME_KEY].asText()
                else null,
                if (jdbcConfig.has(JdbcUtils.PASSWORD_KEY))
                    jdbcConfig[JdbcUtils.PASSWORD_KEY].asText()
                else null,
                driverClassName,
                jdbcConfig[JdbcUtils.JDBC_URL_KEY].asText(),
                connectionProperties,
                getConnectionTimeout(connectionProperties)
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
        LOGGER.info {
            "Data source product recognized as ${database.metaData.databaseProductName}:${database.metaData.databaseProductVersion}"
        }
    }

    override fun close() {
        dataSources.forEach(
            Consumer { d: DataSource ->
                try {
                    close(d)
                } catch (e: Exception) {
                    LOGGER.warn(e) { "Unable to close data source." }
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
            .filter { c: ConfiguredAirbyteStream -> c.syncMode == INCREMENTAL }
            .filter { stream: ConfiguredAirbyteStream ->
                newlyAddedStreams.contains(
                    AirbyteStreamNameNamespacePair.fromAirbyteStream(stream.stream)
                )
            }
            .map { `object`: ConfiguredAirbyteStream -> Jsons.clone(`object`) }
    }

    companion object {

        /**
         * Aggregate list of @param entries of StreamName and PrimaryKey and
         *
         * @return a map by StreamName to associated list of primary keys
         */
        @VisibleForTesting
        @JvmStatic
        fun aggregatePrimateKeys(
            entries: List<PrimaryKeyAttributesFromDb>
        ): Map<String, MutableList<String>> {
            val result: MutableMap<String, MutableList<String>> = HashMap()
            entries
                .sortedWith(Comparator.comparingInt(PrimaryKeyAttributesFromDb::keySequence))
                .forEach { entry: PrimaryKeyAttributesFromDb ->
                    if (!result.containsKey(entry.streamName)) {
                        result[entry.streamName] = ArrayList()
                    }
                    result[entry.streamName]!!.add(entry.primaryKey)
                }
            return result
        }
    }

    override fun createReadIterator(
        database: JdbcDatabase,
        airbyteStream: ConfiguredAirbyteStream,
        catalog: ConfiguredAirbyteCatalog?,
        table: TableInfo<CommonField<Datatype>>,
        stateManager: StateManager?,
        emittedAt: Instant
    ): AutoCloseableIterator<AirbyteMessage> {
        val iterator =
            super.createReadIterator(
                database,
                airbyteStream,
                catalog,
                table,
                stateManager,
                emittedAt
            )
        return when (airbyteStream.syncMode) {
            INCREMENTAL -> augmentWithStreamStatus(airbyteStream, iterator)
            else -> iterator
        }
    }
}
