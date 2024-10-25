/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.debezium.spi.common.ReplacementFunction
import java.util.*

abstract class DebeziumPropertiesManager(
    private val properties: Properties,
    private val config: JsonNode,
    private val catalog: ConfiguredAirbyteCatalog
) {
    fun getDebeziumProperties(offsetManager: AirbyteFileOffsetBackingStore): Properties {
        return getDebeziumProperties(offsetManager, Optional.empty())
    }

    fun getDebeziumProperties(
        offsetManager: AirbyteFileOffsetBackingStore,
        schemaHistoryManager: Optional<AirbyteSchemaHistoryStorage>
    ): Properties {
        val props = Properties()
        props.putAll(properties)

        // debezium engine configuration
        offsetManager.setDebeziumProperties(props)
        // default values from debezium CommonConnectorConfig
        props.setProperty("max.batch.size", "2048")
        props.setProperty("max.queue.size", "8192")

        props.setProperty("errors.max.retries", "0")
        // This property must be strictly less than errors.retry.delay.max.ms
        // (https://github.com/debezium/debezium/blob/bcc7d49519a4f07d123c616cfa45cd6268def0b9/debezium-core/src/main/java/io/debezium/util/DelayStrategy.java#L135)
        props.setProperty("errors.retry.delay.initial.ms", "299")
        props.setProperty("errors.retry.delay.max.ms", "300")

        schemaHistoryManager.ifPresent { m: AirbyteSchemaHistoryStorage ->
            m.setDebeziumProperties(props)
        }

        // https://debezium.io/documentation/reference/2.2/configuration/avro.html
        props.setProperty("key.converter.schemas.enable", "false")
        props.setProperty("value.converter.schemas.enable", "false")

        // debezium names
        props.setProperty(NAME_KEY, getName(config))

        // connection configuration
        props.putAll(getConnectionConfiguration(config))

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
        props.setProperty(TOPIC_PREFIX_KEY, sanitizeTopicPrefix(getName(config)))
        // https://issues.redhat.com/browse/DBZ-7635
        // https://cwiki.apache.org/confluence/display/KAFKA/KIP-581%3A+Value+of+optional+null+field+which+has+default+value
        // A null value in a column with default value won't be generated correctly in CDC unless we
        // set the
        // following
        props.setProperty("value.converter.replace.null.with.default", "false")
        // includes
        props.putAll(getIncludeConfiguration(catalog, config))

        return props
    }

    protected abstract fun getConnectionConfiguration(config: JsonNode): Properties

    protected abstract fun getName(config: JsonNode): String

    protected abstract fun getIncludeConfiguration(
        catalog: ConfiguredAirbyteCatalog,
        config: JsonNode?
    ): Properties

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
                        ReplacementFunction.UNDERSCORE_REPLACEMENT.replace(c)
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
    }
}
