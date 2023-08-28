/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal;

import io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants;

public class MongoConstants {

  public static final String AUTH_SOURCE_CONFIGURATION_KEY = MongoDbDebeziumConstants.Configuration.AUTH_SOURCE_CONFIGURATION_KEY;
  public static final Integer CHECKPOINT_INTERVAL = 1000;
  public static final String CONNECTION_STRING_CONFIGURATION_KEY = MongoDbDebeziumConstants.Configuration.CONNECTION_STRING_CONFIGURATION_KEY;
  public static final String DATABASE_CONFIGURATION_KEY = MongoDbDebeziumConstants.Configuration.DATABASE_CONFIGURATION_KEY;
  public static final String ID_FIELD = "_id";
  public static final String PASSWORD_CONFIGURATION_KEY = MongoDbDebeziumConstants.Configuration.PASSWORD_CONFIGURATION_KEY;
  public static final String REPLICA_SET_CONFIGURATION_KEY = MongoDbDebeziumConstants.Configuration.REPLICA_SET_CONFIGURATION_KEY;
  public static final String USER_CONFIGURATION_KEY = MongoDbDebeziumConstants.Configuration.USER_CONFIGURATION_KEY;

  private MongoConstants() {}

}
