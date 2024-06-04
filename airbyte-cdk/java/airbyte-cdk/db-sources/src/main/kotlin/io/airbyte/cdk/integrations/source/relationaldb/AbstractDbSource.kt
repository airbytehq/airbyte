/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.relationaldb

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.base.Preconditions
import datadog.trace.api.Trace
import io.airbyte.cdk.db.AbstractDatabase
import io.airbyte.cdk.db.IncrementalUtils.getCursorField
import io.airbyte.cdk.db.IncrementalUtils.getCursorFieldOptional
import io.airbyte.cdk.db.IncrementalUtils.getCursorType
import io.airbyte.cdk.db.jdbc.AirbyteRecordData
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.JdbcConnector
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility.emitConfigErrorTrace
import io.airbyte.cdk.integrations.base.Source
import io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage.getErrorMessage
import io.airbyte.cdk.integrations.source.relationaldb.state.*
import io.airbyte.cdk.integrations.util.ApmTraceUtils.addExceptionToTrace
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.exceptions.ConnectionErrorException
import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.airbyte.commons.features.FeatureFlags
import io.airbyte.commons.functional.CheckedConsumer
import io.airbyte.commons.lang.Exceptions
import io.airbyte.commons.stream.AirbyteStreamUtils
import io.airbyte.commons.util.AutoCloseableIterator
import io.airbyte.commons.util.AutoCloseableIterators
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.CommonField
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.*
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.SQLException
import java.time.Duration
import java.time.Instant
import java.util.*
import java.util.concurrent.atomic.AtomicLong
import java.util.stream.Stream

private val LOGGER = KotlinLogging.logger {}
/**
 * This class contains helper functions and boilerplate for implementing a source connector for a DB
 * source of both non-relational and relational type
 */
abstract class AbstractDbSource<DataType, Database : AbstractDatabase?>
protected constructor(driverClassName: String) :
    JdbcConnector(driverClassName), Source, AutoCloseable {
    // TODO: Remove when the flag is not use anymore
    var featureFlags: FeatureFlags = EnvVariableFeatureFlags()

    @Trace(operationName = CHECK_TRACE_OPERATION_NAME)
    @Throws(Exception::class)
    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        try {
            val database = createDatabase(config)
            for (checkOperation in getCheckOperations(config)) {
                checkOperation.accept(database)
            }

            return AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
        } catch (ex: ConnectionErrorException) {
            addExceptionToTrace(ex)
            val message = getErrorMessage(ex.stateCode, ex.errorCode, ex.exceptionMessage, ex)
            emitConfigErrorTrace(ex, message)
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(message)
        } catch (e: Exception) {
            addExceptionToTrace(e)
            LOGGER.info { "Exception while checking connection: $e" }
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(
                    String.format(
                        ConnectorExceptionUtil.COMMON_EXCEPTION_MESSAGE_TEMPLATE,
                        e.message
                    )
                )
        } finally {
            close()
        }
    }

    @Trace(operationName = DISCOVER_TRACE_OPERATION_NAME)
    @Throws(Exception::class)
    override fun discover(config: JsonNode): AirbyteCatalog {
        try {
            val database = createDatabase(config)
            val tableInfos = discoverWithoutSystemTables(database)
            val fullyQualifiedTableNameToPrimaryKeys = discoverPrimaryKeys(database, tableInfos)
            return DbSourceDiscoverUtil.convertTableInfosToAirbyteCatalog(
                tableInfos,
                fullyQualifiedTableNameToPrimaryKeys
            ) { columnType: DataType -> this.getAirbyteType(columnType) }
        } finally {
            close()
        }
    }

    /**
     * Creates a list of AirbyteMessageIterators with all the streams selected in a configured
     * catalog
     *
     * @param config
     * - integration-specific configuration object as json. e.g. { "username": "airbyte",
     * "password": "super secure" }
     * @param catalog
     * - schema of the incoming messages.
     * @param state
     * - state of the incoming messages.
     * @return AirbyteMessageIterator with all the streams that are to be synced
     * @throws Exception
     */
    @Throws(Exception::class)
    override fun read(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        state: JsonNode?
    ): AutoCloseableIterator<AirbyteMessage> {
        val supportedStateType = getSupportedStateType(config)
        val stateManager =
            StateManagerFactory.createStateManager(
                supportedStateType,
                StateGeneratorUtils.deserializeInitialState(state, supportedStateType),
                catalog
            )
        val emittedAt = Instant.now()

        val database = createDatabase(config)

        logPreSyncDebugData(database, catalog)

        val fullyQualifiedTableNameToInfo =
            discoverWithoutSystemTables(database).associateBy {
                String.format("%s.%s", it.nameSpace, it.name)
            }

        validateCursorFieldForIncrementalTables(fullyQualifiedTableNameToInfo, catalog, database)

        DbSourceDiscoverUtil.logSourceSchemaChange(fullyQualifiedTableNameToInfo, catalog) {
            columnType: DataType ->
            this.getAirbyteType(columnType)
        }

        initializeForStateManager(database, catalog, fullyQualifiedTableNameToInfo, stateManager)

        val incrementalIterators =
            getIncrementalIterators(
                database,
                catalog,
                fullyQualifiedTableNameToInfo,
                stateManager,
                emittedAt
            )
        val fullRefreshIterators =
            getFullRefreshIterators(
                database,
                catalog,
                fullyQualifiedTableNameToInfo,
                stateManager,
                emittedAt
            )
        val iteratorList =
            Stream.of(incrementalIterators, fullRefreshIterators)
                .flatMap(Collection<AutoCloseableIterator<AirbyteMessage>>::stream)
                .toList()

        return AutoCloseableIterators.appendOnClose(
            AutoCloseableIterators.concatWithEagerClose(
                iteratorList,
                AirbyteTraceMessageUtility::emitStreamStatusTrace
            )
        ) {
            LOGGER.info { "Closing database connection pool." }
            Exceptions.toRuntime { this.close() }
            LOGGER.info { "Closed database connection pool." }
        }
    }

    // Optional - perform any initialization logic before read. For example, source connector
    // can choose to load up state manager here.
    protected open fun initializeForStateManager(
        database: Database,
        catalog: ConfiguredAirbyteCatalog,
        tableNameToTable: Map<String, TableInfo<CommonField<DataType>>>,
        stateManager: StateManager
    ) {}

    @Throws(SQLException::class)
    protected fun validateCursorFieldForIncrementalTables(
        tableNameToTable: Map<String, TableInfo<CommonField<DataType>>>,
        catalog: ConfiguredAirbyteCatalog,
        database: Database
    ) {
        val tablesWithInvalidCursor: MutableList<InvalidCursorInfoUtil.InvalidCursorInfo> =
            ArrayList()
        for (airbyteStream in catalog.streams) {
            val stream = airbyteStream.stream
            val fullyQualifiedTableName =
                DbSourceDiscoverUtil.getFullyQualifiedTableName(stream.namespace, stream.name)
            val hasSourceDefinedCursor =
                (!Objects.isNull(airbyteStream.stream.sourceDefinedCursor) &&
                    airbyteStream.stream.sourceDefinedCursor)
            if (
                !tableNameToTable.containsKey(fullyQualifiedTableName) ||
                    airbyteStream.syncMode != SyncMode.INCREMENTAL ||
                    hasSourceDefinedCursor
            ) {
                continue
            }

            val table = tableNameToTable[fullyQualifiedTableName]!!
            val cursorField = getCursorFieldOptional(airbyteStream)
            if (cursorField.isEmpty) {
                continue
            }
            val cursorType =
                table.fields
                    .filter { info: CommonField<DataType> -> info.name == cursorField.get() }
                    .map { obj: CommonField<DataType> -> obj.type }
                    .first()

            if (!isCursorType(cursorType)) {
                tablesWithInvalidCursor.add(
                    InvalidCursorInfoUtil.InvalidCursorInfo(
                        fullyQualifiedTableName,
                        cursorField.get(),
                        cursorType.toString(),
                        "Unsupported cursor type"
                    )
                )
                continue
            }

            if (
                !verifyCursorColumnValues(
                    database,
                    stream.namespace,
                    stream.name,
                    cursorField.get()
                )
            ) {
                tablesWithInvalidCursor.add(
                    InvalidCursorInfoUtil.InvalidCursorInfo(
                        fullyQualifiedTableName,
                        cursorField.get(),
                        cursorType.toString(),
                        "Cursor column contains NULL value"
                    )
                )
            }
        }

        if (!tablesWithInvalidCursor.isEmpty()) {
            throw ConfigErrorException(
                InvalidCursorInfoUtil.getInvalidCursorConfigMessage(tablesWithInvalidCursor)
            )
        }
    }

    /**
     * Verify that cursor column allows syncing to go through.
     *
     * @param database database
     * @return true if syncing can go through. false otherwise
     * @throws SQLException exception
     */
    @Throws(SQLException::class)
    protected open fun verifyCursorColumnValues(
        database: Database,
        schema: String?,
        tableName: String?,
        columnName: String?
    ): Boolean {
        /* no-op */
        return true
    }

    /**
     * Estimates the total volume (rows and bytes) to sync and emits a [AirbyteEstimateTraceMessage]
     * associated with the full refresh stream.
     *
     * @param database database
     */
    protected open fun estimateFullRefreshSyncSize(
        database: Database,
        configuredAirbyteStream: ConfiguredAirbyteStream?
    ) {
        /* no-op */
    }

    @Throws(Exception::class)
    protected fun discoverWithoutSystemTables(
        database: Database
    ): List<TableInfo<CommonField<DataType>>> {
        val systemNameSpaces = excludedInternalNameSpaces
        val systemViews = excludedViews
        val discoveredTables = discoverInternal(database)
        return (if (systemNameSpaces.isEmpty()) discoveredTables
        else
            discoveredTables.filter { table: TableInfo<CommonField<DataType>> ->
                !systemNameSpaces.contains(table.nameSpace) && !systemViews.contains(table.name)
            })
    }

    protected fun getFullRefreshIterators(
        database: Database,
        catalog: ConfiguredAirbyteCatalog,
        tableNameToTable: Map<String, TableInfo<CommonField<DataType>>>,
        stateManager: StateManager?,
        emittedAt: Instant
    ): List<AutoCloseableIterator<AirbyteMessage>> {
        return getSelectedIterators(
            database,
            catalog,
            tableNameToTable,
            stateManager,
            emittedAt,
            SyncMode.FULL_REFRESH
        )
    }

    protected open fun getIncrementalIterators(
        database: Database,
        catalog: ConfiguredAirbyteCatalog,
        tableNameToTable: Map<String, TableInfo<CommonField<DataType>>>,
        stateManager: StateManager?,
        emittedAt: Instant
    ): List<AutoCloseableIterator<AirbyteMessage>> {
        return getSelectedIterators(
            database,
            catalog,
            tableNameToTable,
            stateManager,
            emittedAt,
            SyncMode.INCREMENTAL
        )
    }

    /**
     * Creates a list of read iterators for each stream within an ConfiguredAirbyteCatalog
     *
     * @param database Source Database
     * @param catalog List of streams (e.g. database tables or API endpoints) with settings on sync
     * mode
     * @param tableNameToTable Mapping of table name to table
     * @param stateManager Manager used to track the state of data synced by the connector
     * @param emittedAt Time when data was emitted from the Source database
     * @param syncMode the sync mode for which we want to grab the required iterators
     * @return List of AirbyteMessageIterators containing all iterators for a catalog
     */
    private fun getSelectedIterators(
        database: Database,
        catalog: ConfiguredAirbyteCatalog?,
        tableNameToTable: Map<String, TableInfo<CommonField<DataType>>>,
        stateManager: StateManager?,
        emittedAt: Instant,
        syncMode: SyncMode
    ): List<AutoCloseableIterator<AirbyteMessage>> {
        val iteratorList: MutableList<AutoCloseableIterator<AirbyteMessage>> = ArrayList()
        for (airbyteStream in catalog!!.streams) {
            if (airbyteStream.syncMode == syncMode) {
                val stream = airbyteStream.stream
                val fullyQualifiedTableName =
                    DbSourceDiscoverUtil.getFullyQualifiedTableName(stream.namespace, stream.name)
                if (!tableNameToTable.containsKey(fullyQualifiedTableName)) {
                    LOGGER.info {
                        "Skipping stream $fullyQualifiedTableName because it is not in the source"
                    }
                    continue
                }

                val table = tableNameToTable[fullyQualifiedTableName]!!
                val tableReadIterator =
                    createReadIterator(
                        database,
                        airbyteStream,
                        catalog,
                        table,
                        stateManager,
                        emittedAt
                    )
                iteratorList.add(tableReadIterator)
            }
        }

        return iteratorList
    }

    /**
     * ReadIterator is used to retrieve records from a source connector
     *
     * @param database Source Database
     * @param airbyteStream represents an ingestion source (e.g. API endpoint or database table)
     * @param table information in tabular format
     * @param stateManager Manager used to track the state of data synced by the connector
     * @param emittedAt Time when data was emitted from the Source database
     * @return
     */
    protected open fun createReadIterator(
        database: Database,
        airbyteStream: ConfiguredAirbyteStream,
        catalog: ConfiguredAirbyteCatalog?,
        table: TableInfo<CommonField<DataType>>,
        stateManager: StateManager?,
        emittedAt: Instant
    ): AutoCloseableIterator<AirbyteMessage> {
        val streamName = airbyteStream.stream.name
        val namespace = airbyteStream.stream.namespace
        val pair =
            io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair(streamName, namespace)
        val selectedFieldsInCatalog = CatalogHelpers.getTopLevelFieldNames(airbyteStream)
        val selectedDatabaseFields =
            table.fields
                .map { obj: CommonField<DataType> -> obj.name }
                .filter { o: String -> selectedFieldsInCatalog.contains(o) }

        val iterator: AutoCloseableIterator<AirbyteMessage>
        // checks for which sync mode we're using based on the configured airbytestream
        // this is where the bifurcation between full refresh and incremental
        if (airbyteStream.syncMode == SyncMode.INCREMENTAL) {
            val cursorField = getCursorField(airbyteStream)
            val cursorInfo = stateManager!!.getCursorInfo(pair)

            val airbyteMessageIterator: AutoCloseableIterator<AirbyteMessage>
            if (cursorInfo.map { it.cursor }.isPresent) {
                airbyteMessageIterator =
                    getIncrementalStream(
                        database,
                        airbyteStream,
                        selectedDatabaseFields,
                        table,
                        cursorInfo.get(),
                        emittedAt
                    )
            } else {
                // if no cursor is present then this is the first read for is the same as doing a
                // full refresh read.
                estimateFullRefreshSyncSize(database, airbyteStream)
                airbyteMessageIterator =
                    getFullRefreshStream(
                        database,
                        airbyteStream,
                        catalog,
                        stateManager,
                        namespace,
                        selectedDatabaseFields,
                        table,
                        emittedAt,
                        SyncMode.INCREMENTAL,
                        Optional.of(cursorField)
                    )
            }

            getCursorType(airbyteStream, cursorField)

            val messageProducer =
                CursorStateMessageProducer(stateManager, cursorInfo.map { it.cursor })

            iterator =
                AutoCloseableIterators.transform(
                    { autoCloseableIterator: AutoCloseableIterator<AirbyteMessage> ->
                        SourceStateIterator(
                            autoCloseableIterator,
                            airbyteStream,
                            messageProducer,
                            StateEmitFrequency(stateEmissionFrequency.toLong(), Duration.ZERO)
                        )
                    },
                    airbyteMessageIterator,
                    AirbyteStreamUtils.convertFromNameAndNamespace(pair.name, pair.namespace)
                )
        } else if (airbyteStream.syncMode == SyncMode.FULL_REFRESH) {
            estimateFullRefreshSyncSize(database, airbyteStream)
            iterator =
                getFullRefreshStream(
                    database,
                    airbyteStream,
                    catalog,
                    stateManager,
                    namespace,
                    selectedDatabaseFields,
                    table,
                    emittedAt,
                    SyncMode.FULL_REFRESH,
                    Optional.empty()
                )
        } else if (airbyteStream.syncMode == null) {
            throw IllegalArgumentException(
                String.format("%s requires a source sync mode", this.javaClass)
            )
        } else {
            throw IllegalArgumentException(
                String.format(
                    "%s does not support sync mode: %s.",
                    this.javaClass,
                    airbyteStream.syncMode
                )
            )
        }

        val recordCount = AtomicLong()
        return AutoCloseableIterators.transform<AirbyteMessage, AirbyteMessage>(
            iterator,
            AirbyteStreamUtils.convertFromNameAndNamespace(pair.name, pair.namespace)
        ) { r: AirbyteMessage ->
            val count = recordCount.incrementAndGet()
            if (count % 10000 == 0L) {
                LOGGER.info { "Reading stream $streamName. Records read: $count" }
            }
            r
        }
    }

    /**
     * @param database Source Database
     * @param airbyteStream represents an ingestion source (e.g. API endpoint or database table)
     * @param selectedDatabaseFields subset of database fields selected for replication
     * @param table information in tabular format
     * @param cursorInfo state of where to start the sync from
     * @param emittedAt Time when data was emitted from the Source database
     * @return AirbyteMessage Iterator that
     */
    private fun getIncrementalStream(
        database: Database,
        airbyteStream: ConfiguredAirbyteStream,
        selectedDatabaseFields: List<String>,
        table: TableInfo<CommonField<DataType>>,
        cursorInfo: CursorInfo,
        emittedAt: Instant
    ): AutoCloseableIterator<AirbyteMessage> {
        val streamName = airbyteStream.stream.name
        val namespace = airbyteStream.stream.namespace
        val cursorField = getCursorField(airbyteStream)
        val cursorType =
            table.fields
                .filter { info: CommonField<DataType> -> info.name == cursorField }
                .map { obj: CommonField<DataType> -> obj.type }
                .first()

        Preconditions.checkState(
            table.fields.any { f: CommonField<DataType> -> f.name == cursorField },
            String.format("Could not find cursor field %s in table %s", cursorField, table.name)
        )

        val queryIterator =
            queryTableIncremental(
                database,
                selectedDatabaseFields,
                table.nameSpace,
                table.name,
                cursorInfo,
                cursorType
            )

        return getMessageIterator(queryIterator, streamName, namespace, emittedAt.toEpochMilli())
    }

    /**
     * Creates a AirbyteMessageIterator that contains all records for a database source connection
     *
     * @param database Source Database
     * @param airbyteStream name of an individual stream in which a stream represents a source (e.g.
     * API endpoint or database table)
     * @param catalog List of streams (e.g. database tables or API endpoints) with settings on sync
     * @param stateManager tracking the state from previous sync; used for resumable full refresh.
     * @param namespace Namespace of the database (e.g. public)
     * @param selectedDatabaseFields List of all interested database column names
     * @param table information in tabular format
     * @param emittedAt Time when data was emitted from the Source database
     * @param syncMode The sync mode that this full refresh stream should be associated with.
     * @return AirbyteMessageIterator with all records for a database source
     */
    protected open fun getFullRefreshStream(
        database: Database,
        airbyteStream: ConfiguredAirbyteStream,
        catalog: ConfiguredAirbyteCatalog?,
        stateManager: StateManager?,
        namespace: String,
        selectedDatabaseFields: List<String>,
        table: TableInfo<CommonField<DataType>>,
        emittedAt: Instant,
        syncMode: SyncMode,
        cursorField: Optional<String>
    ): AutoCloseableIterator<AirbyteMessage> {
        val queryStream =
            queryTableFullRefresh(
                database,
                selectedDatabaseFields,
                table.nameSpace,
                table.name,
                syncMode,
                cursorField
            )
        return getMessageIterator(
            queryStream,
            airbyteStream.stream.name,
            namespace,
            emittedAt.toEpochMilli()
        )
    }

    /**
     * @param database
     * - The database where from privileges for tables will be consumed
     * @param schema
     * - The schema where from privileges for tables will be consumed
     * @return Set with privileges for tables for current DB-session user The method is responsible
     * for SELECT-ing the table with privileges. In some cases such SELECT doesn't require (e.g. in
     * Oracle DB - the schema is the user, you cannot REVOKE a privilege on a table from its owner).
     */
    @Throws(SQLException::class)
    protected open fun <T> getPrivilegesTableForCurrentUser(
        database: JdbcDatabase?,
        schema: String?
    ): Set<T> {
        return emptySet()
    }

    /**
     * Map a database implementation-specific configuration to json object that adheres to the
     * database config spec. See resources/spec.json.
     *
     * @param config database implementation-specific configuration.
     * @return database spec config
     */
    @Trace(operationName = DISCOVER_TRACE_OPERATION_NAME)
    abstract fun toDatabaseConfig(config: JsonNode): JsonNode

    /**
     * Creates a database instance using the database spec config.
     *
     * @param config database spec config
     * @return database instance
     * @throws Exception might throw an error during connection to database
     */
    @Trace(operationName = DISCOVER_TRACE_OPERATION_NAME)
    @Throws(Exception::class)
    protected abstract fun createDatabase(config: JsonNode): Database

    /**
     * Gets and logs relevant and useful database metadata such as DB product/version, index names
     * and definition. Called before syncing data. Any logged information should be scoped to the
     * configured catalog and database.
     *
     * @param database given database instance.
     * @param catalog configured catalog.
     */
    @Throws(Exception::class)
    protected open fun logPreSyncDebugData(
        database: Database,
        catalog: ConfiguredAirbyteCatalog?
    ) {}

    /**
     * Configures a list of operations that can be used to check the connection to the source.
     *
     * @return list of consumers that run queries for the check command.
     */
    @Throws(Exception::class)
    protected abstract fun getCheckOperations(
        config: JsonNode?
    ): List<CheckedConsumer<Database, Exception>>

    /**
     * Map source types to Airbyte types
     *
     * @param columnType source data type
     * @return airbyte data type
     */
    protected abstract fun getAirbyteType(columnType: DataType): JsonSchemaType

    protected abstract val excludedInternalNameSpaces: Set<String>

    protected open val excludedViews: Set<String>
        /**
         * Get list of system views in order to exclude them from the `discover` result list.
         *
         * @return set of views to be excluded
         */
        get() = emptySet()

    /**
     * Discover all available tables in the source database.
     *
     * @param database source database
     * @return list of the source tables
     * @throws Exception access to the database might lead to an exceptions.
     */
    @Trace(operationName = DISCOVER_TRACE_OPERATION_NAME)
    @Throws(Exception::class)
    protected abstract fun discoverInternal(
        database: Database
    ): List<TableInfo<CommonField<DataType>>>

    /**
     * Discovers all available tables within a schema in the source database.
     *
     * @param database
     * - source database
     * @param schema
     * - source schema
     * @return list of source tables
     * @throws Exception
     * - access to the database might lead to exceptions.
     */
    @Throws(Exception::class)
    protected abstract fun discoverInternal(
        database: Database,
        schema: String?
    ): List<TableInfo<CommonField<DataType>>>

    /**
     * Discover Primary keys for each table and @return a map of namespace.table name to their
     * associated list of primary key fields.
     *
     * @param database source database
     * @param tableInfos list of tables
     * @return map of namespace.table and primary key fields.
     */
    protected abstract fun discoverPrimaryKeys(
        database: Database,
        tableInfos: List<TableInfo<CommonField<DataType>>>
    ): Map<String, MutableList<String>>

    protected abstract val quoteString: String?

    /**
     * Read all data from a table.
     *
     * @param database source database
     * @param columnNames interested column names
     * @param schemaName table namespace
     * @param tableName target table
     * @param syncMode The sync mode that this full refresh stream should be associated with.
     * @return iterator with read data
     */
    protected abstract fun queryTableFullRefresh(
        database: Database,
        columnNames: List<String>,
        schemaName: String?,
        tableName: String,
        syncMode: SyncMode,
        cursorField: Optional<String>
    ): AutoCloseableIterator<AirbyteRecordData>

    /**
     * Read incremental data from a table. Incremental read should return only records where cursor
     * column value is bigger than cursor. Note that if the connector needs to emit intermediate
     * state (i.e. [AbstractDbSource.getStateEmissionFrequency] > 0), the incremental query must be
     * sorted by the cursor field.
     *
     * @return iterator with read data
     */
    protected abstract fun queryTableIncremental(
        database: Database,
        columnNames: List<String>,
        schemaName: String?,
        tableName: String,
        cursorInfo: CursorInfo,
        cursorFieldType: DataType
    ): AutoCloseableIterator<AirbyteRecordData>

    protected open val stateEmissionFrequency: Int
        /**
         * When larger than 0, the incremental iterator will emit intermediate state for every N
         * records. Please note that if intermediate state emission is enabled, the incremental
         * query must be ordered by the cursor field.
         *
         * TODO: Return an optional value instead of 0 to make it easier to understand.
         */
        get() = 0

    /** @return list of fields that could be used as cursors */
    protected abstract fun isCursorType(type: DataType): Boolean

    /**
     * Returns the [AirbyteStateType] supported by this connector.
     *
     * @param config The connector configuration.
     * @return A [AirbyteStateType] representing the state supported by this connector.
     */
    protected open fun getSupportedStateType(
        config: JsonNode?
    ): AirbyteStateMessage.AirbyteStateType {
        return AirbyteStateMessage.AirbyteStateType.STREAM
    }

    companion object {
        const val CHECK_TRACE_OPERATION_NAME: String = "check-operation"
        const val DISCOVER_TRACE_OPERATION_NAME: String = "discover-operation"
        const val READ_TRACE_OPERATION_NAME: String = "read-operation"

        @JvmStatic
        private fun getMessageIterator(
            recordIterator: AutoCloseableIterator<AirbyteRecordData>,
            streamName: String,
            namespace: String,
            emittedAt: Long
        ): AutoCloseableIterator<AirbyteMessage> {
            return AutoCloseableIterators.transform(
                recordIterator,
                AirbyteStreamNameNamespacePair(streamName, namespace)
            ) { airbyteRecordData ->
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(streamName)
                            .withNamespace(namespace)
                            .withEmittedAt(emittedAt)
                            .withData(airbyteRecordData.rawRowData)
                            .withMeta(
                                if (isMetaChangesEmptyOrNull(airbyteRecordData.meta)) null
                                else airbyteRecordData.meta
                            )
                    )
            }
        }

        private fun isMetaChangesEmptyOrNull(meta: AirbyteRecordMessageMeta?): Boolean {
            return meta == null || meta.changes == null || meta.changes.isEmpty()
        }
    }
}
