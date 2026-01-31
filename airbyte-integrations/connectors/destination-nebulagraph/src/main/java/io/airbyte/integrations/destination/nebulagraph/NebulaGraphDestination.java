/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.nebulagraph;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer;
import io.airbyte.cdk.integrations.base.Destination;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * NebulaGraph Destination wired to Airbyte CDK.
 */
public final class NebulaGraphDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(NebulaGraphDestination.class);

  public static void main(String[] args) throws Exception {
    final Destination destination = new NebulaGraphDestination();
    LOGGER.info("Starting destination: {}", NebulaGraphDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("Completed destination: {}", NebulaGraphDestination.class);
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      // Parse and perform minimal schema provisioning using a no-op client for now.
      final NebulaGraphConfig cfg = NebulaGraphConfig.from(config);
      final StatementBuilder sb = new StatementBuilder();
      try (NebulaGraphClient client = NebulaGraphClient.connect(cfg)) {
        ensureSpaceExists(client, sb, cfg);
      }
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("NebulaGraphDestination.check failed", e);
      return new AirbyteConnectionStatus().withStatus(Status.FAILED)
          .withMessage(String.valueOf(e.getMessage()));
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector) {
    final NebulaGraphConfig cfg = NebulaGraphConfig.from(config);
    final StatementBuilder sb = new StatementBuilder();
    final NebulaGraphClient client = NebulaGraphClient.connect(cfg);
    final int maxBatch = cfg.maxBatchRecords;

    // Build stream mapping for quick lookup
    final Map<String, NebulaGraphConfig.StreamConfig> byKey = new LinkedHashMap<>();
    if (cfg.streams != null) {
      for (NebulaGraphConfig.StreamConfig s : cfg.streams) {
        final String key = deriveTagName(s.namespace, s.name);
        byKey.put(key, s);
      }
    }

    // Startup-time schema upgrade (ensure base schema and typed columns). No runtime DDL.
    final Map<String, List<String>> knownVertexTypedCols = new LinkedHashMap<>();
    final Map<String, List<String>> knownEdgeTypedCols = new LinkedHashMap<>();
    if (catalog != null && catalog.getStreams() != null) {
      final SchemaManager sm = new SchemaManager(client, sb);
      try {
        ensureSpaceExists(client, sb, cfg);
      } catch (Exception e) {
        try {
          client.close();
        } catch (Exception ignore) {}
        throw new RuntimeException("failed to USE space: " + cfg.space, e);
      }

      // Ensure base Tags for all streams; only create Edge types for explicitly defined edge streams
      for (ConfiguredAirbyteStream s : catalog.getStreams()) {
        final String ns = s.getStream() == null ? null : s.getStream().getNamespace();
        final String nm = s.getStream() == null ? null : s.getStream().getName();
        final String key = deriveTagName(ns, nm);
        final NebulaGraphConfig.StreamConfig sc = byKey.get(key);
        if (sc == null || "vertex".equals(sc.entityType)) {
          sm.ensureTagExists(deriveTagName(ns, nm));
        } else {
          final String et = (sc.edgeType != null && !sc.edgeType.isEmpty()) ? toSafeLower(sc.edgeType) : deriveTagName(ns, nm);
          sm.ensureEdgeTypeExists(et);
        }
      }

      // Derive typed columns from JSON Schema and apply once; record known typed columns per stream
      for (ConfiguredAirbyteStream s : catalog.getStreams()) {
        final String ns = s.getStream() == null ? null : s.getStream().getNamespace();
        final String nm = s.getStream() == null ? null : s.getStream().getName();
        final String key = deriveTagName(ns, nm);
        final NebulaGraphConfig.StreamConfig sc = byKey.get(key);
        if (sc == null || !sc.typedEnabled) {
          continue;
        }
        final Map<String, Class<?>> typedCols = deriveTypedColumnsFromJsonSchema(s.getStream().getJsonSchema());
        if (typedCols.isEmpty()) {
          continue;
        }
        if ("vertex".equals(sc.entityType)) {
          final String tag = deriveTagName(ns, nm);
          sm.addTagColumnsIfMissing(tag, typedCols);
          knownVertexTypedCols.put(key, new ArrayList<>(typedCols.keySet()));
        } else {
          final String et = (sc.edgeType != null && !sc.edgeType.isEmpty()) ? toSafeLower(sc.edgeType) : deriveTagName(ns, nm);
          sm.addEdgeColumnsIfMissing(et, typedCols);
          knownEdgeTypedCols.put(key, new ArrayList<>(typedCols.keySet()));
        }
      }
    }

    return new NebulaGraphRecordConsumer(
        cfg,
        client,
        sb,
        new VidGenerator(),
        new TypedExtractor(),
        maxBatch,
        knownVertexTypedCols,
        knownEdgeTypedCols,
        catalog,
        outputRecordCollector);
  }

  private static String deriveTagName(String namespace, String name) {
    String ns = toSafeLower(namespace);
    String nm = toSafeLower(name);
    return (ns == null || ns.isEmpty()) ? nm : ns + "__" + nm;
  }

  private static String toSafeLower(String s) {
    return s == null ? null : s.trim().toLowerCase();
  }

  /**
   * Ensure target space exists and can be USED. If missing and allowed, create it with
   * vid_type=FIXED_STRING(N). Retries USE a few times after creation to allow metadata to settle.
   */
  private static void ensureSpaceExists(NebulaGraphClient client, StatementBuilder sb, NebulaGraphConfig cfg) throws Exception {
    try {
      client.execute("USE " + sb.q(cfg.space));
      return;
    } catch (Exception first) {
      if (!cfg.createSpaceIfMissing) {
        throw new RuntimeException("Space does not exist and auto-create is disabled: " + cfg.space, first);
      }
      // Quick readiness probe: wait until at least one storaged is ONLINE (up to ~90s),
      // then proceed to CREATE/USE retries. If probe fails, continue anyway.
      try {
        final long readyDeadline = System.currentTimeMillis() + 5_000L;
        final int[] readyBackoffMs = new int[] {200, 400, 800, 1600, 3200, 6400, 12800};
        int readyIdx = 0;
        while (System.currentTimeMillis() < readyDeadline) {
          try {
            java.util.List<String> statuses = client.queryJsonColumn("SHOW HOSTS STORAGE", "Status");
            boolean anyOnline = false;
            if (statuses != null) {
              for (String s : statuses) {
                if (s != null && s.toUpperCase().contains("ONLINE")) {
                  anyOnline = true;
                  break;
                }
              }
            }
            if (anyOnline) {
              break;
            }
          } catch (Exception ignore) {
            // ignore and retry until deadline
          }
          try {
            Thread.sleep(readyBackoffMs[Math.min(readyIdx, readyBackoffMs.length - 1)]);
          } catch (InterruptedException ie) {
            Thread.currentThread().interrupt();
            break;
          }
          if (readyIdx < readyBackoffMs.length - 1)
            readyIdx++;
        }
      } catch (Exception ignoreProbe) {
        // best-effort readiness; continue to CREATE
      }
      // Try to create the space with FIXED_STRING(N). Include conservative defaults for
      // partition/replica.
      String create = "CREATE SPACE IF NOT EXISTS " + sb.q(cfg.space)
          + " (vid_type=FIXED_STRING(" + cfg.vidFixedStringLength + "), partition_num=1, replica_factor=1)";
      // Longer backoff for CREATE (≈180s)
      int[] createBackoffMs = new int[] {
        200, 400, 800, 1600, 3200, 6400, 12800, 25600,
      };
      Exception lastCreateErr = null;
      // Retry CREATE as storaged may not be registered yet (Host not enough)
      for (int i = 0; i < createBackoffMs.length; i++) {
        try {
          client.execute(create);
          lastCreateErr = null;
          break;
        } catch (Exception ce) {
          lastCreateErr = ce;
          String msg = String.valueOf(ce.getMessage()).toLowerCase();
          boolean transientHost = msg.contains("host not enough") || msg.contains("no host") || msg.contains("not enough host");
          if (!transientHost || i == createBackoffMs.length) {
            throw new RuntimeException("Failed to CREATE SPACE: " + cfg.space, ce);
          }
          try {
            Thread.sleep(createBackoffMs[i]);
          } catch (InterruptedException ie) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Interrupted while waiting to create space: " + cfg.space, ce);
          }
        }
      }
      // Retry USE with moderate backoff (≈50s) to wait for meta propagation.
      int[] useBackoffMs = new int[] {200, 400, 800, 1600, 3200, 6400, 12800, 25600};
      for (int i = 0; i < useBackoffMs.length; i++) {
        try {
          client.execute("USE " + sb.q(cfg.space));
          return;
        } catch (Exception retryErr) {
          if (i == useBackoffMs.length - 1) {
            throw new RuntimeException("Failed to USE space after creation: " + cfg.space, retryErr);
          }
          try {
            Thread.sleep(useBackoffMs[i]);
          } catch (InterruptedException ie) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Interrupted while waiting for space creation: " + cfg.space, retryErr);
          }
        }
      }
    }
  }

  private static Map<String, Class<?>> deriveTypedColumnsFromJsonSchema(JsonNode schema) {
    final Map<String, Class<?>> out = new LinkedHashMap<>();
    if (schema == null || !schema.isObject())
      return out;
    final JsonNode props = schema.get("properties");
    if (props == null || !props.isObject())
      return out;
    props.fields().forEachRemaining(e -> {
      final String name = e.getKey();
      final JsonNode p = e.getValue();
      final Class<?> t = mapJsonTypeToJava(p);
      if (name != null && !name.isEmpty() && t != null) {
        out.put(name, t);
      }
    });
    return out;
  }

  private static Class<?> mapJsonTypeToJava(JsonNode p) {
    if (p == null)
      return null;
    final JsonNode t = p.get("type");
    if (t == null)
      return null;
    String ts = t.isArray() && t.size() > 0 ? t.get(0).asText() : t.asText();
    if (ts == null)
      return null;
    ts = ts.trim().toLowerCase();
    if ("boolean".equals(ts))
      return Boolean.class;
    if ("integer".equals(ts))
      return Long.class;
    if ("number".equals(ts))
      return Double.class;
    if ("string".equals(ts))
      return String.class;
    return null;
  }

}
