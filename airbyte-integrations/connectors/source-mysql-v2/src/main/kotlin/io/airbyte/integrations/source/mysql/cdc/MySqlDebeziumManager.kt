/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.cdc

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.integrations.debezium.internals.AirbyteFileOffsetBackingStore
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.AirbyteSchemaHistoryStorage
import io.airbyte.cdk.read.DebeziumManager
import io.airbyte.integrations.source.mysql.cdc.MySqlCdcState.Companion.IS_COMPRESSED
import io.airbyte.integrations.source.mysql.cdc.MySqlCdcState.Companion.MYSQL_CDC_OFFSET
import io.airbyte.integrations.source.mysql.cdc.MySqlCdcState.Companion.MYSQL_DB_HISTORY
import io.airbyte.integrations.source.mysql.cdc.MySqlDebeziumStateUtil.Companion.MysqlDebeziumStateAttributes
import io.airbyte.integrations.source.mysql.cdc.MySqlDebeziumStateUtil.Companion.constructBinlogOffset
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.debezium.config.Configuration
import io.debezium.connector.common.OffsetReader
import io.debezium.connector.mysql.MySqlConnectorConfig
import io.debezium.connector.mysql.MySqlOffsetContext
import io.debezium.connector.mysql.MySqlPartition
import io.debezium.connector.mysql.gtid.MySqlGtidSet
import io.debezium.embedded.KafkaConnectUtil
import io.debezium.pipeline.spi.Offsets
import io.debezium.pipeline.spi.Partition
import io.debezium.relational.RelationalDatabaseConnectorConfig
import io.debezium.spi.common.ReplacementFunction
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.ResultSet
import java.sql.SQLException
import java.util.*
import java.util.regex.Pattern
import java.util.stream.Collectors
import java.util.stream.StreamSupport
import kotlin.math.floor
import org.apache.kafka.connect.json.JsonConverter
import org.apache.kafka.connect.runtime.WorkerConfig
import org.apache.kafka.connect.runtime.standalone.StandaloneConfig
import org.apache.kafka.connect.storage.FileOffsetBackingStore
import org.apache.kafka.connect.storage.OffsetStorageReaderImpl
import org.codehaus.plexus.util.StringUtils

private val log = KotlinLogging.logger {}

@Singleton
@Primary
class MySqlDebeziumManager(
    val config: JdbcSourceConfiguration,
    val catalog: ConfiguredAirbyteCatalog,
    jdbcConnectionFactory: JdbcConnectionFactory
) : DebeziumManager {

    val dbName = config.namespaces.first().toString()
    val jdbcConnectionFactory = jdbcConnectionFactory

    private lateinit var offsetManager: AirbyteFileOffsetBackingStore
    private lateinit var schemaHistoryStorage: AirbyteSchemaHistoryStorage

    override fun getPropertiesForSync(opaqueStateValue: OpaqueStateValue?): Properties {
        val props = Properties()

        setMyqlProps(props)
        // RELATIONAL CONFIGS
        setRelationalDbProps(props)
        setBaseProps(props)
        setOffsetProps(props, opaqueStateValue)
        return props
    }

    override fun getPropertiesForSchemaHistory(): Properties {
        val props = Properties()

        setMyqlProps(props)

        // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-snapshot-mode
        // We use the recovery property cause using this mode will instruct Debezium to
        // construct the db schema history.
        // Note that we used to use schema_only_recovery mode, but this mode has been deprecated.
        props.setProperty("snapshot.mode", "recovery")
        // RELATIONAL CONFIGS
        setRelationalDbProps(props)
        setBaseProps(props)
        setOffsetProps(props, null)
        return props
    }

    override fun readOffsetState(): OpaqueStateValue {
        val offset : Map<String, String> = offsetManager.read()
        val schemaHistory: AirbyteSchemaHistoryStorage.SchemaHistory<String> =
            schemaHistoryStorage.read()

        assert(!offset.isEmpty())
        assert(Objects.nonNull(schemaHistory))
        assert(Objects.nonNull(schemaHistory.schema))

        val offsetReader = OffsetReader<Partition, MySqlOffsetContext, MySqlOffsetContext.Loader>(
            offsetStorageReader,
            loader,
        )
        val offsets = offsetReader.offsets(partitions)

        val state: OpaqueStateValue = serialize(offset, schemaHistory)
        // check if offset is on LSN server
        savedOffsetStillPresentOnServer(jdbcConnectionFactory.get(), state)
        return state
    }

    /**
     * Creates and starts a [FileOffsetBackingStore] that is used to store the tracked Debezium
     * offset state.
     *
     * @param properties The Debezium configuration properties for the selected Debezium connector.
     * @return A configured and started [FileOffsetBackingStore] instance.
     */
    fun getFileOffsetBackingStore(properties: MutableMap<String, String>): FileOffsetBackingStore? {
        val fileOffsetBackingStore = KafkaConnectUtil.fileOffsetBackingStore()
        properties[WorkerConfig.KEY_CONVERTER_CLASS_CONFIG] = JsonConverter::class.java.name
        properties[WorkerConfig.VALUE_CONVERTER_CLASS_CONFIG] = JsonConverter::class.java.name
        fileOffsetBackingStore.configure(StandaloneConfig(properties))
        fileOffsetBackingStore.start()
        return fileOffsetBackingStore
    }

    fun extractGtidSetFromState(state: OpaqueStateValue) : Set<String> {

        val properties = offsetManager.read()
        val fileOffsetBackingStore = getFileOffsetBackingStore(properties.toMutableMap())
        val offsetStorageReader =
            OffsetStorageReaderImpl(
                fileOffsetBackingStore,
                properties["name"],
                JsonConverter(),
                JsonConverter(),
            )
        val connectorConfig = MySqlConnectorConfig(Configuration.from(properties))
        val loader = MySqlOffsetContext.Loader(connectorConfig)
        val partitions = setOf<Partition>(
            MySqlPartition(
                connectorConfig.logicalName,
                properties[RelationalDatabaseConnectorConfig.DATABASE_NAME.name()],
            ),
            )


        val offsetReader = OffsetReader<Partition, MySqlOffsetContext, MySqlOffsetContext.Loader>(
            offsetStorageReader,
            loader,
        )
        val offsets = offsetReader.offsets(partitions)

        return extractStateAttributes(partitions, offsets)
    }

    private fun extractStateAttributes(
        partitions: Set<Partition>,
        offsets: Map<Partition, MySqlOffsetContext>
    ): Optional<MySqlDebeziumStateUtil.MysqlDebeziumStateAttributes> {
        var found = false
        for (partition in partitions) {
            val mySqlOffsetContext = offsets[partition]

            if (mySqlOffsetContext != null) {
                found = true
                logger.info(
                    "Found previous partition offset {}: {}",
                    partition,
                    mySqlOffsetContext.offset,
                )
            }
        }

        if (!found) {
            MySqlDebeziumStateUtil.LOGGER.info("No previous offsets found")
            return Optional.empty<MySqlDebeziumStateUtil.MysqlDebeziumStateAttributes>()
        }

        val of = Offsets.of(offsets)
        val previousOffset = of.theOnlyOffset

        return Optional.of<MySqlDebeziumStateUtil.MysqlDebeziumStateAttributes>(
            MySqlDebeziumStateUtil.MysqlDebeziumStateAttributes(
                previousOffset.source.binlogFilename(), previousOffset.source.binlogPosition(),
                Optional.ofNullable<String>(previousOffset.gtidSet()),
            ),
        )
    }

    fun savedOffsetStillPresentOnServer(
        jdbcConnection: Connection,
        savedStateAttributes: MysqlDebeziumStateAttributes
    ): Boolean {
        if (savedStateAttributes.gtidSet.isPresent()) {
            val availableGtidStr = MySqlDebeziumStateUtil.getStateAttributesFromDB(jdbcConnection).gtidSet
            if (availableGtidStr.isEmpty) {
                // Last offsets had GTIDs but the server does not use them
                log.info("Connector used GTIDs previously, but MySQL server does not know of any GTIDs or they are not enabled")
                return false
            }
            val gtidSetFromSavedState: MySqlGtidSet = MySqlGtidSet(savedStateAttributes.gtidSet.get())
            // Get the GTID set that is available in the server
            val availableGtidSet: MySqlGtidSet = MySqlGtidSet(availableGtidStr.get())
            if (gtidSetFromSavedState.isContainedWithin(availableGtidSet)) {
                log.info(
                    "MySQL server current GTID set {} does contain the GTID set required by the connector {}",
                    availableGtidSet,
                    gtidSetFromSavedState,
                )
                val gtidSetToReplicate: Optional<MySqlGtidSet> =
                    subtractGtidSet(availableGtidSet, gtidSetFromSavedState, jdbcConnection)
                if (gtidSetToReplicate.isPresent()) {
                    val purgedGtidSet: Optional<MySqlGtidSet> = purgedGtidSet(database)
                    if (purgedGtidSet.isPresent()) {
                        log.info(
                            "MySQL server has already purged {} GTIDs",
                            purgedGtidSet.get(),
                        )
                        val nonPurgedGtidSetToReplicate: Optional<MySqlGtidSet> =
                            subtractGtidSet(gtidSetToReplicate.get(), purgedGtidSet.get(), jdbcConnection)
                        if (nonPurgedGtidSetToReplicate.isPresent()) {
                            log.info(
                                "GTIDs known by the MySQL server but not processed yet {}, for replication are available only {}",
                                gtidSetToReplicate,
                                nonPurgedGtidSetToReplicate,
                            )
                            if (gtidSetToReplicate != nonPurgedGtidSetToReplicate) {
                                log.info("Some of the GTIDs needed to replicate have been already purged by MySQL server")
                                return false
                            }
                        }
                    }
                }
                return true
            }
            MySqlDebeziumStateUtil.LOGGER.info(
                "Connector last known GTIDs are {}, but MySQL server only has {}",
                gtidSetFromSavedState,
                availableGtidSet,
            )
            return false
        }

        val existingLogFiles: List<String> = getExistingLogFiles(database)
        val found = existingLogFiles.stream()
            .anyMatch { anObject: String? -> savedState.binlogFilename.equals(anObject) }
        if (!found) {
            MySqlDebeziumStateUtil.LOGGER.info(
                "Connector requires binlog file '{}', but MySQL server only has {}",
                savedState.binlogFilename,
                java.lang.String.join(", ", existingLogFiles),
            )
        } else {
            MySqlDebeziumStateUtil.LOGGER.info(
                "MySQL server has the binlog file '{}' required by the connector",
                savedState.binlogFilename,
            )
        }

        return found
    }

    private fun subtractGtidSet(
        set1: MySqlGtidSet,
        set2: MySqlGtidSet,
        conn: Connection
    ): Optional<MySqlGtidSet> {
        try {
            conn.prepareStatement("SELECT GTID_SUBTRACT(?, ?)").use { ps ->
                ps.setString(1, set1.toString())
                ps.setString(2, set2.toString())
                ps.executeQuery().use { rs ->
                    val gtidSets = rs.toList()
                    return if (gtidSets.isEmpty()) {
                        Optional.empty()
                    } else if (gtidSets.size == 1) {
                        Optional.of(gtidSets[0])
                    } else {
                        throw RuntimeException("Not expecting gtid set size to be greater than 1")
                    }
                }
            }
        } catch (e: SQLException) {
            throw RuntimeException(e)
        }
    }

    private fun purgedGtidSet(conn: Connection): Optional<MySqlGtidSet> {
        try {

            val stream = conn.createStatement().executeQuery("SELECT @@global.gtid_purged").use { resultSet: ResultSet ->
                if (resultSet.metaData.columnCount > 0) {
                    val string = resultSet.getString(1)
                    if (string != null && !string.isEmpty()) {
                        return Optional.of<MySqlGtidSet>(
                            MySqlGtidSet(
                                string,
                            ),
                        )
                    }
                }
            }
                val gtidSet: List<Optional<MySqlGtidSet>> = stream.toList()
                return if (gtidSet.isEmpty()) {
                    Optional.empty()
                } else if (gtidSet.size == 1) {
                    gtidSet[0]
                } else {
                    throw java.lang.RuntimeException("Not expecting the size to be greater than 1")
                }

        } catch (e: SQLException) {
            throw java.lang.RuntimeException(e)
        }
    }


    fun serialize(
        offset: Map<String, String>,
        dbHistory: AirbyteSchemaHistoryStorage.SchemaHistory<String>
    ): JsonNode {
        val mapper = ObjectMapper()
        val internalState: MutableMap<String, Any> = HashMap()
        internalState[MYSQL_CDC_OFFSET] = offset
        internalState[MYSQL_DB_HISTORY] = dbHistory.schema
        internalState[IS_COMPRESSED] = dbHistory.isCompressed

        val internalStateNode: JsonNode = ObjectMapper().valueToTree(internalState)

        // Add original fields into the "state" field of the new structure
        val rootNode: ObjectNode = mapper.createObjectNode()
        rootNode.set<ObjectNode>("state", internalStateNode)

        return rootNode
    }

    fun setOffsetProps(props: Properties, opaqueStateValue: OpaqueStateValue?) {
        if (opaqueStateValue == null) {
            val emptySchemaHistory: AirbyteSchemaHistoryStorage.SchemaHistory<Optional<JsonNode>> =
                AirbyteSchemaHistoryStorage.SchemaHistory(Optional.empty(), false)

            val offset =
                constructBinlogOffset(
                    jdbcConnectionFactory.get(),
                    dbName,
                    sanitizeTopicPrefix(dbName),
                )
            offsetManager = AirbyteFileOffsetBackingStore.initializeState(offset, Optional.empty())
            schemaHistoryStorage =
                AirbyteSchemaHistoryStorage.initializeDBHistory(
                    emptySchemaHistory,
                    compressSchemaHistoryForState = false,
                )
        } else {
            // Initialize offset json node
            val mySqlCdcState = MySqlCdcState(opaqueStateValue)
            mySqlCdcState.savedOffset
            mySqlCdcState.getSavedSchemaHistory()

            offsetManager =
                AirbyteFileOffsetBackingStore.initializeState(
                    mySqlCdcState.savedOffset,
                    Optional.empty(),
                )
            schemaHistoryStorage =
                AirbyteSchemaHistoryStorage.initializeDBHistory(
                    mySqlCdcState.getSavedSchemaHistory(),
                    compressSchemaHistoryForState = false,
                )
        }

        offsetManager.setDebeziumProperties(props)
        schemaHistoryStorage.setDebeziumProperties(props)
    }

    fun setBaseProps(props: Properties) {
        // debezium engine configuration
        // default values from debezium CommonConnectorConfig
        props.setProperty("max.batch.size", "2048")
        props.setProperty("max.queue.size", "8192")

        props.setProperty("errors.max.retries", "0")
        // This property must be strictly less than errors.retry.delay.max.ms
        // (https://github.com/debezium/debezium/blob/bcc7d49519a4f07d123c616cfa45cd6268def0b9/debezium-core/src/main/java/io/debezium/util/DelayStrategy.java#L135)
        props.setProperty("errors.retry.delay.initial.ms", "299")
        props.setProperty("errors.retry.delay.max.ms", "300")

        // https://debezium.io/documentation/reference/2.2/configuration/avro.html
        props.setProperty("key.converter.schemas.enable", "false")
        props.setProperty("value.converter.schemas.enable", "false")

        // debezium names
        props.setProperty(NAME_KEY, dbName)

        // By default "decimal.handing.mode=precise" which's caused returning this value as a
        // binary.
        // The "double" type may cause a loss of precision, so set Debezium's config to store it as
        // a String
        // explicitly in its Kafka messages for more details see:
        // https://debezium.io/documentation/reference/2.2/connectors/postgresql.html#postgresql-decimal-types
        // https://debezium.io/documentation/faq/#how_to_retrieve_decimal_field_from_binary_representation
        props.setProperty("decimal.handling.mode", "string")

        // https://debezium.io/documentation/reference/2.2/connectors/postgresql.html#postgresql-property-max-queue-size-in-bytes
        props.setProperty("max.queue.size.in.bytes", BYTE_VALUE_256_MB)

        // WARNING : Never change the value of this otherwise all the connectors would start syncing
        // from
        // scratch.
        props.setProperty(TOPIC_PREFIX_KEY, sanitizeTopicPrefix(dbName))
        // https://issues.redhat.com/browse/DBZ-7635
        // https://cwiki.apache.org/confluence/display/KAFKA/KIP-581%3A+Value+of+optional+null+field+which+has+default+value
        // A null value in a column with default value won't be generated correctly in CDC unless we
        // set the
        // following
        props.setProperty("value.converter.replace.null.with.default", "false")

        props.setProperty("heartbeat.interval.ms", "1000") // Change to 10s for non tests
    }

    fun setRelationalDbProps(properties: Properties) {
        properties.setProperty("database.hostname", config.realHost)
        properties.setProperty("database.port", config.realPort.toString())
        properties.setProperty("database.user", config.jdbcProperties["user"])
        properties.setProperty("database.dbname", dbName)
        properties.setProperty("database.password", config.jdbcProperties["password"])

        // table selection
        properties.setProperty("table.include.list", getTableIncludelist(catalog))
        // column selection
        properties.setProperty("column.include.list", getColumnIncludeList(catalog))
    }

    fun setMyqlProps(props: Properties) {
        // debezium engine configuration
        props.setProperty("connector.class", "io.debezium.connector.mysql.MySqlConnector")
        props.setProperty("database.server.id", generateServerID().toString())

        // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-snapshot-mode
        props.setProperty("snapshot.mode", "when_needed")
        // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-snapshot-locking-mode
        // This is to make sure other database clients are allowed to write to a table while Airbyte
        // is
        // taking a snapshot. There is a risk involved that
        // if any database client makes a schema change then the sync might break
        props.setProperty("snapshot.locking.mode", "none")

        // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-include-schema-changes
        props.setProperty("include.schema.changes", "false")

        // This to make sure that binary data represented as a base64-encoded String.
        // https://debezium.io/documentation/reference/2.2/connectors/mysql.html#mysql-property-binary-handling-mode
        props.setProperty("binary.handling.mode", "base64")
        props.setProperty("database.include.list", dbName)
    }

    companion object {
        private const val BYTE_VALUE_256_MB = (256 * 1024 * 1024).toString()

        const val NAME_KEY: String = "name"
        const val TOPIC_PREFIX_KEY: String = "topic.prefix"

        @JvmStatic
        fun sanitizeTopicPrefix(topicName: String): String {
            val sanitizedNameBuilder = StringBuilder(topicName.length)
            var changed = false

            for (i in 0 until topicName.length) {
                val c = topicName[i]
                if (isValidCharacter(c)) {
                    sanitizedNameBuilder.append(c)
                } else {
                    sanitizedNameBuilder.append(
                        ReplacementFunction.UNDERSCORE_REPLACEMENT.replace(c),
                    )
                    changed = true
                }
            }

            return if (changed) {
                sanitizedNameBuilder.toString()
            } else {
                topicName
            }
        }

        // We need to keep the validation rule the same as debezium engine, which is defined here:
        // https://github.com/debezium/debezium/blob/c51ef3099a688efb41204702d3aa6d4722bb4825/debezium-core/src/main/java/io/debezium/schema/AbstractTopicNamingStrategy.java#L178
        private fun isValidCharacter(c: Char): Boolean {
            return c == '.' ||
                c == '_' ||
                c == '-' ||
                c >= 'A' && c <= 'Z' ||
                c >= 'a' && c <= 'z' ||
                c >= '0' && c <= '9'
        }

        private fun generateServerID(): Int {
            val min = 5400
            val max = 6400

            val serverId = floor(Math.random() * (max - min + 1) + min).toInt()
            return serverId
        }

        fun getTableIncludelist(
            catalog: ConfiguredAirbyteCatalog
            // completedStreamNames: List<String>
            ): String {
            // Turn "stream": {
            // "namespace": "schema1"
            // "name": "table1
            // },
            // "stream": {
            // "namespace": "schema2"
            // "name": "table2
            // } -------> info "schema1.table1, schema2.table2"

            return catalog.streams
                .filter { s: ConfiguredAirbyteStream -> s.syncMode == SyncMode.INCREMENTAL }
                .map { obj: ConfiguredAirbyteStream -> obj.stream }
                .map { stream: AirbyteStream -> stream.namespace + "." + stream.name }
                // .filter { streamName: String -> completedStreamNames.contains(streamName) }
                // debezium needs commas escaped to split properly
                .joinToString(",") { x: String ->
                    StringUtils.escape(Pattern.quote(x), ",".toCharArray(), "\\,")
                }
        }

        fun getColumnIncludeList(
            catalog: ConfiguredAirbyteCatalog
            // completedStreamNames: List<String>
            ): String {
            // Turn "stream": {
            // "namespace": "schema1"
            // "name": "table1"
            // "jsonSchema": {
            // "properties": {
            // "column1": {
            // },
            // "column2": {
            // }
            // }
            // }
            // } -------> info "schema1.table1.(column1 | column2)"

            return catalog.streams
                .filter { s: ConfiguredAirbyteStream -> s.syncMode == SyncMode.INCREMENTAL }
                .map { obj: ConfiguredAirbyteStream -> obj.stream }
                // .filter { stream: AirbyteStream ->
                //  completedStreamNames.contains(stream.namespace + "." + stream.name)
                // }
                .map { s: AirbyteStream ->
                    val fields = parseFields(s.jsonSchema["properties"].fieldNames())
                    Pattern.quote(s.namespace + "." + s.name) +
                        (if (StringUtils.isNotBlank(fields)) "\\.$fields" else "")
                }
                .joinToString(",") { x: String -> StringUtils.escape(x, ",".toCharArray(), "\\,") }
        }

        private fun parseFields(fieldNames: Iterator<String>?): String {
            if (fieldNames == null || !fieldNames.hasNext()) {
                return ""
            }
            val iter = Iterable { fieldNames }
            return StreamSupport.stream(iter.spliterator(), false)
                .map { f: String -> Pattern.quote(f) }
                .collect(Collectors.joining("|", "(", ")"))
        }
    }
}
