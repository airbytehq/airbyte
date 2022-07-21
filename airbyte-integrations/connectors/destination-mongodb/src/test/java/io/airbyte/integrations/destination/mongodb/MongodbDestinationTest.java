/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.params.provider.Arguments.arguments;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

class MongodbDestinationTest {

  private static final JsonNode standaloneConfig = Jsons.jsonNode(ImmutableMap.builder()
      .put("instance", "standalone")
      .put(JdbcUtils.HOST_KEY, "localhost")
      .put(JdbcUtils.PORT_KEY, 27017)
      .put(JdbcUtils.TLS_KEY, false)
      .build());
  private static final JsonNode standaloneTlsConfig = Jsons.jsonNode(ImmutableMap.builder()
      .put("instance", "standalone")
      .put(JdbcUtils.HOST_KEY, "localhost")
      .put(JdbcUtils.PORT_KEY, 27017)
      .put(JdbcUtils.TLS_KEY, true)
      .build());
  private static final JsonNode replicaWithNameConfig = Jsons.jsonNode(ImmutableMap.builder()
      .put("instance", "replica")
      .put("server_addresses", "localhost1:27017,localhost2:27017")
      .put("replica_set", "replicaName")
      .build());
  private static final JsonNode replicaWithoutNameConfig = Jsons.jsonNode(ImmutableMap.builder()
      .put("instance", "replica")
      .put("server_addresses", "localhost1:27017,localhost2:27017")
      .build());
  private static final JsonNode atlasConfig = Jsons.jsonNode(ImmutableMap.builder()
      .put("instance", "atlas")
      .put("cluster_url", "cluster.shard.url")
      .build());

  private static final JsonNode authConfig = Jsons.jsonNode(ImmutableMap.builder()
      .put("authorization", "login/password")
      .put(JdbcUtils.USERNAME_KEY, "user")
      .put(JdbcUtils.PASSWORD_KEY, "pass")
      .build());
  private static final JsonNode noneAuthConfig = Jsons.jsonNode(ImmutableMap.builder()
      .put("authorization", "none")
      .build());

  private MongodbDestination mongodbDestination;

  @BeforeEach
  void setUp() {
    mongodbDestination = new MongodbDestination();
  }

  @ParameterizedTest
  @MethodSource("configAndDataProvider")
  void testGetConnectionString(final JsonNode config, final String expected) {
    final var actual = mongodbDestination.getConnectionString(config);
    assertEquals(expected, actual);
  }

  private static Stream<Arguments> configAndDataProvider() {
    return Stream.of(
        arguments(Jsons.jsonNode(ImmutableMap.builder()
            .put("instance_type", standaloneConfig)
            .put(JdbcUtils.DATABASE_KEY, "dbName")
            .put("auth_type", authConfig).build()),
            "mongodb://user:pass@localhost:27017/dbName?authSource=admin&ssl=false"),
        arguments(Jsons.jsonNode(ImmutableMap.builder()
            .put("instance_type", standaloneTlsConfig)
            .put(JdbcUtils.DATABASE_KEY, "dbName")
            .put("auth_type", noneAuthConfig).build()),
            "mongodb://localhost:27017/dbName?authSource=admin&ssl=true"),
        arguments(Jsons.jsonNode(ImmutableMap.builder()
            .put("instance_type", replicaWithNameConfig)
            .put(JdbcUtils.DATABASE_KEY, "dbName")
            .put("auth_type", authConfig).build()),
            "mongodb://user:pass@localhost1:27017,localhost2:27017/dbName?authSource=admin&directConnection=false&ssl=true&replicaSet=replicaName"),
        arguments(Jsons.jsonNode(ImmutableMap.builder()
            .put("instance_type", replicaWithoutNameConfig)
            .put(JdbcUtils.DATABASE_KEY, "dbName")
            .put("auth_type", noneAuthConfig).build()),
            "mongodb://localhost1:27017,localhost2:27017/dbName?authSource=admin&directConnection=false&ssl=true"),
        arguments(Jsons.jsonNode(ImmutableMap.builder()
            .put("instance_type", atlasConfig)
            .put(JdbcUtils.DATABASE_KEY, "dbName")
            .put("auth_type", authConfig).build()),
            "mongodb+srv://user:pass@cluster.shard.url/dbName?retryWrites=true&w=majority&tls=true"),
        arguments(Jsons.jsonNode(ImmutableMap.builder()
            .put("instance_type", atlasConfig)
            .put(JdbcUtils.DATABASE_KEY, "dbName")
            .put("auth_type", noneAuthConfig).build()),
            "mongodb+srv://cluster.shard.url/dbName?retryWrites=true&w=majority&tls=true"),
        // older versions support
        arguments(Jsons.jsonNode(ImmutableMap.builder()
            .put(JdbcUtils.HOST_KEY, "localhost")
            .put(JdbcUtils.PORT_KEY, "27017")
            .put(JdbcUtils.DATABASE_KEY, "dbName")
            .put("auth_type", authConfig).build()),
            "mongodb://user:pass@localhost:27017/dbName?authSource=admin&ssl=false"),
        arguments(Jsons.jsonNode(ImmutableMap.builder()
            .put(JdbcUtils.HOST_KEY, "localhost")
            .put(JdbcUtils.PORT_KEY, "27017")
            .put(JdbcUtils.DATABASE_KEY, "dbName")
            .put("auth_type", noneAuthConfig).build()),
            "mongodb://localhost:27017/dbName?authSource=admin&ssl=false"));
  }

}
