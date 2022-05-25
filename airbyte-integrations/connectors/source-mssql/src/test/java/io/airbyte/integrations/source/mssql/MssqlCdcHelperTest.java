package io.airbyte.integrations.source.mssql;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import java.util.Map;
import org.junit.jupiter.api.Test;

class MssqlCdcHelperTest {

  @Test
  public void testIsCdc() {
    // legacy replication method config before version 0.4.0
    final JsonNode legacyNonCdc = Jsons.jsonNode(Map.of("replication_method", "STANDARD"));
    assertFalse(MssqlCdcHelper.isCdc(legacyNonCdc));

    final JsonNode legacyCdc = Jsons.jsonNode(Map.of("replication_method", "CDC"));
    assertTrue(MssqlCdcHelper.isCdc(legacyCdc));

    // new replication method config since version 0.4.0
    final JsonNode newNonCdc = Jsons.jsonNode(Map.of("replication_method",
        Jsons.jsonNode(Map.of("replication_type", "STANDARD"))));
    assertFalse(MssqlCdcHelper.isCdc(newNonCdc));

    final JsonNode newCdc = Jsons.jsonNode(Map.of("replication_method",
        Jsons.jsonNode(Map.of(
            "replication_type", "CDC",
            "data_to_sync", "Existing and New",
            "snapshot_isolation", "Snapshot"))));
    assertTrue(MssqlCdcHelper.isCdc(newCdc));
  }

}
