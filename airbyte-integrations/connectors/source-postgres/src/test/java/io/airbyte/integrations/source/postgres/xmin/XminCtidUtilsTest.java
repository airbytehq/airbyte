package io.airbyte.integrations.source.postgres.xmin;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.internal.models.XminStatus;
import org.junit.jupiter.api.Test;

public class XminCtidUtilsTest {

  @Test
  void testWraparound() {
    final JsonNode initialStatus =
        Jsons.jsonNode(new XminStatus()
            .withNumWraparound(0L)
            .withXminRawValue(5555L)
            .withXminRawValue(5555L));

    final XminStatus noWrapAroundStatus =
        new XminStatus()
            .withNumWraparound(0L)
            .withXminRawValue(5588L)
            .withXminRawValue(5588L);
    assertFalse(XminCtidUtils.shouldPerformFullSync(noWrapAroundStatus, initialStatus));

    final XminStatus singleWrapAroundStatus =
        new XminStatus()
            .withNumWraparound(1L)
            .withXminRawValue(5588L)
            .withXminRawValue(4294972884L);

    assertFalse(XminCtidUtils.shouldPerformFullSync(singleWrapAroundStatus, initialStatus));

    final XminStatus doubleWrapAroundStatus =
        new XminStatus()
            .withNumWraparound(2L)
            .withXminRawValue(5588L)
            .withXminRawValue(8589940180L);

    assertTrue(XminCtidUtils.shouldPerformFullSync(doubleWrapAroundStatus, initialStatus));
  }

}
