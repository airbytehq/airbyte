/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.integrations.destination.redshift.RedshiftSQLNameTransformer;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.io.IOException;
import java.time.Instant;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import java.util.Random;
import org.jooq.DSLContext;
import org.jooq.conf.Settings;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class RedshiftSqlGeneratorTest {

  private static final Random RANDOM = new Random();

  private static final RedshiftSqlGenerator redshiftSqlGenerator = new RedshiftSqlGenerator(new RedshiftSQLNameTransformer(), false) {

    // Override only for tests to print formatted SQL. The actual implementation should use unformatted
    // to save bytes.
    @Override
    protected DSLContext getDslContext() {
      return DSL.using(getDialect(), new Settings().withRenderFormatted(true));
    }

  };

  private StreamId streamId;

  private StreamConfig incrementalDedupStream;

  private StreamConfig incrementalAppendStream;

  @BeforeEach
  public void setup() {
    streamId = new StreamId("test_schema", "users_final", "test_schema", "users_raw", "test_schema", "users_final");
    final ColumnId id1 = redshiftSqlGenerator.buildColumnId("id1");
    final ColumnId id2 = redshiftSqlGenerator.buildColumnId("id2");
    final List<ColumnId> primaryKey = List.of(id1, id2);
    final ColumnId cursor = redshiftSqlGenerator.buildColumnId("updated_at");

    final LinkedHashMap<ColumnId, AirbyteType> columns = new LinkedHashMap<>();
    columns.put(id1, AirbyteProtocolType.INTEGER);
    columns.put(id2, AirbyteProtocolType.INTEGER);
    columns.put(cursor, AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
    columns.put(redshiftSqlGenerator.buildColumnId("struct"), new Struct(new LinkedHashMap<>()));
    columns.put(redshiftSqlGenerator.buildColumnId("array"), new Array(AirbyteProtocolType.UNKNOWN));
    columns.put(redshiftSqlGenerator.buildColumnId("string"), AirbyteProtocolType.STRING);
    columns.put(redshiftSqlGenerator.buildColumnId("number"), AirbyteProtocolType.NUMBER);
    columns.put(redshiftSqlGenerator.buildColumnId("integer"), AirbyteProtocolType.INTEGER);
    columns.put(redshiftSqlGenerator.buildColumnId("boolean"), AirbyteProtocolType.BOOLEAN);
    columns.put(redshiftSqlGenerator.buildColumnId("timestamp_with_timezone"), AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
    columns.put(redshiftSqlGenerator.buildColumnId("timestamp_without_timezone"), AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE);
    columns.put(redshiftSqlGenerator.buildColumnId("time_with_timezone"), AirbyteProtocolType.TIME_WITH_TIMEZONE);
    columns.put(redshiftSqlGenerator.buildColumnId("time_without_timezone"), AirbyteProtocolType.TIME_WITHOUT_TIMEZONE);
    columns.put(redshiftSqlGenerator.buildColumnId("date"), AirbyteProtocolType.DATE);
    columns.put(redshiftSqlGenerator.buildColumnId("unknown"), AirbyteProtocolType.UNKNOWN);
    columns.put(redshiftSqlGenerator.buildColumnId("_ab_cdc_deleted_at"), AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
    incrementalDedupStream = new StreamConfig(
        streamId,
        DestinationSyncMode.APPEND_DEDUP,
        primaryKey,
        Optional.of(cursor),
        columns,
        0,
        0,
        0);
    incrementalAppendStream = new StreamConfig(
        streamId,
        DestinationSyncMode.APPEND,
        primaryKey,
        Optional.of(cursor),
        columns, 0, 0, 0);
  }

  @Test
  public void testTypingAndDeduping() throws IOException {
    final String expectedSql = MoreResources.readResource("typing_deduping_with_cdc.sql");
    final Sql generatedSql =
        redshiftSqlGenerator.updateTable(incrementalDedupStream, "unittest", Optional.of(Instant.parse("2023-02-15T18:35:24.00Z")), false);
    final List<String> expectedSqlLines = Arrays.stream(expectedSql.split("\n")).map(String::trim).toList();
    final List<String> generatedSqlLines = generatedSql.asSqlStrings("BEGIN", "COMMIT").stream()
        .flatMap(statement -> Arrays.stream(statement.split("\n")))
        .map(String::trim)
        .filter(line -> !line.isEmpty())
        .toList();
    assertEquals(expectedSqlLines.size(), generatedSqlLines.size());
    for (int i = 0; i < expectedSqlLines.size(); i++) {
      assertEquals(expectedSqlLines.get(i), generatedSqlLines.get(i));
    }
  }

  @Test
  public void test2000ColumnSql() {
    final ColumnId id1 = redshiftSqlGenerator.buildColumnId("id1");
    final ColumnId id2 = redshiftSqlGenerator.buildColumnId("id2");
    final List<ColumnId> primaryKey = List.of(id1, id2);
    final ColumnId cursor = redshiftSqlGenerator.buildColumnId("updated_at");

    final LinkedHashMap<ColumnId, AirbyteType> columns = new LinkedHashMap<>();
    columns.put(id1, AirbyteProtocolType.INTEGER);
    columns.put(id2, AirbyteProtocolType.INTEGER);
    columns.put(cursor, AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);

    for (int i = 0; i < 2000; i++) {
      final String columnName = RANDOM
          .ints('a', 'z' + 1)
          .limit(15)
          .collect(StringBuilder::new, StringBuilder::appendCodePoint, StringBuilder::append)
          .toString();
      columns.put(redshiftSqlGenerator.buildColumnId(columnName), AirbyteProtocolType.STRING);
    }
    final Sql generatedSql = redshiftSqlGenerator.updateTable(new StreamConfig(
        streamId,
        DestinationSyncMode.APPEND_DEDUP,
        primaryKey,
        Optional.of(cursor),
        columns, 0, 0, 0), "unittest", Optional.of(Instant.parse("2023-02-15T18:35:24.00Z")), false);
    // This should not throw an exception.
    assertFalse(generatedSql.transactions().isEmpty());
  }

}
