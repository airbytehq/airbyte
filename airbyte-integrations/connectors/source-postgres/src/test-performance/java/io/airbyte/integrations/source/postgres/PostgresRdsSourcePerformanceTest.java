/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.source.performancetest.AbstractSourcePerformanceTest;
import java.nio.file.Path;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.params.provider.Arguments;

public class PostgresRdsSourcePerformanceTest extends AbstractSourcePerformanceTest {

  private static final String PERFORMANCE_SECRET_CREDS = "secrets/performance-config.json";

  @Override
  protected String getImageName() {
    return "airbyte/source-postgres:dev";
  }

  @Override
  protected void setupDatabase(String dbName) {
    JsonNode plainConfig = Jsons.deserialize(IOs.readFile(Path.of(PERFORMANCE_SECRET_CREDS)));

    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "Standard")
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", plainConfig.get("host"))
        .put("port", plainConfig.get("port"))
        .put("database", plainConfig.get("database"))
        .put("username", plainConfig.get("username"))
        .put("password", plainConfig.get("password"))
        .put("ssl", true)
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
  @BeforeAll
  public static void beforeAll() {
    AbstractSourcePerformanceTest.testArgs = Stream.of(
        Arguments.of("test1000tables240columns200recordsDb", "test1000tables240columns200recordsDb", 200, 240, 1000),
        Arguments.of("newregular25tables50000records", "newregular25tables50000records", 50000, 8, 25),
        Arguments.of("newsmall1000tableswith10000rows", "newsmall1000tableswith10000rows", 10000, 8, 1000));
  }

}
