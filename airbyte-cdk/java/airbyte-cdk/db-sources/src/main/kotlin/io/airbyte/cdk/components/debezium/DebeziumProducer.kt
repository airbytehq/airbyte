/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.components.debezium

import io.airbyte.cdk.components.ConsumerComponent
import io.airbyte.cdk.components.ProducerComponent
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.SyncMode
import io.debezium.engine.ChangeEvent
import io.debezium.engine.DebeziumEngine
import io.debezium.engine.format.Json
import io.debezium.spi.common.ReplacementFunction
import io.debezium.storage.file.history.FileSchemaHistory
import java.lang.reflect.Method
import java.time.Duration
import java.util.*
import java.util.regex.Pattern
import org.apache.kafka.connect.connector.Connector
import org.apache.kafka.connect.runtime.standalone.StandaloneConfig
import org.apache.kafka.connect.source.SourceRecord
import org.apache.kafka.connect.storage.FileOffsetBackingStore
import org.codehaus.plexus.util.StringUtils
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/** [ProducerComponent] for Debezium. Essentially a wrapper around [DebeziumEngine]. */
class DebeziumProducer
private constructor(
    debeziumProperties: Properties,
    boundChecker: BoundChecker,
    consumer: ConsumerComponent<DebeziumRecord>,
    notifyStop: () -> Unit,
    private val initialState: DebeziumState,
) : ProducerComponent<DebeziumState> {

    private val stateFilesAccessor = StateFilesAccessor()

    init {
        // Write offset and schema files.
        stateFilesAccessor.writeOffset(initialState.offset)
        initialState.schema.ifPresent(stateFilesAccessor::writeSchema)
        // Add missing offset and schema history file path properties.
        debeziumProperties.setProperty(
            StandaloneConfig.OFFSET_STORAGE_FILE_FILENAME_CONFIG,
            stateFilesAccessor.offsetFilePath.toString()
        )
        if (initialState.schema.isPresent) {
            debeziumProperties.setProperty(
                FileSchemaHistory.FILE_PATH.name(),
                stateFilesAccessor.schemaFilePath.toString()
            )
        }
    }

    private val engine: DebeziumEngine<ChangeEvent<String?, String?>> =
        DebeziumEngine.create(Json::class.java)
            .using(debeziumProperties)
            // Event handler.
            .notifying { event ->
                if (event.value() == null) {
                    // Debezium outputs a tombstone event that has a value of null. This is an
                    // artifact of how it interacts with kafka. We want to ignore it. More on the
                    // tombstone:
                    // https://debezium.io/documentation/reference/2.2/transformations/event-flattening.html
                    return@notifying
                }
                val record = DebeziumRecord(Jsons.deserialize(event.value()))
                // Heartbeat events aren't useful to the consumer, they're used for bound checks.
                if (!record.isHeartbeat) {
                    consumer.accept(record)
                    if (consumer.shouldCheckpoint()) {
                        // Stop if we need to checkpoint.
                        notifyStop()
                    }
                }
                if (!boundChecker.checkWithinBound(record, maybeGetSourceRecord(event))) {
                    // Stop if we've reached the upper bound.
                    notifyStop()
                }
            }
            // Completion handler.
            .using { success: Boolean, message: String, error: Throwable? ->
                if (success) {
                    log.info("Debezium engine has shut down successfully: {}", message)
                } else {
                    log.warn("Debezium engine has NOT shut down successfully: {}", message, error)
                    // There are cases where Debezium doesn't succeed but only fills the message
                    // field.
                    throw (error ?: RuntimeException(message))
                }
            }
            .build()

    override fun run() = engine.run()

    override fun close() {
        // The EmbeddedEngine's close() is idempotent and blocking.
        engine.close()
    }

    override fun finalState() =
        DebeziumState(
            stateFilesAccessor.readUpdatedOffset(initialState.offset),
            initialState.schema.map { _ -> stateFilesAccessor.readSchema() }
        )

    companion object {
        private val log: Logger = LoggerFactory.getLogger(DebeziumProducer::class.java)
        private val embeddedEngineChangeEventClass: Class<*> =
            Class.forName("io.debezium.embedded.EmbeddedEngineChangeEvent")
        private val getSourceRecord: Method =
            embeddedEngineChangeEventClass.getDeclaredMethod("sourceRecord").apply {
                isAccessible = true
            }

        @JvmStatic
        private fun maybeGetSourceRecord(event: ChangeEvent<String?, String?>): SourceRecord? =
            if (embeddedEngineChangeEventClass.isInstance(event)) {
                val obj: Any? = getSourceRecord(event)
                if (obj is SourceRecord) obj else null
            } else {
                null
            }
    }

    private fun interface BoundChecker {
        /**
         * Returns true iff the Debezium [Record] is within bounds. The Debezium [SourceRecord]
         * accompanying the [Record] is preferred, but this object is internal to the Debezium
         * Engine and therefore may not always be available.
         */
        fun checkWithinBound(record: DebeziumRecord, sourceRecord: SourceRecord?): Boolean
    }

    class Builder : ProducerComponent.Builder<DebeziumRecord, DebeziumState> {

        internal val props: Properties = Properties()

        private lateinit var boundChecker: BoundChecker

        fun withBoundChecker(lsnMapper: LsnMapper<*>, upperBound: DebeziumState): Builder = apply {
            boundChecker =
                object : BoundChecker {
                    val anyLsnMapper = lsnMapper.asAny()
                    val upperBoundLsn = lsnMapper.asAny().get(upperBound.offset)

                    override fun checkWithinBound(
                        record: DebeziumRecord,
                        sourceRecord: SourceRecord?
                    ): Boolean {
                        val lsn = (sourceRecord?.let(anyLsnMapper::get) ?: anyLsnMapper.get(record))
                        return if (lsn == null) true else lsn < upperBoundLsn
                    }

                    override fun toString(): String = "BoundChecker(lsn < $upperBoundLsn)"
                }
        }

        override fun build(
            input: DebeziumState,
            consumer: ConsumerComponent<DebeziumRecord>,
            notifyStop: () -> Unit
        ): ProducerComponent<DebeziumState> =
            DebeziumProducer(props.clone() as Properties, boundChecker, consumer, notifyStop, input)

        init {
            // default values from debezium CommonConnectorConfig
            props.setProperty("max.batch.size", "2048")
            props.setProperty("max.queue.size", "8192")

            // Disabling retries because debezium startup time might exceed our 60-second wait limit
            // The maximum number of retries on connection errors before failing (-1 = no limit, 0 =
            // disabled, >
            // 0 = num of retries).
            props.setProperty("errors.max.retries", "0")

            // This property must be strictly less than errors.retry.delay.max.ms
            // (https://github.com/debezium/debezium/blob/bcc7d49519a4f07d123c616cfa45cd6268def0b9/debezium-core/src/main/java/io/debezium/util/DelayStrategy.java#L135)
            props.setProperty("errors.retry.delay.initial.ms", "299")
            props.setProperty("errors.retry.delay.max.ms", "300")

            // https://debezium.io/documentation/reference/2.2/configuration/avro.html
            props.setProperty("key.converter.schemas.enable", "false")
            props.setProperty("value.converter.schemas.enable", "false")

            // By default "decimal.handing.mode=precise" which's caused returning this value as a
            // binary. The "double" type may cause a loss of precision, so set Debezium's config to
            // store it as a String explicitly in its Kafka messages. For more details see:
            // https://debezium.io/documentation/reference/2.2/connectors/postgresql.html#postgresql-decimal-types
            // https://debezium.io/documentation/faq/#how_to_retrieve_decimal_field_from_binary_representation
            props.setProperty("decimal.handling.mode", "string")

            props.setProperty("offset.storage", FileOffsetBackingStore::class.java.canonicalName)
            props.setProperty("offset.flush.interval.ms", "1000") // todo: make this longer

            // https://issues.redhat.com/browse/DBZ-7635
            // https://cwiki.apache.org/confluence/display/KAFKA/KIP-581%3A+Value+of+optional+null+field+which+has+default+value
            // A null value in a column with default value won't be generated correctly in CDC
            // unless we set the following.
            props.setProperty("value.converter.replace.null.with.default", "false")

            // Timeout for DebeziumEngine's close() method.
            props.setProperty("debezium.embedded.shutdown.pause.before.interrupt.ms", "10000")
        }

        fun withSchemaHistory(): Builder =
            with("schema.history.internal", FileSchemaHistory::class.java.canonicalName)
                .with("schema.history.internal.store.only.captured.databases.ddl", "true")

        fun withDebeziumName(name: String): Builder =
            with("name", name)
                // WARNING: Never change the value of this otherwise all the connectors would start
                // syncing from scratch.
                .with("topic.prefix", sanitizeTopicPrefix(name))

        fun withConnector(connectorClass: Class<out Connector>): Builder =
            with("connector.class", connectorClass.canonicalName)

        fun withHeartbeats(heartbeatInterval: Duration): Builder =
            with("heartbeat.interval.ms", heartbeatInterval.toMillis().toString())

        fun with(key: String, value: String): Builder = apply { props.setProperty(key, value) }

        fun with(properties: Map<*, *>): Builder = apply { props.putAll(properties) }

        fun withDatabaseHost(host: String): Builder = with("database.hostname", host)

        fun withDatabasePort(port: Int): Builder = with("database.port", port.toString())

        fun withDatabaseUser(user: String): Builder = with("database.user", user)

        fun withDatabasePassword(password: String): Builder = with("database.password", password)

        fun withDatabaseName(name: String): Builder =
            with("database.dbname", name).withDebeziumName(name)

        /** Tells Debezium which tables and columns we care about. */
        fun withCatalog(catalog: ConfiguredAirbyteCatalog): Builder {
            val incrementalStreams: List<AirbyteStream> =
                catalog.streams
                    .filter { cs -> cs.syncMode == SyncMode.INCREMENTAL }
                    .map { cs -> cs.stream }
            val tableIncludeList =
                incrementalStreams.map { s -> Pattern.quote("${s.namespace}.${s.name}") }
            val columnIncludeList: List<String> =
                incrementalStreams.map { s ->
                    val prefix = Pattern.quote("${s.namespace}.${s.name}")
                    val suffix =
                        s.jsonSchema["properties"]
                            .fieldNames()
                            .asSequence()
                            .map(Pattern::quote)
                            .joinToString("|")
                    "$prefix\\.($suffix)"
                }
            return with("table.include.list", joinIncludeList(tableIncludeList))
                .with("column.include.list", joinIncludeList(columnIncludeList))
        }

        private fun joinIncludeList(includes: List<String>): String =
            includes.map { StringUtils.escape(it, ",".toCharArray(), "\\,") }.joinToString(",")

        private fun sanitizeTopicPrefix(topicName: String): String =
            topicName.asSequence().map(this::sanitizedChar).joinToString("")

        // We need to keep the validation rule the same as debezium engine, which is defined here:
        // https://github.com/debezium/debezium/blob/c51ef3099a688efb41204702d3aa6d4722bb4825/debezium-core/src/main/java/io/debezium/schema/AbstractTopicNamingStrategy.java#L178
        private fun sanitizedChar(c: Char): String =
            when (c) {
                '.',
                '_',
                '-',
                in 'A'..'Z',
                in 'a'..'z',
                in '0'..'9' -> c.toString()
                else -> ReplacementFunction.UNDERSCORE_REPLACEMENT.replace(c)
            }
    }
}
