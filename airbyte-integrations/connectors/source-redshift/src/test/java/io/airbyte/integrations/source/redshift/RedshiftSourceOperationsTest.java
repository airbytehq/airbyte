/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.redshift;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.util.Calendar;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class RedshiftSourceOperationsTest {

  private RedshiftSourceOperations ops;
  private ResultSet resultSet;
  private ResultSetMetaData metadata;

  @BeforeEach
  void setUp() throws SQLException {
    ops = new RedshiftSourceOperations();
    resultSet = mock(ResultSet.class);
    metadata = mock(ResultSetMetaData.class);
    when(resultSet.getMetaData()).thenReturn(metadata);
  }

  @Test
  void testPutTimestampWithTimezoneDoesNotCallGetString() throws SQLException {
    // Reproduces the StackOverflowError scenario: the Redshift JDBC driver's
    // PGTimestamp.toString() triggers infinite recursion when getString() is
    // called on a timestamptz column. This test verifies that the fixed
    // implementation never calls getString().
    final OffsetDateTime expected = OffsetDateTime.of(2026, 6, 4, 5, 50, 52, 815018000, ZoneOffset.UTC);
    when(resultSet.getObject(eq(1), eq(OffsetDateTime.class))).thenReturn(expected);

    final ObjectNode node = (ObjectNode) Jsons.emptyObject();
    ops.putTimestampWithTimezone(node, "created_at", resultSet, 1);

    verify(resultSet, never()).getString(anyInt());
    verify(resultSet, never()).getString(any(String.class));

    assertFalse(node.isEmpty());
    assertTrue(node.get("created_at").asText().startsWith("2026-06-04T05:50:52"));
  }

  @Test
  void testPutTimestampWithTimezoneFallsBackWhenGetObjectFails() throws SQLException {
    // When getObject(OffsetDateTime) throws, the method should fall back to
    // getTimestamp(utcCal) instead of calling getString (which would cause
    // StackOverflowError in the Redshift JDBC driver).
    when(resultSet.getObject(eq(1), eq(OffsetDateTime.class)))
        .thenThrow(new SQLException("Unsupported conversion"));
    when(resultSet.getTimestamp(eq(1), any(Calendar.class)))
        .thenReturn(Timestamp.from(OffsetDateTime.of(2026, 6, 4, 5, 50, 52, 815018000, ZoneOffset.UTC).toInstant()));

    final ObjectNode node = (ObjectNode) Jsons.emptyObject();
    ops.putTimestampWithTimezone(node, "created_at", resultSet, 1);

    verify(resultSet, never()).getString(anyInt());
    verify(resultSet, never()).getString(any(String.class));

    assertFalse(node.isEmpty());
    assertTrue(node.get("created_at").asText().contains("2026-06-04"));
  }

  @Test
  void testPutTimestampWithTimezoneHandlesNullInFallback() throws SQLException {
    when(resultSet.getObject(eq(1), eq(OffsetDateTime.class)))
        .thenThrow(new SQLException("Unsupported conversion"));
    when(resultSet.getTimestamp(eq(1), any(Calendar.class))).thenReturn(null);

    final ObjectNode node = (ObjectNode) Jsons.emptyObject();
    ops.putTimestampWithTimezone(node, "created_at", resultSet, 1);

    verify(resultSet, never()).getString(anyInt());
    assertFalse(node.has("created_at"));
  }

  @Test
  void testCopyToJsonFieldRoutesTimestamptzCorrectly() throws SQLException {
    // Verify that copyToJsonField dispatches timestamptz columns through
    // putTimestampWithTimezone (and therefore avoids getString).
    when(metadata.getColumnTypeName(1)).thenReturn("timestamptz");
    when(metadata.getColumnName(1)).thenReturn("updated_at");

    final OffsetDateTime expected = OffsetDateTime.of(2026, 1, 15, 10, 30, 0, 0, ZoneOffset.UTC);
    when(resultSet.getObject(eq(1), eq(OffsetDateTime.class))).thenReturn(expected);

    final ObjectNode node = (ObjectNode) Jsons.emptyObject();
    ops.copyToJsonField(resultSet, 1, node);

    verify(resultSet, never()).getString(anyInt());
    assertTrue(node.has("updated_at"));
    assertTrue(node.get("updated_at").asText().startsWith("2026-01-15T10:30:00"));
  }

}
