/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.mongodb;

/**
 * A collection of constants for use with the Debezium MongoDB Connector.
 */
public class MongoDbDebeziumConstants {

  /**
   * Constants for Debezium Offset State storage.
   */
  public static class OffsetState {

    public static final String KEY_REPLICA_SET = "rs";

    public static final String KEY_SERVER_ID = "server_id";

    public static final String VALUE_INCREMENT = "ord";

    public static final String VALUE_RESUME_TOKEN = "resume_token";

    public static final String VALUE_SECONDS = "sec";

    public static final String VALUE_TRANSACTION_ID = "transaction_id";

  }

}
