/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcUtils;

public class MongoDbDestinationUtils {

  public static final String MONGODB_SERVER_URL = "mongodb://%s%s:%s/%s?authSource=admin&ssl=%s";
  public static final String MONGODB_CLUSTER_URL = "mongodb+srv://%s%s/%s?retryWrites=true&w=majority&tls=true";
  public static final String MONGODB_REPLICA_URL = "mongodb://%s%s/%s?authSource=admin&directConnection=false&ssl=true";
  public static final String INSTANCE_TYPE = "instance_type";
  public static final String INSTANCE = "instance";
  public static final String CLUSTER_URL = "cluster_url";
  public static final String SERVER_ADDRESSES = "server_addresses";
  public static final String REPLICA_SET = "replica_set";
  public static final String AUTH_TYPE = "auth_type";
  public static final String AUTHORIZATION = "authorization";
  public static final String LOGIN_AND_PASSWORD = "login/password";
  public static final String AIRBYTE_DATA_HASH = "_airbyte_data_hash";

  /**
   * Determines whether TLS/SSL should be enabled for a standalone instance of MongoDB.
   */
  public static boolean tlsEnabledForStandaloneInstance(final JsonNode config, final JsonNode instanceConfig) {
    return config.has(JdbcUtils.TLS_KEY) ? config.get(JdbcUtils.TLS_KEY).asBoolean()
        : (instanceConfig.has(JdbcUtils.TLS_KEY) ? instanceConfig.get(JdbcUtils.TLS_KEY).asBoolean() : true);
  }
  
}
