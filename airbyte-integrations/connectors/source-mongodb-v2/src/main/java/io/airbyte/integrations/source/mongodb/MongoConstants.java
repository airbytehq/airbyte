/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants;
import io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants;
import java.time.Duration;

public class MongoConstants {

  public static final String AUTH_SOURCE_CONFIGURATION_KEY = MongoDbDebeziumConstants.Configuration.AUTH_SOURCE_CONFIGURATION_KEY;
  public static final Integer CHECKPOINT_INTERVAL = DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS;
  public static final String CHECKPOINT_INTERVAL_CONFIGURATION_KEY = "sync_checkpoint_interval";
  public static final Duration CHECKPOINT_DURATION = DebeziumIteratorConstants.SYNC_CHECKPOINT_DURATION;
  public static final String COLLECTION_STATISTICS_COUNT_KEY = "count";
  public static final String COLLECTION_STATISTICS_STORAGE_SIZE_KEY = "size";
  public static final String CONNECTION_STRING_CONFIGURATION_KEY = MongoDbDebeziumConstants.Configuration.CONNECTION_STRING_CONFIGURATION_KEY;
  public static final String COUNT_KEY = "count";
  public static final String CREDENTIALS_PLACEHOLDER = MongoDbDebeziumConstants.Configuration.CREDENTIALS_PLACEHOLDER;
  public static final String DATABASE_CONFIGURATION_KEY = MongoDbDebeziumConstants.Configuration.DATABASE_CONFIGURATION_KEY;
  public static final String DATABASE_CONFIG_CONFIGURATION_KEY = MongoDbDebeziumConstants.Configuration.DATABASE_CONFIG_CONFIGURATION_KEY;
  public static final String DEFAULT_AUTH_SOURCE = "admin";
  public static final Integer DEFAULT_DISCOVER_SAMPLE_SIZE = 10000;
  public static final String DISCOVER_SAMPLE_SIZE_CONFIGURATION_KEY = "discover_sample_size";
  public static final String DRIVER_NAME = "Airbyte";
  public static final String ID_FIELD = "_id";
  public static final String IS_TEST_CONFIGURATION_KEY = "is_test";
  public static final String PASSWORD_CONFIGURATION_KEY = MongoDbDebeziumConstants.Configuration.PASSWORD_CONFIGURATION_KEY;
  public static final String QUEUE_SIZE_CONFIGURATION_KEY = "queue_size";
  public static final String STORAGE_STATS_KEY = "storageStats";
  public static final String USERNAME_CONFIGURATION_KEY = MongoDbDebeziumConstants.Configuration.USERNAME_CONFIGURATION_KEY;

  private MongoConstants() {}

}
