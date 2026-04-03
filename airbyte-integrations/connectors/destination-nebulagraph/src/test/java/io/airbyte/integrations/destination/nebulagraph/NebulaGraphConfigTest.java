/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.nebulagraph;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("NebulaGraphConfig")
class NebulaGraphConfigTest {

  private static final ObjectMapper M = new ObjectMapper();

  private ObjectNode baseRequired() {
    ObjectNode root = M.createObjectNode();
    root.put("graphd_addresses", "127.0.0.1:9669");
    root.put("space", "s1");
    root.put("username", "root");
    // password optional
    return root;
  }

  @Test
  void missingRequiredFieldsThrows() {
    // missing graphd_addresses
    ObjectNode a = M.createObjectNode();
    a.put("space", "s1");
    a.put("username", "u");
    assertThrows(IllegalArgumentException.class, () -> NebulaGraphConfig.from(a));

    // missing space
    ObjectNode b = M.createObjectNode();
    b.put("graphd_addresses", "127.0.0.1:9669");
    b.put("username", "u");
    assertThrows(IllegalArgumentException.class, () -> NebulaGraphConfig.from(b));

    // missing username
    ObjectNode c = M.createObjectNode();
    c.put("graphd_addresses", "127.0.0.1:9669");
    c.put("space", "s1");
    assertThrows(IllegalArgumentException.class, () -> NebulaGraphConfig.from(c));
  }

  @Test
  void defaultsApplied() {
    ObjectNode root = baseRequired();
    NebulaGraphConfig cfg = NebulaGraphConfig.from(root);

    assertEquals(false, cfg.useUpsert);
    assertEquals(500, cfg.maxBatchRecords);
    assertEquals("::", cfg.vidSeparator);
    assertEquals(128, cfg.vidFixedStringLength);
    assertTrue(cfg.createSpaceIfMissing);
  }

  @Test
  void invalidRangesThrow() {

    // vid length out of range
    ObjectNode r2 = baseRequired();
    r2.put("vid_fixed_string_length", 4);
    assertThrows(IllegalArgumentException.class, () -> NebulaGraphConfig.from(r2));

    // max_batch_records < 1
    ObjectNode r3 = baseRequired();
    r3.put("max_batch_records", 0);
    assertThrows(IllegalArgumentException.class, () -> NebulaGraphConfig.from(r3));
  }

  @Test
  void streamConfigVertexRequiresVidFields() {
    ObjectNode root = baseRequired();
    ArrayNode streams = M.createArrayNode();
    ObjectNode s = M.createObjectNode();
    s.put("name", "users");
    s.put("entity_type", "vertex");
    // missing vid_fields
    streams.add(s);
    root.set("streams", streams);

    assertThrows(IllegalArgumentException.class, () -> NebulaGraphConfig.from(root));
  }

  @Test
  void streamConfigEdgeRequiresEndpoints() {
    ObjectNode root = baseRequired();
    ArrayNode streams = M.createArrayNode();
    ObjectNode s = M.createObjectNode();
    s.put("name", "rel");
    s.put("entity_type", "edge");
    // missing src_fields/dst_fields
    streams.add(s);
    root.set("streams", streams);

    assertThrows(IllegalArgumentException.class, () -> NebulaGraphConfig.from(root));
  }

  @Test
  void streamConfigTypedEnabledParsed() {
    ObjectNode root = baseRequired();

    ArrayNode vidFields = M.createArrayNode();
    vidFields.add("tenant_id");

    ObjectNode typed = M.createObjectNode();
    typed.put("enabled", true);

    ArrayNode streams = M.createArrayNode();
    ObjectNode s = M.createObjectNode();
    s.put("name", "users");
    s.put("namespace", "public");
    s.put("entity_type", "vertex");
    s.set("vid_fields", vidFields);
    s.set("typed", typed);
    streams.add(s);

    root.set("streams", streams);

    NebulaGraphConfig cfg = NebulaGraphConfig.from(root);
    assertEquals(1, cfg.streams.size());
    NebulaGraphConfig.StreamConfig sc = cfg.streams.get(0);
    assertTrue(sc.typedEnabled);
    assertEquals(List.of("tenant_id"), sc.vidFields);
  }

}
