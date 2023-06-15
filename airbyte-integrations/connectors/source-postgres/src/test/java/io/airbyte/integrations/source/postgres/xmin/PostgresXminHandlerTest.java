package io.airbyte.integrations.source.postgres.xmin;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.integrations.source.postgres.internal.models.XminStatus;
import org.junit.jupiter.api.Test;

public class PostgresXminHandlerTest {

  @Test
  void testWraparound() {
    final XminStatus initialStatus =
        new XminStatus()
            .withNumWraparound(0L)
            .withXminRawValue(5555L)
            .withXminRawValue(5555L);

    final XminStatus noWrapAroundStatus =
        new XminStatus()
            .withNumWraparound(0L)
            .withXminRawValue(5588L)
            .withXminRawValue(5588L);
    assertFalse(PostgresXminHandler.isSingleWraparound(initialStatus, noWrapAroundStatus));
    assertFalse(PostgresXminHandler.shouldPerformFullSync(initialStatus, noWrapAroundStatus));

    final XminStatus singleWrapAroundStatus =
        new XminStatus()
            .withNumWraparound(1L)
            .withXminRawValue(5588L)
            .withXminRawValue(4294972884L);

    assertTrue(PostgresXminHandler.isSingleWraparound(initialStatus, singleWrapAroundStatus));
    assertFalse(PostgresXminHandler.shouldPerformFullSync(initialStatus, singleWrapAroundStatus));

    final XminStatus doubleWrapAroundStatus =
        new XminStatus()
            .withNumWraparound(2L)
            .withXminRawValue(5588L)
            .withXminRawValue(8589940180L);

    assertFalse(PostgresXminHandler.isSingleWraparound(initialStatus, doubleWrapAroundStatus));
    assertTrue(PostgresXminHandler.shouldPerformFullSync(initialStatus, doubleWrapAroundStatus));
  }
}
