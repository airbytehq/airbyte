/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import java.util.List;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

public class SnowflakeInternalStagingCaseInsensitiveTypingDedupingTest extends AbstractSnowflakeTypingDedupingTest {

  @Override
  protected String getConfigPath() {
    return "secrets/1s1t_case_insensitive.json";
  }

  @Override
  protected List<JsonNode> dumpRawTableRecords(String streamNamespace, final String streamName) throws Exception {
    List<JsonNode> records = super.dumpRawTableRecords(streamNamespace, streamName);
    return records.stream()
        .map(record -> {
          // Downcase the column names.
          // RecordDiffer expects the raw table column names to be lowercase.
          // TODO we should probably provide a way to mutate the expected data?
          ObjectNode mutatedRecord = (ObjectNode) Jsons.emptyObject();
          record.fields().forEachRemaining(entry -> {
            mutatedRecord.set(entry.getKey().toLowerCase(), entry.getValue());
          });
          return (JsonNode) mutatedRecord;
        })
        .toList();
  }

  @Disabled("This test assumes the ability to create case-sensitive tables, which is by definition not available with QUOTED_IDENTIFIERS_IGNORE_CASE=TRUE")
  @Test
  public void testFinalTableUppercasingMigration_append() throws Exception {
    super.testFinalTableUppercasingMigration_append();
  }

}
