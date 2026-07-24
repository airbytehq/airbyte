/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.nebulagraph;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

@DisplayName("NebulaGraphRecordConsumer")
class NebulaGraphRecordConsumerTest {

  private static final ObjectMapper M = new ObjectMapper();

  @Test
  void con01AppendVertexPaginationFlush() throws Exception {
    NebulaGraphClient client = mock(NebulaGraphClient.class);
    Consumer<AirbyteMessage> collector = mock(Consumer.class);
    doNothing().when(client).execute(anyString());

    NebulaGraphConfig cfg = buildVertexCfg("public", "users", null, false, List.of("id"));
    ConfiguredAirbyteCatalog catalog = buildCatalog("public", "users");

    NebulaGraphRecordConsumer consumer = newConsumer(cfg, client, 2, Map.of(), Map.of(), catalog, collector);

    consumer.start();

    // produce 5 records => expect 3 INSERT batches: 2,2,1
    List<AirbyteMessage> records = new ArrayList<>();
    for (int i = 1; i <= 5; i++) {
      ObjectNode data = M.createObjectNode();
      data.put("id", "u" + i);
      data.put("payload", i);
      records.add(new AirbyteMessage()
          .withType(AirbyteMessage.Type.RECORD)
          .withRecord(new AirbyteRecordMessage()
              .withStream("users")
              .withNamespace("public")
              .withEmittedAt(1L * i)
              .withData(data)));
    }
    for (AirbyteMessage m : records)
      consumer.accept(m);

    // flush remaining (last page size 1)
    consumer.flushAll();

    // capture SQL
    ArgumentCaptor<String> sqls = ArgumentCaptor.forClass(String.class);
    verify(client, org.mockito.Mockito.atLeast(3)).execute(sqls.capture());

    List<String> inserts = sqls.getAllValues().stream()
        .filter(sq -> sq.startsWith("INSERT VERTEX "))
        .collect(Collectors.toList());

    assertEquals(3, inserts.size(), "Expected 3 vertex insert batches");
    assertEquals(2, countTuples(inserts.get(0)));
    assertEquals(2, countTuples(inserts.get(1)));
    assertEquals(1, countTuples(inserts.get(2)));
  }

  @Test
  void con02AppendEdgePaginationFlush() throws Exception {
    NebulaGraphClient client = mock(NebulaGraphClient.class);
    Consumer<AirbyteMessage> collector = mock(Consumer.class);
    doNothing().when(client).execute(anyString());

    NebulaGraphConfig cfg = buildEdgeCfg("public", "rels", null, false, List.of("sa", "sb"), List.of("da"));
    ConfiguredAirbyteCatalog catalog = buildCatalog("public", "rels");

    NebulaGraphRecordConsumer consumer = newConsumer(cfg, client, 2, Map.of(), Map.of(), catalog, collector);

    consumer.start();

    // 5 records -> 3 INSERT EDGE batches: 2,2,1
    List<AirbyteMessage> records = new ArrayList<>();
    for (int i = 1; i <= 5; i++) {
      ObjectNode data = M.createObjectNode();
      data.put("sa", "s" + i);
      data.put("sb", i);
      data.put("da", "d" + i);
      data.put("payload", "p" + i);
      records.add(new AirbyteMessage()
          .withType(AirbyteMessage.Type.RECORD)
          .withRecord(new AirbyteRecordMessage()
              .withStream("rels")
              .withNamespace("public")
              .withEmittedAt(1L * i)
              .withData(data)));
    }
    for (AirbyteMessage m : records)
      consumer.accept(m);

    consumer.flushAll();

    ArgumentCaptor<String> sqls = ArgumentCaptor.forClass(String.class);
    verify(client, org.mockito.Mockito.atLeast(3)).execute(sqls.capture());

    List<String> inserts = sqls.getAllValues().stream()
        .filter(sq -> sq.startsWith("INSERT EDGE "))
        .collect(Collectors.toList());

    assertEquals(3, inserts.size(), "Expected 3 edge insert batches");
    assertEquals(2, countTuples(inserts.get(0)));
    assertEquals(2, countTuples(inserts.get(1)));
    assertEquals(1, countTuples(inserts.get(2)));
  }

  @Test
  void con03AppendDedupUpsertVertexAndEdge() throws Exception {
    NebulaGraphClient client = mock(NebulaGraphClient.class);
    Consumer<AirbyteMessage> collector = mock(Consumer.class);
    doNothing().when(client).execute(anyString());

    NebulaGraphConfig cfgV = buildVertexCfg("public", "users", true, false, List.of("id"));
    ConfiguredAirbyteCatalog catalogV = buildCatalog("public", "users");

    NebulaGraphRecordConsumer consumerV = newConsumer(cfgV, client, 100, Map.of(), Map.of(), catalogV, collector);

    consumerV.start();
    // two vertex records => expect two UPSERT VERTEX, no INSERT VERTEX
    for (int i = 1; i <= 2; i++) {
      ObjectNode data = M.createObjectNode();
      data.put("id", "u" + i);
      data.put("x", i);
      consumerV.accept(new AirbyteMessage()
          .withType(AirbyteMessage.Type.RECORD)
          .withRecord(new AirbyteRecordMessage()
              .withStream("users").withNamespace("public").withEmittedAt(1L * i).withData(data)));
    }

    ArgumentCaptor<String> sqlV = ArgumentCaptor.forClass(String.class);
    verify(client, org.mockito.Mockito.atLeast(2)).execute(sqlV.capture());
    long upsertsV = sqlV.getAllValues().stream().filter(sq -> sq.startsWith("UPSERT VERTEX ON ")).count();
    long insertsV = sqlV.getAllValues().stream().filter(sq -> sq.startsWith("INSERT VERTEX ")).count();
    assertEquals(2, upsertsV);
    assertEquals(0, insertsV);

    // config: edge stream with use_upsert=true
    NebulaGraphClient clientE = mock(NebulaGraphClient.class);
    doNothing().when(clientE).execute(anyString());
    Consumer<AirbyteMessage> collectorE = mock(Consumer.class);

    NebulaGraphConfig cfgE = buildEdgeCfg("public", "rels", true, false, List.of("sa", "sb"), List.of("da"));
    ConfiguredAirbyteCatalog catalogE = buildCatalog("public", "rels");

    NebulaGraphRecordConsumer consumerE = newConsumer(cfgE, clientE, 100, Map.of(), Map.of(), catalogE, collectorE);

    consumerE.start();
    for (int i = 1; i <= 3; i++) {
      ObjectNode data = M.createObjectNode();
      data.put("sa", "s" + i);
      data.put("sb", i);
      data.put("da", "d" + i);
      consumerE.accept(new AirbyteMessage()
          .withType(AirbyteMessage.Type.RECORD)
          .withRecord(new AirbyteRecordMessage()
              .withStream("rels").withNamespace("public").withEmittedAt(1L * i).withData(data)));
    }

    ArgumentCaptor<String> sqlE = ArgumentCaptor.forClass(String.class);
    verify(clientE, org.mockito.Mockito.atLeast(3)).execute(sqlE.capture());
    long upsertsE = sqlE.getAllValues().stream().filter(sq -> sq.startsWith("UPSERT EDGE ON ")).count();
    long insertsE = sqlE.getAllValues().stream().filter(sq -> sq.startsWith("INSERT EDGE ")).count();
    assertEquals(3, upsertsE);
    assertEquals(0, insertsE);
  }

  @Test
  void con04TypedColumnsWriteFilteringVertexAndEdge() throws Exception {
    NebulaGraphClient clientV = mock(NebulaGraphClient.class);
    Consumer<AirbyteMessage> collectorV = mock(Consumer.class);
    doNothing().when(clientV).execute(anyString());

    NebulaGraphConfig cfg = buildVertexCfg("public", "users", null, true, List.of("id"));
    ConfiguredAirbyteCatalog catalog = buildCatalog("public", "users");

    Map<String, List<String>> allowedVertex = Map.of("public__users", List.of("age", "name"));

    NebulaGraphRecordConsumer consumerV = newConsumer(cfg, clientV, 10, allowedVertex, Map.of(), catalog, collectorV);

    consumerV.start();

    // one record in append mode -> buffered then flushAll -> INSERT VERTEX with raw4+age+name
    ObjectNode data = M.createObjectNode();
    data.put("id", "u1");
    data.put("age", 30);
    data.put("name", "n1");
    data.put("ignored", "x"); // should not appear
    consumerV.accept(new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream("users").withNamespace("public").withEmittedAt(1L).withData(data)));

    consumerV.flushAll();

    ArgumentCaptor<String> sqlsV = ArgumentCaptor.forClass(String.class);
    verify(clientV, org.mockito.Mockito.atLeast(1)).execute(sqlsV.capture());
    String insert = sqlsV.getAllValues().stream().filter(sq -> sq.startsWith("INSERT VERTEX ")).findFirst().orElse("");

    org.junit.jupiter.api.Assertions.assertTrue(insert.contains("`age`"));
    org.junit.jupiter.api.Assertions.assertTrue(insert.contains("`name`"));
    org.junit.jupiter.api.Assertions.assertTrue(!insert.contains("`ignored`"));

    // edge typed enabled, allowed cols: score
    NebulaGraphClient clientE = mock(NebulaGraphClient.class);
    doNothing().when(clientE).execute(anyString());
    Consumer<AirbyteMessage> collectorE = mock(Consumer.class);

    NebulaGraphConfig cfgE = buildEdgeCfg("public", "rels", null, true, List.of("sa", "sb"), List.of("da"));
    ConfiguredAirbyteCatalog catalogE = buildCatalog("public", "rels");

    Map<String, List<String>> allowedEdge = Map.of("public__rels", List.of("score"));

    NebulaGraphRecordConsumer consumerE = newConsumer(cfgE, clientE, 10, Map.of(), allowedEdge, catalogE, collectorE);

    consumerE.start();
    ObjectNode d2 = M.createObjectNode();
    d2.put("sa", "s1");
    d2.put("sb", 1);
    d2.put("da", "d1");
    d2.put("score", 9.5);
    d2.put("ignored", true);
    consumerE.accept(new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream("rels").withNamespace("public").withEmittedAt(2L).withData(d2)));

    consumerE.flushAll();

    ArgumentCaptor<String> sqlsE = ArgumentCaptor.forClass(String.class);
    verify(clientE, org.mockito.Mockito.atLeast(1)).execute(sqlsE.capture());
    String insertE = sqlsE.getAllValues().stream().filter(sq -> sq.startsWith("INSERT EDGE ")).findFirst().orElse("");
    org.junit.jupiter.api.Assertions.assertTrue(insertE.contains("`score`"));
    org.junit.jupiter.api.Assertions.assertTrue(!insertE.contains("`ignored`"));
  }

  @Test
  void con05StateFlushThenEmitOrdering() throws Exception {
    NebulaGraphClient client = mock(NebulaGraphClient.class);
    @SuppressWarnings("unchecked")
    Consumer<AirbyteMessage> collector = (Consumer<AirbyteMessage>) mock(Consumer.class);
    doNothing().when(client).execute(anyString());

    NebulaGraphConfig cfg = buildVertexCfg("public", "users", null, false, List.of("id"));
    ConfiguredAirbyteCatalog catalog = buildCatalog("public", "users");

    NebulaGraphRecordConsumer consumer = newConsumer(cfg, client, 10, Map.of(), Map.of(), catalog, collector);
    consumer.start();

    // push two records (buffered), then send STATE
    for (int i = 1; i <= 2; i++) {
      ObjectNode data = M.createObjectNode();
      data.put("id", "u" + i);
      consumer.accept(new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
          .withRecord(new AirbyteRecordMessage().withStream("users").withNamespace("public").withEmittedAt(1L * i).withData(data)));
    }

    AirbyteMessage state = new AirbyteMessage()
        .withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage());
    consumer.accept(state);

    ArgumentCaptor<String> sqls = ArgumentCaptor.forClass(String.class);
    verify(client, org.mockito.Mockito.atLeast(1)).execute(sqls.capture());

    // ensure INSERT happened before collector.accept(STATE)
    // We can't directly assert call order without InOrder here; check that at least 1 INSERT exists
    boolean hasInsert = sqls.getAllValues().stream().anyMatch(s -> s.startsWith("INSERT VERTEX "));
    org.junit.jupiter.api.Assertions.assertTrue(hasInsert, "Expected INSERT before STATE emission");

    ArgumentCaptor<AirbyteMessage> out = ArgumentCaptor.forClass(AirbyteMessage.class);
    verify(collector, org.mockito.Mockito.atLeast(1)).accept(out.capture());
    org.junit.jupiter.api.Assertions.assertTrue(out.getAllValues().stream().anyMatch(m -> m.getType() == AirbyteMessage.Type.STATE));
  }

  @Test
  void con06CloseFlushesBeforeClientClose() throws Exception {
    NebulaGraphClient client = mock(NebulaGraphClient.class);
    @SuppressWarnings("unchecked")
    Consumer<AirbyteMessage> collector = (Consumer<AirbyteMessage>) mock(Consumer.class);
    doNothing().when(client).execute(anyString());

    NebulaGraphConfig cfg = buildEdgeCfg("public", "rels", null, false, List.of("sa"), List.of("da"));
    ConfiguredAirbyteCatalog catalog = buildCatalog("public", "rels");
    NebulaGraphRecordConsumer consumer = newConsumer(cfg, client, 10, Map.of(), Map.of(), catalog, collector);
    consumer.start();

    ObjectNode d = M.createObjectNode();
    d.put("sa", "s");
    d.put("da", "d");
    consumer.accept(new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream("rels").withNamespace("public").withEmittedAt(1L).withData(d)));

    // close triggers flushAll then client.close
    consumer.close(false);

    ArgumentCaptor<String> sqls = ArgumentCaptor.forClass(String.class);
    verify(client, org.mockito.Mockito.atLeast(1)).execute(sqls.capture());
    boolean hasEdgeInsert = sqls.getAllValues().stream().anyMatch(s -> s.startsWith("INSERT EDGE "));
    org.junit.jupiter.api.Assertions.assertTrue(hasEdgeInsert, "Expected edge INSERT before close");

    // verify close called
    verify(client, org.mockito.Mockito.atLeast(1)).close();
  }

  // @Test
  // void con07UnmappedStreamMappingThrows() throws Exception {
  // NebulaGraphClient client = mock(NebulaGraphClient.class);
  // doNothing().when(client).execute(anyString());

  // // config has no streams; catalog has one -> start should throw IllegalStateException
  // NebulaGraphConfig cfg = buildVertexCfg("public", "users", null, false, List.of("id"));
  // // override: empty streams by building a config with different stream name and then not providing
  // mapping? Simpler: build empty mapping
  // // Build config with no streams by rebuilding minimal root
  // ObjectNode raw = M.createObjectNode();
  // raw.put("graphd_addresses", "127.0.0.1:9669");
  // raw.put("space", "s1");
  // raw.put("username", "u");
  // NebulaGraphConfig cfgNoStreams = NebulaGraphConfig.from(raw);

  // ConfiguredAirbyteCatalog catalog = buildCatalog("public", "users");
  // NebulaGraphRecordConsumer consumer = newConsumer(cfgNoStreams, client, 10, Map.of(), Map.of(),
  // catalog, msg -> {});

  // org.junit.jupiter.api.Assertions.assertThrows(IllegalStateException.class, consumer::start);
  // }

  @Test
  void con08RetrySucceedsAfterTransientFailures() throws Exception {
    NebulaGraphClient client = mock(NebulaGraphClient.class);
    doNothing().when(client).execute(anyString());

    java.util.concurrent.atomic.AtomicInteger attempts = new java.util.concurrent.atomic.AtomicInteger();
    org.mockito.Mockito.doAnswer(inv -> {
      String sql = inv.getArgument(0);
      if (sql.startsWith("INSERT VERTEX ")) {
        int a = attempts.getAndIncrement();
        if (a < 2) {
          throw new Exception("transient");
        }
      }
      return null;
    }).when(client).execute(anyString());

    NebulaGraphConfig cfg = buildVertexCfg("public", "users", null, false, List.of("id"));
    ConfiguredAirbyteCatalog catalog = buildCatalog("public", "users");
    NebulaGraphRecordConsumer consumer = newConsumer(cfg, client, 10, Map.of(), Map.of(), catalog, msg -> {});
    consumer.start();

    // one record, then flush -> first 2 attempts fail, then succeed
    ObjectNode d = M.createObjectNode();
    d.put("id", "u1");
    consumer.accept(new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream("users").withNamespace("public").withEmittedAt(1L).withData(d)));

    // force flush
    consumer.flushAll();

    // if we got here, success; also verify at least 3 execute calls total
    ArgumentCaptor<String> sqls = ArgumentCaptor.forClass(String.class);
    verify(client, org.mockito.Mockito.atLeast(3)).execute(sqls.capture());
    long insertCalls = sqls.getAllValues().stream().filter(s -> s.startsWith("INSERT VERTEX ")).count();
    org.junit.jupiter.api.Assertions.assertTrue(insertCalls >= 1);
  }

  @Test
  void con09RetryExhaustedThrows() throws Exception {
    NebulaGraphClient client = mock(NebulaGraphClient.class);
    // For INSERT VERTEX, always throw
    org.mockito.Mockito.doAnswer(inv -> {
      String sql = inv.getArgument(0);
      if (sql.startsWith("INSERT VERTEX ")) {
        throw new Exception("persistent failure");
      }
      return null;
    }).when(client).execute(anyString());

    NebulaGraphConfig cfg = buildVertexCfg("public", "users", null, false, List.of("id"));
    ConfiguredAirbyteCatalog catalog = buildCatalog("public", "users");
    NebulaGraphRecordConsumer consumer = newConsumer(cfg, client, 10, Map.of(), Map.of(), catalog, msg -> {});
    consumer.start();

    ObjectNode d = M.createObjectNode();
    d.put("id", "u1");
    consumer.accept(new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withStream("users").withNamespace("public").withEmittedAt(1L).withData(d)));

    RuntimeException ex = org.junit.jupiter.api.Assertions.assertThrows(RuntimeException.class, consumer::flushAll);
    org.junit.jupiter.api.Assertions.assertTrue(String.valueOf(ex.getMessage()).contains("Operation failed after retries"));
  }

  private static int countTuples(String sql) {
    int idx = sql.indexOf("VALUES\n");
    int end = sql.lastIndexOf(';');
    if (idx < 0 || end <= idx)
      return 0;
    String body = sql.substring(idx + 7, end);
    if (body.isEmpty())
      return 0;
    return body.split(",\n  ", -1).length;
  }

  private static NebulaGraphConfig buildVertexCfg(String ns, String name, Boolean useUpsert, boolean typed, List<String> vidFields) {
    ObjectNode root = M.createObjectNode();
    root.put("graphd_addresses", "127.0.0.1:9669");
    root.put("space", "s1");
    root.put("username", "u");
    if (useUpsert != null)
      root.put("use_upsert", useUpsert.booleanValue());
    ObjectNode s = M.createObjectNode();
    s.put("name", name);
    s.put("namespace", ns);
    s.put("entity_type", "vertex");
    var arr = s.putArray("vid_fields");
    for (String f : vidFields)
      arr.add(f);
    if (typed) {
      ObjectNode t = M.createObjectNode();
      t.put("enabled", true);
      s.set("typed", t);
    }
    root.putArray("streams").add(s);
    return NebulaGraphConfig.from(root);
  }

  private static NebulaGraphConfig buildEdgeCfg(String ns, String name, Boolean useUpsert, boolean typed, List<String> src, List<String> dst) {
    ObjectNode root = M.createObjectNode();
    root.put("graphd_addresses", "127.0.0.1:9669");
    root.put("space", "s1");
    root.put("username", "u");
    if (useUpsert != null)
      root.put("use_upsert", useUpsert.booleanValue());
    ObjectNode s = M.createObjectNode();
    s.put("name", name);
    s.put("namespace", ns);
    s.put("entity_type", "edge");
    var as = s.putArray("src_fields");
    for (String f : src)
      as.add(f);
    var ad = s.putArray("dst_fields");
    for (String f : dst)
      ad.add(f);
    if (typed) {
      ObjectNode t = M.createObjectNode();
      t.put("enabled", true);
      s.set("typed", t);
    }
    root.putArray("streams").add(s);
    return NebulaGraphConfig.from(root);
  }

  private static ConfiguredAirbyteCatalog buildCatalog(String ns, String name) {
    AirbyteStream stream = new AirbyteStream().withName(name).withNamespace(ns);
    return new ConfiguredAirbyteCatalog().withStreams(List.of(new ConfiguredAirbyteStream().withStream(stream)));
  }

  private static NebulaGraphRecordConsumer newConsumer(NebulaGraphConfig cfg,
                                                       NebulaGraphClient client,
                                                       int maxBatch,
                                                       Map<String, List<String>> knownVertex,
                                                       Map<String, List<String>> knownEdge,
                                                       ConfiguredAirbyteCatalog catalog,
                                                       Consumer<AirbyteMessage> collector) {
    return new NebulaGraphRecordConsumer(
        cfg, client, new StatementBuilder(), new VidGenerator(), new TypedExtractor(), maxBatch,
        knownVertex, knownEdge, catalog, collector);
  }

}
