/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.nebulagraph;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.cdk.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;

public final class NebulaGraphRecordConsumer extends FailureTrackingAirbyteMessageConsumer {

  // 配置 & 依赖
  private final NebulaGraphConfig cfg;
  private final NebulaGraphClient client;
  private final StatementBuilder sb;
  private final VidGenerator vidGenerator;
  private final TypedExtractor typedExtractor;
  private final int maxBatchRecords;

  // startup-only schema; no runtime DDL, manager removed

  // Known typed columns list determined at startup (by streamKey)
  private final Map<String, List<String>> knownVertexTypedCols;
  private final Map<String, List<String>> knownEdgeTypedCols;

  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputCollector;

  private final Map<String, NebulaGraphConfig.StreamConfig> streamConfigByKey = new HashMap<>();

  private static final ObjectMapper OM = new ObjectMapper();

  private final Map<String, List<VertexRow>> vertexBuf = new LinkedHashMap<>();
  private final Map<String, String> vertexTagByStream = new LinkedHashMap<>();

  private final Map<String, List<EdgeRow>> edgeBuf = new LinkedHashMap<>();
  private final Map<String, String> edgeTypeByStream = new LinkedHashMap<>();

  public NebulaGraphRecordConsumer(NebulaGraphConfig cfg,
                                   NebulaGraphClient client,
                                   StatementBuilder sb,
                                   VidGenerator vidGenerator,
                                   TypedExtractor typedExtractor,
                                   int maxBatchRecords,
                                   Map<String, List<String>> knownVertexTypedCols,
                                   Map<String, List<String>> knownEdgeTypedCols,
                                   ConfiguredAirbyteCatalog catalog,
                                   Consumer<AirbyteMessage> outputCollector) {
    if (cfg == null || client == null || sb == null)
      throw new IllegalArgumentException("cfg/client/sb is null");
    if (maxBatchRecords < 1)
      throw new IllegalArgumentException("maxBatchRecords must be >=1");
    this.cfg = cfg;
    this.client = client;
    this.sb = sb;
    this.vidGenerator = vidGenerator == null ? new VidGenerator() : vidGenerator;
    this.typedExtractor = typedExtractor == null ? new TypedExtractor() : typedExtractor;
    this.maxBatchRecords = maxBatchRecords;
    this.catalog = catalog;
    this.outputCollector = outputCollector;
    this.knownVertexTypedCols = knownVertexTypedCols == null ? Map.of() : knownVertexTypedCols;
    this.knownEdgeTypedCols = knownEdgeTypedCols == null ? Map.of() : knownEdgeTypedCols;

    if (cfg.streams != null) {
      for (NebulaGraphConfig.StreamConfig s : cfg.streams) {
        String key = deriveTagName(s.namespace, s.name);
        streamConfigByKey.put(key, s);
      }
    }
  }

  /** Start: switch Space */
  @Override
  protected void startTracked() {
    try {
      client.execute("USE " + sb.q(cfg.space));
    } catch (Exception e) {
      throw new RuntimeException("failed to USE space: " + cfg.space, e);
    }
  }

  @Override
  protected void acceptTracked(final AirbyteMessage airbyteMessage) {
    if (airbyteMessage == null || airbyteMessage.getType() == null) {
      return;
    }
    if (airbyteMessage.getType() == AirbyteMessage.Type.RECORD) {
      final AirbyteRecordMessage record = airbyteMessage.getRecord();
      if (record == null)
        return;

      final String stream = record.getStream();
      final String namespace = record.getNamespace();
      final String streamKey = deriveTagName(namespace, stream);

      final NebulaGraphConfig.StreamConfig sc = streamConfigByKey.get(streamKey);

      // Prepare common data
      final Map<String, Object> recordMap = OM.convertValue(record.getData(), Map.class);
      final String rawJson = record.getData() == null ? null : record.getData().toString();
      final String abId = UUID.randomUUID().toString();
      final long emittedAt = record.getEmittedAt() == null ? System.currentTimeMillis() : record.getEmittedAt();
      final long loadedAt = System.currentTimeMillis();

      final boolean isEdge = (sc != null && "edge".equals(sc.entityType));
      if (!isEdge) {
        // Register Tag
        if (!vertexTagByStream.containsKey(streamKey)) {
          final String tagName = deriveTagName(namespace, stream);
          registerVertexStream(streamKey, tagName);
        }
        // Generate VID: If no mapping or vid_fields not configured, use abId as VID (append mode is enough)
        String vid;
        if (sc != null && sc.vidFields != null && !sc.vidFields.isEmpty()) {
          vid = vidGenerator.buildVid(recordMap, sc.vidFields, cfg.vidSeparator, cfg.vidFixedStringLength);
        } else {
          vid = abId;
        }

        // use_upsert=true → row-level UPSERT; false → into buffer
        final boolean dedup = cfg.useUpsert;
        if (dedup) {
          // Original four column headers and values
          final List<String> cols = new ArrayList<>(List.of("_airbyte_data", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_loaded_at"));
          final List<Object> vals = new ArrayList<>(List.of(rawJson, abId, emittedAt, loadedAt));

          if (sc != null && sc.typedEnabled) {
            final List<String> allowed = knownVertexTypedCols.getOrDefault(streamKey, List.of());
            if (!allowed.isEmpty()) {
              final Map<String, Object> typed = typedExtractor.extractTopLevelTyped(recordMap);
              for (String k : allowed) {
                cols.add(k);
                Object v = (typed == null) ? null : typed.get(k);
                vals.add(v);
              }
            }
          }

          String tagName = vertexTagByStream.get(streamKey);
          String sql = sb.buildUpsertVertex(tagName, vid, cols, vals);
          execWithRetry(sql, "upsertVertex stream=" + streamKey + ", vid=" + vid);
        } else {
          // append path: into buffer
          if (sc != null && sc.typedEnabled) {
            final Map<String, Object> typed = typedExtractor.extractTopLevelTyped(recordMap);
            addVertexRecord(streamKey, vid, rawJson, abId, emittedAt, loadedAt, typed);
          } else {
            addVertexRecord(streamKey, vid, rawJson, abId, emittedAt, loadedAt);
          }
        }
        return;
      }

      if (isEdge) {
        // Register Edge Type
        if (!edgeTypeByStream.containsKey(streamKey)) {
          final String edgeType = (sc.edgeType != null && !sc.edgeType.isEmpty()) ? toSafeLower(sc.edgeType) : deriveTagName(namespace, stream);
          registerEdgeStream(streamKey, edgeType);
        }
        // Generate src/dst/rank
        EndpointBuilder eb = new EndpointBuilder();
        final String src = eb.buildSrc(recordMap, sc.srcFields, cfg.vidSeparator, cfg.vidFixedStringLength);
        final String dst = eb.buildDst(recordMap, sc.dstFields, cfg.vidSeparator, cfg.vidFixedStringLength);
        final long rank = eb.buildRank(recordMap, sc.rankField);

        final boolean dedup = cfg.useUpsert;
        if (dedup) {
          // Original four column headers and values
          final List<String> cols = new ArrayList<>(List.of("_airbyte_data", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_loaded_at"));
          final List<Object> vals = new ArrayList<>(List.of(rawJson, abId, emittedAt, loadedAt));

          if (sc.typedEnabled) {
            final List<String> allowed = knownEdgeTypedCols.getOrDefault(streamKey, List.of());
            if (!allowed.isEmpty()) {
              final Map<String, Object> typed = typedExtractor.extractTopLevelTyped(recordMap);
              for (String k : allowed) {
                cols.add(k);
                Object v = (typed == null) ? null : typed.get(k);
                vals.add(v);
              }
            }
          }

          String et = edgeTypeByStream.get(streamKey);
          String sql = sb.buildUpsertEdge(et, src, dst, rank, cols, vals);
          execWithRetry(sql, "upsertEdge stream=" + streamKey + ", src=" + src + ", dst=" + dst + ", rank=" + rank);
        } else {
          // append: into buffer
          if (sc.typedEnabled) {
            final Map<String, Object> typed = typedExtractor.extractTopLevelTyped(recordMap);
            addEdgeRecord(streamKey, src, dst, rank, rawJson, abId, emittedAt, loadedAt, typed);
          } else {
            addEdgeRecord(streamKey, src, dst, rank, rawJson, abId, emittedAt, loadedAt);
          }
        }
        return;
      }
    }

    if (airbyteMessage.getType() == AirbyteMessage.Type.STATE) {
      // Before STATE, flushAll, then pass STATE
      flushAll();
      if (outputCollector != null) {
        outputCollector.accept(airbyteMessage);
      }
    }
  }

  /**
   * Flush all buffers (Vertex and Edge). Used to ensure submission semantics before STATE/close.
   */
  public void flushAll() {
    if (vertexBuf != null && !vertexBuf.isEmpty()) {
      List<String> vKeys = new ArrayList<>(vertexBuf.keySet());
      for (String k : vKeys) {
        flushVertexAppend(k);
      }
    }
    if (edgeBuf != null && !edgeBuf.isEmpty()) {
      List<String> eKeys = new ArrayList<>(edgeBuf.keySet());
      for (String k : eKeys) {
        flushEdgeAppend(k);
      }
    }
  }

  private void execWithRetry(String sql, String opDesc) {
    final int[] backoffMs = new int[] {100, 200, 400, 800, 1600, 3200, 6400, 12800};
    Exception last = null;
    for (int attempt = 0; attempt <= backoffMs.length; attempt++) {
      try {
        // Log first attempt statements (INFO for visibility in test logs, DEBUG full length)
        if (attempt == 0 && (sql.startsWith("INSERT VERTEX") || sql.startsWith("UPSERT VERTEX") || sql.startsWith("INSERT EDGE")
            || sql.startsWith("UPSERT EDGE"))) {
          String trimmed = sql.length() > 1200 ? sql.substring(0, 1200) + "..." : sql;
          org.slf4j.Logger logger = org.slf4j.LoggerFactory.getLogger(NebulaGraphRecordConsumer.class);
          logger.info("exec op={} attempt={} sqlSnippet={} chars={}", opDesc, attempt, trimmed.replaceAll("\n", "\\n"), sql.length());
          if (logger.isDebugEnabled()) {
            logger.debug("FULL-SQL op={} sql=\n{}", opDesc, sql);
          }
        }
        client.execute(sql);
        return;
      } catch (Exception e) {
        last = e;
        if (attempt == backoffMs.length) {
          throw new RuntimeException("Operation failed after retries: " + opDesc, e);
        }
        try {
          Thread.sleep(backoffMs[attempt]);
        } catch (InterruptedException ie) {
          Thread.currentThread().interrupt();
          throw new RuntimeException("Interrupted during retry backoff for: " + opDesc, e);
        }
      }
    }
    if (last != null) {
      throw new RuntimeException("Operation failed: " + opDesc, last);
    }
  }

  private static String deriveTagName(String namespace, String name) {
    String ns = toSafeLower(namespace);
    String nm = toSafeLower(name);
    return (ns == null || ns.isEmpty()) ? nm : ns + "__" + nm;
  }

  private static String toSafeLower(String s) {
    return s == null ? null : s.trim().toLowerCase();
  }

  /** Register a Vertex stream's Tag name (streamKey usually is namespace__stream) */
  public void registerVertexStream(String streamKey, String tagName) {
    if (streamKey == null || streamKey.isEmpty())
      throw new IllegalArgumentException("streamKey empty");
    if (tagName == null || tagName.isEmpty())
      throw new IllegalArgumentException("tagName empty");
    vertexTagByStream.put(streamKey, tagName);
    vertexBuf.computeIfAbsent(streamKey, k -> new ArrayList<>());
    // startup-only schema; nothing to seed at runtime
  }

  /** Register an Edge stream's EdgeType name */
  public void registerEdgeStream(String streamKey, String edgeType) {
    if (streamKey == null || streamKey.isEmpty())
      throw new IllegalArgumentException("streamKey empty");
    if (edgeType == null || edgeType.isEmpty())
      throw new IllegalArgumentException("edgeType empty");
    edgeTypeByStream.put(streamKey, edgeType);
    edgeBuf.computeIfAbsent(streamKey, k -> new ArrayList<>());
    // startup-only schema; nothing to seed at runtime
  }

  /** Append a Vertex record to the buffer (raw-only). Trigger flush when exceeds the threshold. */
  public void addVertexRecord(String streamKey, String vid, String rawJson, String abId, long emittedAt, long loadedAt) {
    if (!vertexTagByStream.containsKey(streamKey)) {
      throw new IllegalStateException("stream not registered: " + streamKey);
    }
    List<VertexRow> buf = vertexBuf.computeIfAbsent(streamKey, k -> new ArrayList<>());
    buf.add(new VertexRow(vid, rawJson, abId, emittedAt, loadedAt));
    if (buf.size() >= maxBatchRecords) {
      flushVertexAppend(streamKey);
    }
  }

  public void addVertexRecord(String streamKey, String vid, String rawJson, String abId, long emittedAt, long loadedAt, Map<String, Object> typed) {
    if (!vertexTagByStream.containsKey(streamKey)) {
      throw new IllegalStateException("stream not registered: " + streamKey);
    }
    List<VertexRow> buf = vertexBuf.computeIfAbsent(streamKey, k -> new ArrayList<>());
    VertexRow row = new VertexRow(vid, rawJson, abId, emittedAt, loadedAt);
    row.typed = typed;
    buf.add(row);
    if (buf.size() >= maxBatchRecords) {
      flushVertexAppend(streamKey);
    }
  }

  /**
   * Batch INSERT (raw+typed). Page execution, each batch不超过 maxBatchRecords。
   */
  public void flushVertexAppend(String streamKey) {
    List<VertexRow> buf = vertexBuf.get(streamKey);
    if (buf == null || buf.isEmpty())
      return;
    String tag = vertexTagByStream.get(streamKey);
    if (tag == null || tag.isEmpty())
      throw new IllegalStateException("missing tag for stream: " + streamKey);

    final List<String> rawCols = List.of("_airbyte_data", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_loaded_at");
    final NebulaGraphConfig.StreamConfig sc = streamConfigByKey.get(streamKey);
    final boolean typedOn = sc != null && sc.typedEnabled;

    int from = 0;
    while (from < buf.size()) {
      int to = Math.min(from + maxBatchRecords, buf.size());
      List<VertexRow> page = buf.subList(from, to);

      List<String> typedKeys = List.of();
      if (typedOn) {
        typedKeys = knownVertexTypedCols.getOrDefault(streamKey, List.of());
      }

      // 2) assemble column headers
      List<String> cols = new ArrayList<>(rawCols);
      if (typedOn) {
        cols.addAll(typedKeys);
      }

      // 3) construct values aligned with column headers, then concatenate vid:"(v1,...)" fragment
      List<String> vidAndValueTuples = new ArrayList<>(page.size());
      for (VertexRow r : page) {
        List<Object> values = new ArrayList<>(cols.size());
        // raw4（两列 string + 两列 int）
        values.add(r.rawJson);
        values.add(r.abId);
        values.add(r.emittedAt);
        values.add(r.loadedAt);
        if (typedOn) {
          for (String k : typedKeys) {
            Object v = (r.typed == null) ? null : r.typed.get(k);
            values.add(v);
          }
        }
        vidAndValueTuples.add(sb.formatVidAndValues(r.vid, values));
      }

      String sql = sb.buildInsertVertexValues(tag, cols, vidAndValueTuples);
      execWithRetry(sql, "flushVertexAppend stream=" + streamKey + ", range=" + from + ".." + (to - 1));

      // Debug probe: fetch first VID just written to verify properties actually stored (helps diagnose
      // NULL issue)
      try {
        if (!page.isEmpty()) {
          String probeVid = page.get(0).vid;
          String fetch = "FETCH PROP ON " + sb.q(tag) + " " + sb.qs(probeVid)
              + " YIELD " + sb.q(tag) + ".`_airbyte_data` AS d," + sb.q(tag) + ".`_airbyte_emitted_at` AS e," + sb.q(tag) + ".`_airbyte_ab_id` AS a";
          try {
            java.util.List<String> probe = client.queryJsonColumn(fetch, "d");
            String firstVal = (probe != null && !probe.isEmpty() ? probe.get(0) : null);
            org.slf4j.LoggerFactory.getLogger(NebulaGraphRecordConsumer.class)
                .info("probe vertex tag={} vid={} fetchRows={} d0={} sql={}", tag, probeVid, (probe == null ? 0 : probe.size()),
                    (firstVal == null ? "<null>" : firstVal), fetch.replace('\n', ' '));
            // Fallback: if firstVal is null, re-write this page using per-row UPSERT (robustness over
            // performance)
            if (firstVal == null) {
              org.slf4j.LoggerFactory.getLogger(NebulaGraphRecordConsumer.class)
                  .warn("batch INSERT returned NULL property; falling back to per-row UPSERT for page size={} tag={}", page.size(), tag);
              for (VertexRow r : page) {
                java.util.List<Object> rowValues = new java.util.ArrayList<>();
                rowValues.add(r.rawJson);
                rowValues.add(r.abId);
                rowValues.add(r.emittedAt);
                rowValues.add(r.loadedAt);
                if (typedOn) {
                  for (String k2 : typedKeys) {
                    Object v2 = (r.typed == null) ? null : r.typed.get(k2);
                    rowValues.add(v2);
                  }
                }
                String upsert = sb.buildUpsertVertex(tag, r.vid, cols, rowValues);
                execWithRetry(upsert, "fallbackUpsertVertex vid=" + r.vid);
              }
              // re-probe
              try {
                java.util.List<String> reprobe = client.queryJsonColumn(fetch, "d");
                String after = (reprobe != null && !reprobe.isEmpty() ? reprobe.get(0) : null);
                org.slf4j.LoggerFactory.getLogger(NebulaGraphRecordConsumer.class)
                    .info("fallback UPSERT probe tag={} vid={} d0After={}", tag, probeVid, after == null ? "<null>" : after);
              } catch (Exception ignoreReprobe) { /* ignore */ }
            }
          } catch (Exception fe) {
            org.slf4j.LoggerFactory.getLogger(NebulaGraphRecordConsumer.class)
                .info("probe vertex failed tag={} vid={} err={}", tag, probeVid, fe.getMessage());
          }
        }
      } catch (Exception outerProbe) {
        // swallow
      }
      from = to;
    }

    // Clear buffer
    buf.clear();
  }

  /** Batch INSERT EDGE (raw+typed), page execution. */
  public void flushEdgeAppend(String streamKey) {
    List<EdgeRow> buf = edgeBuf.get(streamKey);
    if (buf == null || buf.isEmpty())
      return;
    String edgeType = edgeTypeByStream.get(streamKey);
    if (edgeType == null || edgeType.isEmpty())
      throw new IllegalStateException("missing edgeType for stream: " + streamKey);

    final List<String> rawCols = List.of("_airbyte_data", "_airbyte_ab_id", "_airbyte_emitted_at", "_airbyte_loaded_at");
    final NebulaGraphConfig.StreamConfig sc = streamConfigByKey.get(streamKey);
    final boolean typedOn = sc != null && sc.typedEnabled;

    int from = 0;
    while (from < buf.size()) {
      int to = Math.min(from + maxBatchRecords, buf.size());
      List<EdgeRow> page = buf.subList(from, to);

      List<String> typedKeys = List.of();
      if (typedOn) {
        typedKeys = knownEdgeTypedCols.getOrDefault(streamKey, List.of());
      }

      // 2) column headers
      List<String> cols = new ArrayList<>(rawCols);
      if (typedOn)
        cols.addAll(typedKeys);

      // 3) assemble "src"->"dst"@rank:(...)
      List<String> endpointsAndValueTuples = new ArrayList<>(page.size());
      for (EdgeRow r : page) {
        List<Object> values = new ArrayList<>(cols.size());
        values.add(r.rawJson);
        values.add(r.abId);
        values.add(r.emittedAt);
        values.add(r.loadedAt);
        if (typedOn) {
          for (String k : typedKeys) {
            Object v = (r.typed == null) ? null : r.typed.get(k);
            values.add(v);
          }
        }
        endpointsAndValueTuples.add(sb.formatEdgeEndpointsAndValues(r.src, r.dst, r.rank, values));
      }

      String sql = sb.buildInsertEdgeValues(edgeType, cols, endpointsAndValueTuples);
      execWithRetry(sql, "flushEdgeAppend stream=" + streamKey + ", range=" + from + ".." + (to - 1));
      from = to;
    }

    buf.clear();
  }

  // Removed unused runtime typing helpers after startup-only schema mode

  @Override
  protected void close(final boolean hasFailed) {
    try {
      // Close before flushAll, ensure all buffers are written
      flushAll();
    } finally {
      client.close();
    }
  }

  public static final class VertexRow {

    public final String vid;
    public final String rawJson;
    public final String abId;
    public final long emittedAt;
    public final long loadedAt;
    public Map<String, Object> typed;

    public VertexRow(String vid, String rawJson, String abId, long emittedAt, long loadedAt) {
      if (vid == null)
        throw new IllegalArgumentException("vid is null");
      this.vid = vid;
      this.rawJson = rawJson; // Can be null → write NULL
      this.abId = abId; // Can be null → write NULL
      this.emittedAt = emittedAt;
      this.loadedAt = loadedAt;
    }

  }

  public static final class EdgeRow {

    public final String src;
    public final String dst;
    public final long rank;
    public final String rawJson;
    public final String abId;
    public final long emittedAt;
    public final long loadedAt;
    public Map<String, Object> typed;

    public EdgeRow(String src, String dst, long rank, String rawJson, String abId, long emittedAt, long loadedAt) {
      if (src == null)
        throw new IllegalArgumentException("src is null");
      if (dst == null)
        throw new IllegalArgumentException("dst is null");
      this.src = src;
      this.dst = dst;
      this.rank = rank;
      this.rawJson = rawJson;
      this.abId = abId;
      this.emittedAt = emittedAt;
      this.loadedAt = loadedAt;
    }

  }

  // Edge buffer append (raw-only)
  public void addEdgeRecord(String streamKey, String src, String dst, long rank, String rawJson, String abId, long emittedAt, long loadedAt) {
    if (!edgeTypeByStream.containsKey(streamKey))
      throw new IllegalStateException("stream not registered: " + streamKey);
    List<EdgeRow> buf = edgeBuf.computeIfAbsent(streamKey, k -> new ArrayList<>());
    buf.add(new EdgeRow(src, dst, rank, rawJson, abId, emittedAt, loadedAt));
    if (buf.size() >= maxBatchRecords)
      flushEdgeAppend(streamKey);
  }

  // Edge buffer append (raw+typed)
  public void addEdgeRecord(String streamKey,
                            String src,
                            String dst,
                            long rank,
                            String rawJson,
                            String abId,
                            long emittedAt,
                            long loadedAt,
                            Map<String, Object> typed) {
    if (!edgeTypeByStream.containsKey(streamKey))
      throw new IllegalStateException("stream not registered: " + streamKey);
    List<EdgeRow> buf = edgeBuf.computeIfAbsent(streamKey, k -> new ArrayList<>());
    EdgeRow row = new EdgeRow(src, dst, rank, rawJson, abId, emittedAt, loadedAt);
    row.typed = typed;
    buf.add(row);
    if (buf.size() >= maxBatchRecords)
      flushEdgeAppend(streamKey);
  }

}
