/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.read.Stream
import io.debezium.spi.common.ReplacementFunction
import io.debezium.storage.file.history.FileSchemaHistory
import java.nio.file.Path
import java.time.Duration
import java.util.Properties
import java.util.regex.Pattern
import kotlin.reflect.KClass
import org.apache.kafka.connect.connector.Connector
import org.apache.kafka.connect.runtime.standalone.StandaloneConfig
import org.apache.kafka.connect.storage.FileOffsetBackingStore

/** Utility class for building [Properties] for initializing the Debezium engine. */
class DebeziumPropertiesBuilder(private val props: Properties = Properties()) {

    fun build(): Properties = props.clone() as Properties

    fun buildMap(): Map<String, String> =
        props.map { (k, v) -> k.toString() to v.toString() }.toMap()

    fun with(key: String, value: String): DebeziumPropertiesBuilder = apply {
        props.setProperty(key, value)
    }

    fun with(properties: Map<*, *>): DebeziumPropertiesBuilder = apply { props.putAll(properties) }

    fun withDefault(): DebeziumPropertiesBuilder = apply {
        // default values from debezium CommonConnectorConfig
        with("max.batch.size", "2048")
        with("max.queue.size", "8192")
        // Disabling retries because debezium startup time might exceed our 60-second wait limit
        // The maximum number of retries on connection errors before failing (-1 = no limit, 0 =
        // disabled, > 0 = num of retries).
        with("errors.max.retries", "0")
        // This property must be strictly less than errors.retry.delay.max.ms
        // (https://github.com/debezium/debezium/blob/bcc7d49519a4f07d123c616cfa45cd6268def0b9/debezium-core/src/main/java/io/debezium/util/DelayStrategy.java#L135)
        with("errors.retry.delay.initial.ms", "299")
        with("errors.retry.delay.max.ms", "300")
        // https://debezium.io/documentation/reference/2.2/configuration/avro.html
        with("key.converter.schemas.enable", "false")
        with("value.converter.schemas.enable", "false")
        // By default "decimal.handing.mode=precise" which's caused returning this value as a
        // binary. The "double" type may cause a loss of precision, so set Debezium's config to
        // store it as a String explicitly in its Kafka messages. For more details see:
        // https://debezium.io/documentation/reference/2.2/connectors/postgresql.html#postgresql-decimal-types
        // https://debezium.io/documentation/faq/#how_to_retrieve_decimal_field_from_binary_representation
        with("decimal.handling.mode", "string")
        // https://issues.redhat.com/browse/DBZ-7635
        // https://cwiki.apache.org/confluence/display/KAFKA/KIP-581%3A+Value+of+optional+null+field+which+has+default+value
        // A null value in a column with default value won't be generated correctly in CDC
        // unless we set the following.
        with("value.converter.replace.null.with.default", "false")
        // Timeout for DebeziumEngine's close() method.
        // We find that in production, substantial time is in fact legitimately required here.
        with("debezium.embedded.shutdown.pause.before.interrupt.ms", "60000")
        // Unblock CDC syncs by skipping errors caused by unparseable DDLs
        with("schema.history.internal.skip.unparseable.ddl", "true")
    }

    fun withOffset(): DebeziumPropertiesBuilder = apply {
        with("offset.storage", FileOffsetBackingStore::class.java.canonicalName)
    }

    val expectsOffsetFile: Boolean
        get() = props["offset.storage"] == FileOffsetBackingStore::class.java.canonicalName

    fun withOffsetFile(offsetFilePath: Path): DebeziumPropertiesBuilder =
        if (expectsOffsetFile) {
            with(StandaloneConfig.OFFSET_STORAGE_FILE_FILENAME_CONFIG, offsetFilePath.toString())
        } else {
            this
        }

    fun withSchemaHistory(): DebeziumPropertiesBuilder = apply {
        with("schema.history.internal", FileSchemaHistory::class.java.canonicalName)
        with("schema.history.internal.store.only.captured.databases.ddl", "true")
    }

    val expectsSchemaHistoryFile: Boolean
        get() = props["schema.history.internal"] == FileSchemaHistory::class.java.canonicalName

    fun withSchemaHistoryFile(schemaFilePath: Path): DebeziumPropertiesBuilder =
        if (expectsSchemaHistoryFile) {
            with(FileSchemaHistory.FILE_PATH.name(), schemaFilePath.toString())
        } else {
            this
        }

    fun withDebeziumName(name: String): DebeziumPropertiesBuilder = apply {
        with("name", name)
        // WARNING: Never change the value of this otherwise all the connectors would start
        // syncing from scratch.
        with("topic.prefix", sanitizeTopicPrefix(name))
    }

    fun withConnector(connectorClass: Class<out Connector>): DebeziumPropertiesBuilder =
        with("connector.class", connectorClass.canonicalName)

    fun withHeartbeats(heartbeatInterval: Duration): DebeziumPropertiesBuilder =
        with("heartbeat.interval.ms", heartbeatInterval.toMillis().toString())

    fun withDatabase(key: String, value: String): DebeziumPropertiesBuilder =
        with("database.$key", value)

    fun withDatabase(properties: Map<*, *>): DebeziumPropertiesBuilder = apply {
        for ((key, value) in properties) {
            withDatabase(key.toString(), value.toString())
        }
    }

    /** Tells Debezium which tables and columns we care about. */
    fun withStreams(streams: List<Stream>): DebeziumPropertiesBuilder {
        val tableIncludeList: List<String> =
            streams.map { Pattern.quote("${it.namespace}.${it.name}") }
        val columnIncludeList: List<String> =
            streams.zip(tableIncludeList).map { (stream: Stream, prefix: String) ->
                val suffix: String = stream.fields.joinToString("|") { Pattern.quote(it.id) }
                "$prefix\\.($suffix)"
            }
        return apply {
            with("table.include.list", joinIncludeList(tableIncludeList))
            with("column.include.list", joinIncludeList(columnIncludeList))
        }
    }

    fun withConverters(
        vararg converters: KClass<out RelationalColumnCustomConverter>
    ): DebeziumPropertiesBuilder = withConverters(*converters.map { it.java }.toTypedArray())

    fun withConverters(
        vararg converters: Class<out RelationalColumnCustomConverter>
    ): DebeziumPropertiesBuilder {
        val classByKey: Map<String, Class<out RelationalColumnCustomConverter>> =
            converters.associateBy {
                it.getDeclaredConstructor().newInstance().debeziumPropertiesKey
            }
        return apply {
            with("converters", classByKey.keys.joinToString(separator = ","))
            for ((key, converterClass) in classByKey) {
                with("${key}.type", converterClass.canonicalName)
            }
        }
    }

    companion object {

        fun joinIncludeList(includes: List<String>): String =
            includes.map { it.replace(",", "\\,") }.joinToString(",")

        fun sanitizeTopicPrefix(topicName: String): String =
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
