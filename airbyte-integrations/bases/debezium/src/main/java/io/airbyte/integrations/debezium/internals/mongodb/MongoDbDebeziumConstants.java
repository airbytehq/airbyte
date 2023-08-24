/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.mongodb;

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

    public static final String SOURCE_ORDER = SourceInfo.ORDER;

    public static final String SOURCE_RESUME_TOKEN = "resume_token";

    public static final String SOURCE_SECONDS = SourceInfo.TIMESTAMP;

    public static final String SOURCE_TIMESTAMP_MS = "ts_ms";

  }

  /**
   * Constants for Debezium Offset State storage.
   */
  public static class OffsetState {

    public static final String KEY_REPLICA_SET = SourceInfo.REPLICA_SET_NAME;

    public static final String KEY_SERVER_ID = SourceInfo.SERVER_ID_KEY;

    public static final String VALUE_INCREMENT = SourceInfo.ORDER;

    public static final String VALUE_RESUME_TOKEN = "resume_token";

    public static final String VALUE_SECONDS = SourceInfo.TIMESTAMP;

    public static final String VALUE_TRANSACTION_ID = "transaction_id";

  }

}
