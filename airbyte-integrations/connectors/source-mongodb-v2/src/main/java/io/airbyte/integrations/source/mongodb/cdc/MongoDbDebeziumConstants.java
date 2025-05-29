/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import io.debezium.connector.mongodb.SourceInfo;

/**
 * A collection of constants for use with the Debezium MongoDB Connector.
 */
public class MongoDbDebeziumConstants {

  /**
   * Constants for Debezium Source Event data.
   */
  public static class ChangeEvent {

    public static final String SOURCE = "source";
    public static final String SOURCE_COLLECTION = SourceInfo.COLLECTION;
    public static final String SOURCE_DB = "db";
    public static final String SOURCE_ORDER = SourceInfo.ORDER;
    public static final String SOURCE_RESUME_TOKEN = "resume_token";
    public static final String SOURCE_SECONDS = SourceInfo.TIMESTAMP;
    public static final String SOURCE_TIMESTAMP_MS = "ts_ms";

  }

  /**
   * Constants for the configuration of the MongoDB connector. These constants represent the
   * configuration values that are to be mapped to the Debezium configuration.
   */
  public static class Configuration {

    public static final String AUTH_SOURCE_CONFIGURATION_KEY = "auth_source";
    public static final String CONNECTION_STRING_CONFIGURATION_KEY = "connection_string";
    public static final String CREDENTIALS_PLACEHOLDER = "<username>:<password>@";
    public static final String DATABASE_CONFIGURATION_KEY = "database";
    public static final String DATABASE_CONFIG_CONFIGURATION_KEY = "database_config";
    public static final String PASSWORD_CONFIGURATION_KEY = "password";
    public static final String USERNAME_CONFIGURATION_KEY = "username";
    public static final String SCHEMA_ENFORCED_CONFIGURATION_KEY = "schema_enforced";
    public static final String SCHEMALESS_MODE_DATA_FIELD = "data";

  }

  /**
   * Constants for Debezium Offset State storage.
   */
  public static class OffsetState {

    // public static final String KEY_REPLICA_SET = SourceInfo.REPLICA_SET_NAME;
    public static final String KEY_SERVER_ID = "server_id";
    public static final String VALUE_INCREMENT = SourceInfo.ORDER;
    public static final String VALUE_RESUME_TOKEN = "resume_token";
    public static final String VALUE_SECONDS = SourceInfo.TIMESTAMP;
    public static final String VALUE_TRANSACTION_ID = "transaction_id";

  }

  private MongoDbDebeziumConstants() {}

}
