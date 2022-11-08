/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static org.bson.BsonType.DATE_TIME;
import static org.bson.BsonType.DECIMAL128;
import static org.bson.BsonType.DOCUMENT;
import static org.bson.BsonType.DOUBLE;
import static org.bson.BsonType.INT32;
import static org.bson.BsonType.INT64;
import static org.bson.BsonType.OBJECT_ID;
import static org.bson.BsonType.STRING;
import static org.bson.BsonType.TIMESTAMP;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcUtils;
import java.util.Set;
import org.bson.BsonType;

public final class MongoDbSourceUtils {

  private MongoDbSourceUtils() {}

  public static final String MONGODB_SERVER_URL = "mongodb://%s%s:%s/%s?authSource=%s&ssl=%s";
  public static final String MONGODB_CLUSTER_URL = "mongodb+srv://%s%s/%s?authSource=%s&retryWrites=true&w=majority&tls=true";
  public static final String MONGODB_REPLICA_URL = "mongodb://%s%s/%s?authSource=%s&directConnection=false&ssl=true";
  public static final String USER = "user";
  public static final String INSTANCE_TYPE = "instance_type";
  public static final String INSTANCE = "instance";
  public static final String CLUSTER_URL = "cluster_url";
  public static final String SERVER_ADDRESSES = "server_addresses";
  public static final String REPLICA_SET = "replica_set";
  public static final String AUTH_SOURCE = "auth_source";
  public static final String PRIMARY_KEY = "_id";
  public static final Set<BsonType> ALLOWED_CURSOR_TYPES = Set.of(DOUBLE, STRING, DOCUMENT, OBJECT_ID, DATE_TIME,
      INT32, TIMESTAMP, INT64, DECIMAL128);

  /**
   * Determines whether TLS/SSL should be enabled for a standalone instance of MongoDB.
   */
  public static boolean tlsEnabledForStandaloneInstance(final JsonNode config, final JsonNode instanceConfig) {
    return config.has(JdbcUtils.TLS_KEY) ? config.get(JdbcUtils.TLS_KEY).asBoolean()
        : (instanceConfig.has(JdbcUtils.TLS_KEY) ? instanceConfig.get(JdbcUtils.TLS_KEY).asBoolean() : true);
  }

}
