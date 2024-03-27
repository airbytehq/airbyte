/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium.internals;

import io.debezium.config.Configuration;
import io.debezium.embedded.KafkaConnectUtil;
import java.util.Map;
import java.util.Properties;
import org.apache.kafka.connect.json.JsonConverter;
import org.apache.kafka.connect.json.JsonConverterConfig;
import org.apache.kafka.connect.runtime.WorkerConfig;
import org.apache.kafka.connect.runtime.standalone.StandaloneConfig;
import org.apache.kafka.connect.storage.FileOffsetBackingStore;
import org.apache.kafka.connect.storage.OffsetStorageReaderImpl;

/**
 * Represents a utility class that assists with the parsing of Debezium offset state.
 */
public interface DebeziumStateUtil {

  /**
   * The name of the Debezium property that contains the unique name for the Debezium connector.
   */
  String CONNECTOR_NAME_PROPERTY = "name";

  /**
   * Configuration for offset state key/value converters.
   */
  Map<String, String> INTERNAL_CONVERTER_CONFIG = Map.of(JsonConverterConfig.SCHEMAS_ENABLE_CONFIG, Boolean.FALSE.toString());

  /**
   * Creates and starts a {@link FileOffsetBackingStore} that is used to store the tracked Debezium
   * offset state.
   *
   * @param properties The Debezium configuration properties for the selected Debezium connector.
   * @return A configured and started {@link FileOffsetBackingStore} instance.
   */
  default FileOffsetBackingStore getFileOffsetBackingStore(final Properties properties) {
    final FileOffsetBackingStore fileOffsetBackingStore = KafkaConnectUtil.fileOffsetBackingStore();
    final Map<String, String> propertiesMap = Configuration.from(properties).asMap();
    propertiesMap.put(WorkerConfig.KEY_CONVERTER_CLASS_CONFIG, JsonConverter.class.getName());
    propertiesMap.put(WorkerConfig.VALUE_CONVERTER_CLASS_CONFIG, JsonConverter.class.getName());
    fileOffsetBackingStore.configure(new StandaloneConfig(propertiesMap));
    fileOffsetBackingStore.start();
    return fileOffsetBackingStore;
  }

  /**
   * Creates and returns a {@link JsonConverter} that can be used to parse keys in the Debezium offset
   * state storage.
   *
   * @return A {@link JsonConverter} for key conversion.
   */
  default JsonConverter getKeyConverter() {
    final JsonConverter keyConverter = new JsonConverter();
    keyConverter.configure(INTERNAL_CONVERTER_CONFIG, true);
    return keyConverter;
  }

  /**
   * Creates and returns an {@link OffsetStorageReaderImpl} instance that can be used to load offset
   * state from the offset file storage.
   *
   * @param fileOffsetBackingStore The {@link FileOffsetBackingStore} that contains the offset state
   *        saved to disk.
   * @param properties The Debezium configuration properties for the selected Debezium connector.
   * @return An {@link OffsetStorageReaderImpl} instance that can be used to load the offset state
   *         from the offset file storage.
   */
  default OffsetStorageReaderImpl getOffsetStorageReader(final FileOffsetBackingStore fileOffsetBackingStore, final Properties properties) {
    return new OffsetStorageReaderImpl(fileOffsetBackingStore, properties.getProperty(CONNECTOR_NAME_PROPERTY), getKeyConverter(),
        getValueConverter());
  }

  /**
   * Creates and returns a {@link JsonConverter} that can be used to parse values in the Debezium
   * offset state storage.
   *
   * @return A {@link JsonConverter} for value conversion.
   */
  default JsonConverter getValueConverter() {
    final JsonConverter valueConverter = new JsonConverter();
    valueConverter.configure(INTERNAL_CONVERTER_CONFIG, false);
    return valueConverter;
  }

}
