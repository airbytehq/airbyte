/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.singlestore;

import static org.testcontainers.shaded.org.hamcrest.MatcherAssert.assertThat;
import static org.testcontainers.shaded.org.hamcrest.Matchers.containsInAnyOrder;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.DateTimeConverter;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.singlestore.SingleStoreTestDatabase.BaseImage;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.function.Function;
import java.util.function.IntFunction;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;

@Order(1)
public class SingleStoreSourceOperationsTest {

  private final SingleStoreSourceOperations sqlSourceOperations = new SingleStoreSourceOperations();

  @Test
  public void varcharAsCursor() throws SQLException {
    testImpl("VARCHAR(30)", i -> "test" + i, v -> v, v -> v, SingleStoreType.VARCHAR, "test1");
  }

  @Test
  public void dateColumnAsCursor() throws SQLException {
    testImpl("DATE", i -> LocalDate.of(2019, 1, i), DateTimeConverter::convertToDate,
        LocalDate::toString, SingleStoreType.DATE,
        DateTimeConverter.convertToDate(LocalDate.of(2019, 1, 1)));
  }

  @Test
  public void timeColumnAsCursor() throws SQLException {
    testImpl("TIME", i -> "20:0" + i + ":00", i -> i,
        i -> i, SingleStoreType.TIME,
        "20:01:00");
  }

  @Test
  public void dateTimeColumnAsCursor() throws SQLException {
    testImpl("DATETIME", i -> LocalDateTime.of(2019, i, 20, 3, 0, 0),
        DateTimeConverter::convertToTimestamp, LocalDateTime::toString, SingleStoreType.DATETIME,
        DateTimeConverter.convertToTimestamp(LocalDateTime.of(2019, 1, 20, 3, 0, 0)));
  }

  @Test
  public void timeStampColumnAsCursor() throws SQLException {
    testImpl("TIMESTAMP", i -> LocalDateTime.of(2019, i, 20, 3, 0, 0),
        DateTimeConverter::convertToTimestamp, LocalDateTime::toString, SingleStoreType.DATETIME,
        DateTimeConverter.convertToTimestamp(LocalDateTime.of(2019, 1, 20, 3, 0, 0)));
    testImpl("TIMESTAMP(6)", i -> LocalDateTime.of(2019, i, 20, 3, 0, 0),
        DateTimeConverter::convertToTimestamp, LocalDateTime::toString, SingleStoreType.DATETIME,
        DateTimeConverter.convertToTimestamp(LocalDateTime.of(2019, 1, 20, 3, 0, 0)));
  }

  private <T> void testImpl(final String sqlType,
                            IntFunction<T> recordBuilder,
                            Function<T, String> airbyteRecordStringifier,
                            Function<T, String> sqlRecordStringifier,
                            SingleStoreType singlestoreType,
                            String initialCursorFieldValue)
      throws SQLException {
    final String cursorColumn = "cursor_column";
    try (final var testdb = SingleStoreTestDatabase.in(BaseImage.SINGLESTORE_DEV)
        .with("CREATE TABLE cursor_table (id INTEGER PRIMARY KEY, %s %s);", cursorColumn,
            sqlType)) {
      final List<JsonNode> expectedRecords = new ArrayList<>();
      for (int i = 1; i <= 4; i++) {
        final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
        jsonNode.put("id", i);
        final T cursorValue = recordBuilder.apply(i);
        jsonNode.put("cursor_column", airbyteRecordStringifier.apply(cursorValue));
        testdb.with("INSERT INTO cursor_table VALUES (%d, '%s');", i,
            sqlRecordStringifier.apply(cursorValue));
        if (i >= 2) {
          expectedRecords.add(jsonNode);
        }
      }
      try (final Connection connection = testdb.getContainer().createConnection("")) {
        final PreparedStatement preparedStatement = connection.prepareStatement(
            "SELECT * FROM " + testdb.getDatabaseName() + ".cursor_table WHERE " + cursorColumn
                + " > ?");
        sqlSourceOperations.setCursorField(preparedStatement, 1, singlestoreType,
            initialCursorFieldValue);
        final List<JsonNode> actualRecords = new ArrayList<>();
        try (final ResultSet resultSet = preparedStatement.executeQuery()) {
          while (resultSet.next()) {
            final ObjectNode jsonNode = (ObjectNode) Jsons.jsonNode(Collections.emptyMap());
            for (int i = 1; i <= resultSet.getMetaData().getColumnCount(); i++) {
              sqlSourceOperations.copyToJsonField(resultSet, i, jsonNode);
            }
            actualRecords.add(jsonNode);
          }
        }
        assertThat(actualRecords, containsInAnyOrder(expectedRecords.toArray()));
      }
    }
  }

}
