/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import io.debezium.config.Configuration
import io.debezium.embedded.KafkaConnectUtil
import java.util.*
import kotlin.String
import org.apache.kafka.connect.json.JsonConverter
import org.apache.kafka.connect.json.JsonConverterConfig
import org.apache.kafka.connect.runtime.WorkerConfig
import org.apache.kafka.connect.runtime.standalone.StandaloneConfig
import org.apache.kafka.connect.storage.FileOffsetBackingStore
import org.apache.kafka.connect.storage.OffsetStorageReaderImpl

/** Represents a utility class that assists with the parsing of Debezium offset state. */
interface DebeziumStateUtil {
    /**
     * Creates and starts a [FileOffsetBackingStore] that is used to store the tracked Debezium
     * offset state.
     *
     * @param properties The Debezium configuration properties for the selected Debezium connector.
     * @return A configured and started [FileOffsetBackingStore] instance.
     */
    fun getFileOffsetBackingStore(properties: Properties?): FileOffsetBackingStore? {
        val fileOffsetBackingStore = KafkaConnectUtil.fileOffsetBackingStore()
        val propertiesMap = Configuration.from(properties).asMap()
        propertiesMap[WorkerConfig.KEY_CONVERTER_CLASS_CONFIG] = JsonConverter::class.java.name
        propertiesMap[WorkerConfig.VALUE_CONVERTER_CLASS_CONFIG] = JsonConverter::class.java.name
        fileOffsetBackingStore.configure(StandaloneConfig(propertiesMap))
        fileOffsetBackingStore.start()
        return fileOffsetBackingStore
    }

    val keyConverter: JsonConverter?
        /**
         * Creates and returns a [JsonConverter] that can be used to parse keys in the Debezium
         * offset state storage.
         *
         * @return A [JsonConverter] for key conversion.
         */
        get() {
            val keyConverter = JsonConverter()
            keyConverter.configure(INTERNAL_CONVERTER_CONFIG, true)
            return keyConverter
        }

    /**
     * Creates and returns an [OffsetStorageReaderImpl] instance that can be used to load offset
     * state from the offset file storage.
     *
     * @param fileOffsetBackingStore The [FileOffsetBackingStore] that contains the offset state
     * saved to disk.
     * @param properties The Debezium configuration properties for the selected Debezium connector.
     * @return An [OffsetStorageReaderImpl] instance that can be used to load the offset state from
     * the offset file storage.
     */
    fun getOffsetStorageReader(
        fileOffsetBackingStore: FileOffsetBackingStore?,
        properties: Properties
    ): OffsetStorageReaderImpl? {
        return OffsetStorageReaderImpl(
            fileOffsetBackingStore,
            properties.getProperty(CONNECTOR_NAME_PROPERTY),
            keyConverter,
            valueConverter
        )
    }

    val valueConverter: JsonConverter?
        /**
         * Creates and returns a [JsonConverter] that can be used to parse values in the Debezium
         * offset state storage.
         *
         * @return A [JsonConverter] for value conversion.
         */
        get() {
            val valueConverter = JsonConverter()
            valueConverter.configure(INTERNAL_CONVERTER_CONFIG, false)
            return valueConverter
        }

    companion object {
        /**
         * The name of the Debezium property that contains the unique name for the Debezium
         * connector.
         */
        const val CONNECTOR_NAME_PROPERTY: String = "name"

        /** Configuration for offset state key/value converters. */
        val INTERNAL_CONVERTER_CONFIG: Map<String, String> =
            java.util.Map.of(JsonConverterConfig.SCHEMAS_ENABLE_CONFIG, false.toString())
    }
}
