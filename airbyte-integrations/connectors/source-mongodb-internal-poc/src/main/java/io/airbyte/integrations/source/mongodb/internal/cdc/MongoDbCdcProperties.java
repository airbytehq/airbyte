/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.cdc;

import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.DATABASE_CONFIGURATION_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import java.time.Duration;
import java.util.Properties;
import java.util.Set;
import java.util.stream.Collectors;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumPropertiesManager;

/**
 * Defines MongoDB specific CDC configuration properties for Debezium.
 */
public class MongoDbCdcProperties {

  static final String CAPTURE_MODE_KEY = "capture.mode";
  static final String CAPTURE_MODE_VALUE = "change_streams_update_full";
  static final String CONNECTOR_CLASS_KEY = "connector.class";
  static final String CONNECTOR_CLASS_VALUE = "io.debezium.connector.mongodb.MongoDbConnector";
  static final String HEARTBEAT_FREQUENCY_MS = Long.toString(Duration.ofSeconds(10).toMillis());
  static final String HEARTBEAT_INTERVAL_KEY = "heartbeat.interval.ms";
  static final String SNAPSHOT_MODE_KEY = "snapshot.mode";
  static final String SNAPSHOT_MODE_VALUE = "initial";
  static final String FIELD_EXCLUDE_LIST_KEY = "field.exclude.list";

  public record CollectionAndField(String collection, String field) {}

  /**
   * Returns the common properties required to configure the Debezium MongoDB connector.
   *
   * @return The common Debezium CDC properties for the Debezium MongoDB connector.
   */
  public static Properties getDebeziumProperties(final JsonNode config, final Set<CollectionAndField> fieldsToExclude) {
    final Properties props = new Properties();

    props.setProperty(CONNECTOR_CLASS_KEY, CONNECTOR_CLASS_VALUE);
    props.setProperty(SNAPSHOT_MODE_KEY, SNAPSHOT_MODE_VALUE);
    props.setProperty(CAPTURE_MODE_KEY, CAPTURE_MODE_VALUE);
    props.setProperty(HEARTBEAT_INTERVAL_KEY, HEARTBEAT_FREQUENCY_MS);
    final String databaseName = config.get(DATABASE_CONFIGURATION_KEY).asText();

    /**
     * //https://debezium.io/documentation/reference/2.2/connectors/mongodb.html#mongodb-property-field-exclude-list
     *
     * This is not the best place to be setting this property. Ideally, we would be setting it in the
     * {@link MongoDbDebeziumPropertiesManager}, but it is not straightforward to do so since debezium
     * only allows to specify an exclude list of fields (as opposed to an include list). If/when debezium adds
     * support for an include list, we should move this property to {@link MongoDbDebeziumPropertiesManager}.
     */
    props.setProperty(FIELD_EXCLUDE_LIST_KEY, createFieldsToExcludeString(fieldsToExclude, databaseName));

    return props;
  }

  private static String createFieldsToExcludeString(final Set<CollectionAndField> fieldsToExclude, final String databaseName) {
    return fieldsToExclude.stream()
        .map(field -> databaseName + "." + field.collection() + "." + field.field())
        .collect(Collectors.joining(","));
  }
}
