/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.nebulagraph;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.commons.json.Jsons;
import java.io.File;
import java.util.HashSet;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Timeout;
import org.testcontainers.containers.DockerComposeContainer;
import org.testcontainers.containers.wait.strategy.Wait;

@Timeout(value = 5,
         unit = TimeUnit.MINUTES)
public class NebulaGraphDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private DockerComposeContainer<?> nebula;
  private String spaceName;
  private String graphdHost;
  private Integer graphdPort;
  private boolean nebulaStarted;

  @Override
  protected String getImageName() {
    return "airbyte/destination-nebulagraph:dev";
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    return "";
  }

  @Override
  protected JsonNode getConfig() {
    ensureNebulaStarted();
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("graphd_addresses", graphdHost + ":" + graphdPort)
        .put("space", spaceName)
        .put("username", "root")
        .put("password", "nebula")
        .put("create_space_if_missing", true)
        .put("use_upsert", false)
        .put("streams", Jsons.jsonNode(new Object[] {
          ImmutableMap.builder()
              .put("name", "users")
              .put("namespace", "public")
              .put("entity_type", "vertex")
              .put("vid_fields", Jsons.jsonNode(new String[] {"tenant_id", "user_id"}))
              .build(),
          ImmutableMap.builder()
              .put("name", "orders_rel")
              .put("namespace", "public")
              .put("entity_type", "edge")
              .put("edge_type", "public__users_to_orders")
              .put("src_fields", Jsons.jsonNode(new String[] {"tenant_id", "user_id"}))
              .put("dst_fields", Jsons.jsonNode(new String[] {"tenant_id", "order_id"}))
              .put("rank_field", "version")
              .build()
        }))
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    ensureNebulaStarted();
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("graphd_addresses", graphdHost + ":" + (graphdPort + 1))
        .put("space", spaceName)
        .put("username", "root")
        .put("password", "nebula")
        .build());
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) {
    spaceName = "it_space_" + UUID.randomUUID().toString().replace("-", "").substring(0, 8);
    ensureNebulaStarted();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    try {
      if (nebulaStarted) {
        final NebulaGraphConfig cfg = NebulaGraphConfig.from(getConfig());
        final StatementBuilder sb = new StatementBuilder();
        try (NebulaGraphClient client = NebulaGraphClient.connect(cfg)) {
          try {
            client.execute("DROP SPACE " + sb.q(cfg.space));
          } catch (Exception dropEx) {
            System.err.println("WARN: failed to drop space in tearDown: " + dropEx.getMessage());
          }
        }
      }
    } catch (Exception outer) {
      System.err.println("WARN: tearDown encountered error: " + outer.getMessage());
    }

    if (nebula != null && nebulaStarted) {
      nebula.stop();
    }
  }

  private synchronized void ensureNebulaStarted() {
    if (nebulaStarted)
      return;
    File compose = new File("src/test-integration/resources/nebulagraph/docker-compose.yaml");
    Assertions.assertTrue(compose.exists(), "Missing NebulaGraph compose file: " + compose.getAbsolutePath());

    nebula = new DockerComposeContainer<>(compose)
        .withExposedService("graphd", 9669, Wait.forListeningPort());
    nebula.start();

    graphdHost = nebula.getServiceHost("graphd", 9669);
    graphdPort = nebula.getServicePort("graphd", 9669);
    nebulaStarted = true;
  }

  @Override
  protected java.util.List<com.fasterxml.jackson.databind.JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                                                                    final String streamName,
                                                                                    final String namespace,
                                                                                    final JsonNode streamSchema)
      throws Exception {
    final NebulaGraphConfig cfg = NebulaGraphConfig.from(getConfig());
    final StatementBuilder sb = new StatementBuilder();

    // Optional mapping from config.streams; fall back to vertex if unmapped
    final java.util.Map<String, NebulaGraphConfig.StreamConfig> byKey = new java.util.LinkedHashMap<>();
    if (cfg.streams != null) {
      for (NebulaGraphConfig.StreamConfig s : cfg.streams) {
        final String k = deriveKey(s.namespace, s.name);
        byKey.put(k, s);
      }
    }
    final String key = deriveKey(namespace, streamName);
    final NebulaGraphConfig.StreamConfig sc = byKey.get(key);

    final java.util.List<com.fasterxml.jackson.databind.JsonNode> out = new java.util.ArrayList<>();
    try (NebulaGraphClient client = NebulaGraphClient.connect(cfg)) {
      client.execute("USE " + sb.q(cfg.space));

      final String sql;
      final boolean isEdge = (sc != null && "edge".equals(sc.entityType));
      if (!isEdge) {
        final String tag =
            (namespace == null || namespace.isEmpty()) ? streamName.toLowerCase() : (namespace.toLowerCase() + "__" + streamName.toLowerCase());
        // Quote the tag when qualifying properties. Without quoting, tags containing hyphens, colons,
        // diacritics,
        // or substrings that look like keywords (e.g. "with") cause parser errors (observed: "syntax error
        // near `with'").
        // Example needed form: v.`stream-with:spécial:character_names`.`_airbyte_data`
        sql = "MATCH (v:" + sb.q(tag) + ") RETURN v." + sb.q(tag) + ".`_airbyte_data` AS d, v." + sb.q(tag) + ".`_airbyte_emitted_at` AS e, v."
            + sb.q(tag) + ".`_airbyte_ab_id` AS a ORDER BY e ASC, a ASC";
      } else {
        final String edgeType = (sc.edgeType != null && !sc.edgeType.isEmpty()) ? sc.edgeType.toLowerCase()
            : ((namespace == null || namespace.isEmpty()) ? streamName.toLowerCase() : (namespace.toLowerCase() + "__" + streamName.toLowerCase()));
        sql = "MATCH ()-[e:" + sb.q(edgeType) + "]->() RETURN e." + sb.q(edgeType) + ".`_airbyte_data` AS d, e." + sb.q(edgeType)
            + ".`_airbyte_emitted_at` AS e, e." + sb.q(edgeType) + ".`_airbyte_ab_id` AS a ORDER BY e ASC, a ASC";
      }

      // fetch only the raw json column alias 'd' and parse
      java.util.List<String> jsons = client.queryJsonColumn(sql, "d");
      System.out.println("[retrieveRecords] stream=" + streamName + " rows=" + (jsons == null ? 0 : jsons.size()) + " sql=" + sql);
      if (jsons != null) {
        for (int i = 0; i < jsons.size(); i++) {
          if (i < 5)
            System.out.println("[retrieveRecords] sample json[" + i + "]=" + jsons.get(i));
        }
      }
      // Fallback: if all values null, attempt alternate MATCH syntax aliasing vertex directly
      boolean allNull = true;
      if (jsons != null) {
        for (String s : jsons) {
          if (s != null && !s.isEmpty() && !"NULL".equalsIgnoreCase(s)) {
            allNull = false;
            break;
          }
        }
      }
      if (allNull) {
        final String altSql;
        if (!isEdge) {
          final String tag =
              (namespace == null || namespace.isEmpty()) ? streamName.toLowerCase() : (namespace.toLowerCase() + "__" + streamName.toLowerCase());
          altSql = "MATCH (v:" + sb.q(tag) + ") RETURN properties(v).`_airbyte_data` AS d ORDER BY id(v)"; // attempt via properties() map
        } else {
          final String edgeType = (sc.edgeType != null && !sc.edgeType.isEmpty()) ? sc.edgeType.toLowerCase()
              : ((namespace == null || namespace.isEmpty()) ? streamName.toLowerCase() : (namespace.toLowerCase() + "__" + streamName.toLowerCase()));
          altSql = "MATCH ()-[e:" + sb.q(edgeType) + "]->() RETURN properties(e).`_airbyte_data` AS d ORDER BY id(e)";
        }
        try {
          java.util.List<String> alt = client.queryJsonColumn(altSql, "d");
          System.out.println("[retrieveRecords] fallback query rows=" + (alt == null ? 0 : alt.size()) + " sql=" + altSql);
          if (alt != null) {
            jsons = alt; // overwrite
            for (int i = 0; i < alt.size(); i++) {
              if (i < 5)
                System.out.println("[retrieveRecords] fallback sample json[" + i + "]=" + alt.get(i));
            }
          }
        } catch (Exception fe) {
          System.out.println("[retrieveRecords] fallback query failed: " + fe.getMessage());
        }
      }
      for (String js : jsons) {
        if (js == null || js.isEmpty() || "NULL".equalsIgnoreCase(js)) {
          out.add(io.airbyte.commons.json.Jsons.emptyObject());
        } else {
          out.add(io.airbyte.commons.json.Jsons.deserialize(js));
        }
      }
    }

    return out;
  }

  private static String deriveKey(String namespace, String name) {
    final String ns = namespace == null ? null : namespace.trim().toLowerCase();
    final String nm = name == null ? null : name.trim().toLowerCase();
    return (ns == null || ns.isEmpty()) ? nm : ns + "__" + nm;
  }

}
