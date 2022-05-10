/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.integrations.standardtest.source.performancetest.AbstractSourcePerformanceTest;
import java.nio.file.Path;
import java.util.Map;
import java.util.stream.Stream;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.params.provider.Arguments;

public class MySqlRdsSourcePerformanceSecretTest extends AbstractSourcePerformanceTest {

  private static final String PERFORMANCE_SECRET_CREDS = "secrets/performance-config.json";

  @Override
  protected String getImageName() {
    return "airbyte/source-mysql:dev";
  }

  @Override
  protected void setupDatabase(final String dbName) throws Exception {
    final JsonNode plainConfig = Jsons.deserialize(IOs.readFile(Path.of(PERFORMANCE_SECRET_CREDS)));

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", plainConfig.get("host"))
        .put("port", plainConfig.get("port"))
        .put("database", dbName)
        .put("username", plainConfig.get("username"))
        .put("password", plainConfig.get("password"))
        .put("replication_method", plainConfig.get("replication_method"))
        .build());

    try (final DSLContext dslContext = DSLContextFactory.create(
        config.get("username").asText(),
        config.get("password").asText(),
        DatabaseDriver.MYSQL.getDriverClassName(),
        String.format(DatabaseDriver.MYSQL.getUrlFormatString(),
            config.get("host").asText(),
            config.get("port").asInt(),
            config.get("database").asText()),
        SQLDialect.MYSQL,
        Map.of("zeroDateTimeBehavior", "convertToNull"))) {

      final Database database = new Database(dslContext);

      // It disable strict mode in the DB and allows to insert specific values.
      // For example, it's possible to insert date with zero values "2021-00-00"
      database.query(ctx -> ctx.execute("SET @@sql_mode=''"));
    }
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
        Arguments.of("t1000_c240_r200", "t1000_c240_r200", 200, 240, 1000),
        Arguments.of("t25_c8_r50k_s10kb", "t25_c8_r50k_s10kb", 50000, 8, 25),
        Arguments.of("t1000_c8_r10k_s500b", "t1000_c8_r10k_s500b", 10000, 8, 1000));
  }

}
