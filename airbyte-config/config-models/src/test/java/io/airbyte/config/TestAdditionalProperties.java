package io.airbyte.config;

import io.airbyte.commons.json.Jsons;
import java.util.ArrayList;
import java.util.Map;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;

public class TestAdditionalProperties {
  @Test
  public void testAddProp() {
    final Map<String, Object> json = Map.ofEntries(
        Map.entry("Not", "allow"),
        Map.entry("streamsToResetWithTypo", new ArrayList<>())
    );

    Assertions.assertThatThrownBy(() -> Jsons.object(Jsons.jsonNode(json), ResetSourceConfiguration.class));
  }
}
