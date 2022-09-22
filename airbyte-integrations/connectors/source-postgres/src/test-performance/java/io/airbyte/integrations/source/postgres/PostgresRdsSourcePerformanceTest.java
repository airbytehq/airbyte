/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.standardtest.source.performancetest.AbstractSourcePerformanceTest;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Stream;
import org.junit.jupiter.params.provider.Arguments;

public class PostgresRdsSourcePerformanceTest extends AbstractSourcePerformanceTest {

  private static final String PERFORMANCE_SECRET_CREDS = "secrets/performance-config.json";
  private static final List<String> SCHEMAS = List.of("t1000_c240_r200",
      "t25_c8_r50k_s10kb", "t1000_c8_r10k_s500b");

  @Override
  protected String getImageName() {
    return "airbyte/source-postgres:dev";
  }

  @Override
  protected void setupDatabase(final String dbName) {
    final JsonNode plainConfig = Jsons.deserialize(IOs.readFile(Path.of(PERFORMANCE_SECRET_CREDS)));

    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "Standard")
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, plainConfig.get(JdbcUtils.HOST_KEY))
        .put(JdbcUtils.PORT_KEY, plainConfig.get(JdbcUtils.PORT_KEY))
        .put(JdbcUtils.DATABASE_KEY, dbName)
        .put(JdbcUtils.SCHEMAS_KEY, List.of(dbName))
        .put(JdbcUtils.USERNAME_KEY, plainConfig.get(JdbcUtils.USERNAME_KEY))
        .put(JdbcUtils.PASSWORD_KEY, plainConfig.get(JdbcUtils.PASSWORD_KEY))
        .put(JdbcUtils.SSL_KEY, true)
        .put("replication_method", replicationMethod)
        .build());
  }

  /**
   * This is a data provider for performance tests, Each argument's group would be ran as a separate
   * test. 1st arg - a name of DB that will be used in jdbc connection string. 2nd arg - a schemaName
   * that will be used as a NameSpace in Configured Airbyte Catalog. 3rd arg - a number of expected
   * records retrieved in each stream. 4th arg - a number of columns in each stream\table that will be
   * use for Airbyte Cataloq configuration 5th arg - a number of streams to read in configured airbyte
   * Catalog. Each stream\table in DB should be names like "test_0", "test_1",..., test_n.
   */
  @Override
  protected Stream<Arguments> provideParameters() {
    return Stream.of(
        Arguments.of(SCHEMAS.get(0), SCHEMAS.get(0), 200, 240, 1000),
        Arguments.of(SCHEMAS.get(1), SCHEMAS.get(1), 50000, 8, 25),
        Arguments.of(SCHEMAS.get(2), SCHEMAS.get(2), 10000, 8, 1000));
  }

}
