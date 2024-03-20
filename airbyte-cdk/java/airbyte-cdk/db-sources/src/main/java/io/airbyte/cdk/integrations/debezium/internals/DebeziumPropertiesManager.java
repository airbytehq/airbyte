/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.debezium.spi.common.ReplacementFunction;
import java.util.Optional;
import java.util.Properties;

public abstract class DebeziumPropertiesManager {

  private static final String BYTE_VALUE_256_MB = Integer.toString(256 * 1024 * 1024);

  public static final String NAME_KEY = "name";
  public static final String TOPIC_PREFIX_KEY = "topic.prefix";

  private final JsonNode config;
  private final Properties properties;
  private final ConfiguredAirbyteCatalog catalog;

  public DebeziumPropertiesManager(final Properties properties,
                                   final JsonNode config,
                                   final ConfiguredAirbyteCatalog catalog) {
    this.properties = properties;
    this.config = config;
    this.catalog = catalog;
  }

  public Properties getDebeziumProperties(final AirbyteFileOffsetBackingStore offsetManager) {
    return getDebeziumProperties(offsetManager, Optional.empty());
  }

  public Properties getDebeziumProperties(
                                          final AirbyteFileOffsetBackingStore offsetManager,
                                          final Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager) {
    final Properties props = new Properties();
    props.putAll(properties);

    // debezium engine configuration
    offsetManager.setDebeziumProperties(props);
    // default values from debezium CommonConnectorConfig
    props.setProperty("max.batch.size", "2048");
    props.setProperty("max.queue.size", "8192");

    props.setProperty("errors.max.retries", "5");
    // This property must be strictly less than errors.retry.delay.max.ms
    // (https://github.com/debezium/debezium/blob/bcc7d49519a4f07d123c616cfa45cd6268def0b9/debezium-core/src/main/java/io/debezium/util/DelayStrategy.java#L135)
    props.setProperty("errors.retry.delay.initial.ms", "299");
    props.setProperty("errors.retry.delay.max.ms", "300");

    schemaHistoryManager.ifPresent(m -> m.setDebeziumProperties(props));

    // https://debezium.io/documentation/reference/2.2/configuration/avro.html
    props.setProperty("key.converter.schemas.enable", "false");
    props.setProperty("value.converter.schemas.enable", "false");

    // debezium names
    props.setProperty(NAME_KEY, getName(config));

    // connection configuration
    props.putAll(getConnectionConfiguration(config));

    // By default "decimal.handing.mode=precise" which's caused returning this value as a binary.
    // The "double" type may cause a loss of precision, so set Debezium's config to store it as a String
    // explicitly in its Kafka messages for more details see:
    // https://debezium.io/documentation/reference/2.2/connectors/postgresql.html#postgresql-decimal-types
    // https://debezium.io/documentation/faq/#how_to_retrieve_decimal_field_from_binary_representation
    props.setProperty("decimal.handling.mode", "string");

    // https://debezium.io/documentation/reference/2.2/connectors/postgresql.html#postgresql-property-max-queue-size-in-bytes
    props.setProperty("max.queue.size.in.bytes", BYTE_VALUE_256_MB);

    // WARNING : Never change the value of this otherwise all the connectors would start syncing from
    // scratch.
    props.setProperty(TOPIC_PREFIX_KEY, sanitizeTopicPrefix(getName(config)));
    // https://issues.redhat.com/browse/DBZ-7635
    // https://cwiki.apache.org/confluence/display/KAFKA/KIP-581%3A+Value+of+optional+null+field+which+has+default+value
    // A null value in a column with default value won't be generated correctly in CDC unless we set the
    // following
    props.setProperty("value.converter.replace.null.with.default", "false");
    // includes
    props.putAll(getIncludeConfiguration(catalog, config));

    return props;
  }

  public static String sanitizeTopicPrefix(final String topicName) {
    StringBuilder sanitizedNameBuilder = new StringBuilder(topicName.length());
    boolean changed = false;

    for (int i = 0; i < topicName.length(); ++i) {
      char c = topicName.charAt(i);
      if (isValidCharacter(c)) {
        sanitizedNameBuilder.append(c);
      } else {
        sanitizedNameBuilder.append(ReplacementFunction.UNDERSCORE_REPLACEMENT.replace(c));
        changed = true;
      }
    }

    if (changed) {
      return sanitizedNameBuilder.toString();
    } else {
      return topicName;
    }
  }

  // We need to keep the validation rule the same as debezium engine, which is defined here:
  // https://github.com/debezium/debezium/blob/c51ef3099a688efb41204702d3aa6d4722bb4825/debezium-core/src/main/java/io/debezium/schema/AbstractTopicNamingStrategy.java#L178
  private static boolean isValidCharacter(char c) {
    return c == '.' || c == '_' || c == '-' || c >= 'A' && c <= 'Z' || c >= 'a' && c <= 'z' || c >= '0' && c <= '9';
  }

  protected abstract Properties getConnectionConfiguration(final JsonNode config);

  protected abstract String getName(final JsonNode config);

  protected abstract Properties getIncludeConfiguration(final ConfiguredAirbyteCatalog catalog, final JsonNode config);

}
