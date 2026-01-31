/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.nebulagraph;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Objects;

public final class NebulaGraphConfig {

  public static final int DEFAULT_MAX_BATCH_RECORDS = 500;
  public static final String DEFAULT_VID_SEPARATOR = "::";
  public static final boolean DEFAULT_USE_UPSERT = false; // false -> buffered INSERT; true -> per-record UPSERT
  public static final int DEFAULT_VID_FIXED_STRING_LENGTH = 128;

  public final String graphdAddresses; // host:port(,host:port)
  public final String space;
  public final String username;
  public final String password;
  public final boolean createSpaceIfMissing;
  public final int vidFixedStringLength;
  public final boolean useUpsert;
  public final int maxBatchRecords;
  public final String vidSeparator;
  public final List<StreamConfig> streams;

  private NebulaGraphConfig(
                            String graphdAddresses,
                            String space,
                            String username,
                            String password,
                            boolean createSpaceIfMissing,
                            int vidFixedStringLength,
                            boolean useUpsert,
                            int maxBatchRecords,
                            String vidSeparator,
                            List<StreamConfig> streams) {
    this.graphdAddresses = graphdAddresses;
    this.space = space;
    this.username = username;
    this.password = password;
    this.createSpaceIfMissing = createSpaceIfMissing;
    this.vidFixedStringLength = vidFixedStringLength;
    this.useUpsert = useUpsert;
    this.maxBatchRecords = maxBatchRecords;
    this.vidSeparator = vidSeparator;
    this.streams = streams;
  }

  public static NebulaGraphConfig from(JsonNode root) {
    Objects.requireNonNull(root, "config is null");

    String graphd = reqText(root, "graphd_addresses");
    String space = reqText(root, "space");
    String username = reqText(root, "username");
    String password = optText(root, "password", "");

    boolean createSpaceIfMissing = optBool(root, "create_space_if_missing", true);
    int vidLen = optInt(root, "vid_fixed_string_length", DEFAULT_VID_FIXED_STRING_LENGTH);
    boolean useUpsert = optBool(root, "use_upsert", DEFAULT_USE_UPSERT);
    int maxBatch = optInt(root, "max_batch_records", DEFAULT_MAX_BATCH_RECORDS);
    String vidSep = optText(root, "vid_separator", DEFAULT_VID_SEPARATOR);
    List<StreamConfig> streams = parseStreams(root.get("streams"));

    if (maxBatch < 1) {
      throw new IllegalArgumentException("max_batch_records must be >= 1");
    }
    if (vidLen < 8 || vidLen > 1024) {
      throw new IllegalArgumentException("vid_fixed_string_length out of range (8..1024)");
    }

    return new NebulaGraphConfig(graphd, space, username, password, createSpaceIfMissing,
        vidLen, useUpsert, maxBatch, vidSep, streams);
  }

  private static List<StreamConfig> parseStreams(JsonNode node) {
    if (node == null || !node.isArray())
      return Collections.emptyList();
    List<StreamConfig> list = new ArrayList<>();
    for (JsonNode s : node) {
      list.add(StreamConfig.from(s));
    }
    return list;
  }

  private static String reqText(JsonNode n, String field) {
    JsonNode v = n.get(field);
    if (v == null || v.isNull() || !v.isTextual()) {
      throw new IllegalArgumentException("Missing/invalid field: " + field);
    }
    return v.asText();
  }

  private static String optText(JsonNode n, String field, String def) {
    JsonNode v = n.get(field);
    return (v == null || v.isNull()) ? def : v.asText();
  }

  private static boolean optBool(JsonNode n, String field, boolean def) {
    JsonNode v = n.get(field);
    return (v == null || v.isNull()) ? def : v.asBoolean();
  }

  private static int optInt(JsonNode n, String field, int def) {
    JsonNode v = n.get(field);
    return (v == null || v.isNull()) ? def : v.asInt();
  }

  public static final class StreamConfig {

    public final String name;
    public final String namespace;
    public final String entityType; // vertex | edge
    public final List<String> vidFields; // vertex only
    public final String edgeType; // optional override
    public final List<String> srcFields; // edge only
    public final List<String> dstFields; // edge only
    public final String rankField; // optional
    public final boolean typedEnabled;

    private StreamConfig(String name,
                         String namespace,
                         String entityType,
                         List<String> vidFields,
                         String edgeType,
                         List<String> srcFields,
                         List<String> dstFields,
                         String rankField,
                         boolean typedEnabled) {
      this.name = name;
      this.namespace = namespace;
      this.entityType = entityType;
      this.vidFields = vidFields;
      this.edgeType = edgeType;
      this.srcFields = srcFields;
      this.dstFields = dstFields;
      this.rankField = rankField;
      this.typedEnabled = typedEnabled;
    }

    static StreamConfig from(JsonNode n) {
      String name = reqText(n, "name");
      String entityType = reqText(n, "entity_type");
      String namespace = optText(n, "namespace", "");

      List<String> vid = readStringArray(n.get("vid_fields"));
      String edgeType = optText(n, "edge_type", "");
      List<String> src = readStringArray(n.get("src_fields"));
      List<String> dst = readStringArray(n.get("dst_fields"));
      String rank = optText(n, "rank_field", null);

      boolean typedEnabled = false;
      JsonNode typedNode = n.get("typed");
      if (typedNode != null && typedNode.isObject()) {
        JsonNode en = typedNode.get("enabled");
        typedEnabled = en != null && en.asBoolean(false);
      }

      if (!entityType.equals("vertex") && !entityType.equals("edge")) {
        throw new IllegalArgumentException("entity_type must be vertex or edge");
      }
      if (entityType.equals("vertex")) {
        if (vid.isEmpty())
          throw new IllegalArgumentException("vertex stream requires vid_fields");
      } else { // edge
        if (src.isEmpty() || dst.isEmpty()) {
          throw new IllegalArgumentException("edge stream requires src_fields and dst_fields");
        }
      }

      return new StreamConfig(name, namespace, entityType, vid, edgeType, src, dst, rank, typedEnabled);
    }

    private static List<String> readStringArray(JsonNode arr) {
      if (arr == null || !arr.isArray())
        return Collections.emptyList();
      List<String> out = new ArrayList<>();
      Iterator<JsonNode> it = arr.elements();
      while (it.hasNext()) {
        JsonNode e = it.next();
        if (e != null && e.isTextual())
          out.add(e.asText());
      }
      return out;
    }

  }

}
