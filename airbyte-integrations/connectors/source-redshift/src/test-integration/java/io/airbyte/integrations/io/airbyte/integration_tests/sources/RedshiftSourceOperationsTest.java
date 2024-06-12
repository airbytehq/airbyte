/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.source.jdbc.JdbcDataSourceUtils;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.redshift.RedshiftSource;
import io.airbyte.integrations.source.redshift.RedshiftSourceOperations;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeFormatterBuilder;
import java.util.List;
import javax.sql.DataSource;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class RedshiftSourceOperationsTest {

  private static final Duration CONNECTION_TIMEOUT = Duration.ofSeconds(60);
  private JdbcDatabase database;

  @BeforeEach
  void setup() {
    final JsonNode config = Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));

    final DataSource dataSource = DataSourceFactory.create(
        config.get("username").asText(),
        config.get("password").asText(),
        DatabaseDriver.REDSHIFT.getDriverClassName(),
        RedshiftSource.getJdbcUrl(config),
        JdbcDataSourceUtils.getConnectionProperties(config),
        CONNECTION_TIMEOUT);
    database = new DefaultJdbcDatabase(dataSource, new RedshiftSourceOperations());
  }

  @Test
  void testTimestampWithTimezone() throws SQLException {
    // CURRENT_TIMESTAMP is converted to a string by queryJsons.
    // CAST(CURRENT_TIMESTAMP AS VARCHAR) does the timestamp -> string conversion on the server side.
    // If queryJsons is implemented correctly, both timestamps should be the same.
    final List<JsonNode> result = database.queryJsons("SELECT CURRENT_TIMESTAMP, CAST(CURRENT_TIMESTAMP AS VARCHAR)");

    final Instant clientSideParse = Instant.parse(result.get(0).get("timestamptz").asText());
    // Redshift's default timestamp format is "2023-11-17 17:50:36.746606+00", which Instant.parse()
    // can't handle. Build a custom datetime formatter.
    // (Redshift supports server-side timestamp formatting, but it doesn't provide a way to force
    // HH:MM offsets, which are required by Instant.parse)
    final Instant serverSideParse = new DateTimeFormatterBuilder()
        .append(DateTimeFormatter.ISO_DATE)
        .appendLiteral(' ')
        .append(DateTimeFormatter.ISO_LOCAL_TIME)
        // "X" represents a +/-HH offset
        .appendPattern("X")
        .toFormatter()
        .parse(result.get(0).get("varchar").asText(), Instant::from);
    assertEquals(serverSideParse, clientSideParse);
  }

}
