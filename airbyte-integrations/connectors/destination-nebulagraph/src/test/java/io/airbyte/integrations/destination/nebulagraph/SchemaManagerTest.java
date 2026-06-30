/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.nebulagraph;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.atLeast;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

import java.util.LinkedHashMap;
import java.util.Map;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;

@DisplayName("SchemaManager")
class SchemaManagerTest {

  @Test
  void ensureBaseSchema() throws Exception {
    NebulaGraphClient client = mock(NebulaGraphClient.class);
    StatementBuilder sb = new StatementBuilder();
    SchemaManager sm = new SchemaManager(client, sb);

    doNothing().when(client).execute(anyString());

    sm.ensureTagExists("public__users");
    sm.ensureEdgeTypeExists("users_to_orders");

    // Capture all SQL and assert CREATE semantics
    ArgumentCaptor<String> captor = ArgumentCaptor.forClass(String.class);
    verify(client, atLeast(2)).execute(captor.capture());

    boolean tagCreated = captor.getAllValues().stream().anyMatch(sql -> sql.startsWith("CREATE TAG IF NOT EXISTS `public__users`") &&
        sql.contains("`_airbyte_data` string") &&
        sql.contains("`_airbyte_ab_id` string") &&
        sql.contains("`_airbyte_emitted_at` int64") &&
        sql.contains("`_airbyte_loaded_at` int64"));

    boolean edgeCreated = captor.getAllValues().stream().anyMatch(sql -> sql.startsWith("CREATE EDGE IF NOT EXISTS `users_to_orders`") &&
        sql.contains("`_airbyte_data` string") &&
        sql.contains("`_airbyte_ab_id` string") &&
        sql.contains("`_airbyte_emitted_at` int64") &&
        sql.contains("`_airbyte_loaded_at` int64"));

    assertTrue(tagCreated, "CREATE TAG missing or malformed");
    assertTrue(edgeCreated, "CREATE EDGE missing or malformed");
  }

  @Test
  void addTagColumnsBatchFailsThenDegradePerColumn() throws Exception {
    NebulaGraphClient client = mock(NebulaGraphClient.class);
    StatementBuilder sb = new StatementBuilder();
    SchemaManager sm = new SchemaManager(client, sb);

    // Answer: if batch ADD (with multiple columns) then throw 'already exists',
    // otherwise do nothing to allow per-column ADD to succeed.
    doAnswer(inv -> {
      String sql = inv.getArgument(0);
      if (sql.startsWith("ALTER TAG `public__users` ADD (") && sql.contains(",")) {
        throw new Exception("already exists");
      }
      return null;
    }).when(client).execute(anyString());

    // Prepare columns in a deterministic order
    Map<String, Class<?>> cols = new LinkedHashMap<>();
    cols.put("age", Long.class); // -> int64
    cols.put("active", Boolean.class); // -> bool
    cols.put("name", String.class); // -> string

    sm.addTagColumnsIfMissing("public__users", cols);

    // Verify degraded per-column ADDs present
    ArgumentCaptor<String> captor = ArgumentCaptor.forClass(String.class);
    verify(client, atLeast(3)).execute(captor.capture());

    String addAge = "ALTER TAG `public__users` ADD (`age` int64)";
    String addActive = "ALTER TAG `public__users` ADD (`active` bool)";
    String addName = "ALTER TAG `public__users` ADD (`name` string)";

    boolean hasAge = captor.getAllValues().stream().anyMatch(sql -> sql.equals(addAge));
    boolean hasActive = captor.getAllValues().stream().anyMatch(sql -> sql.equals(addActive));
    boolean hasName = captor.getAllValues().stream().anyMatch(sql -> sql.equals(addName));

    assertTrue(hasAge, "Missing per-column ADD for age");
    assertTrue(hasActive, "Missing per-column ADD for active");
    assertTrue(hasName, "Missing per-column ADD for name");
  }

  @Test
  void addEdgeColumnsBatchSuccess() throws Exception {
    NebulaGraphClient client = mock(NebulaGraphClient.class);
    StatementBuilder sb = new StatementBuilder();
    SchemaManager sm = new SchemaManager(client, sb);

    doNothing().when(client).execute(anyString());

    Map<String, Class<?>> cols = new LinkedHashMap<>();
    cols.put("score", Double.class); // -> double
    cols.put("flag", Boolean.class); // -> bool

    sm.addEdgeColumnsIfMissing("orders_edge", cols);

    ArgumentCaptor<String> captor = ArgumentCaptor.forClass(String.class);
    verify(client, atLeast(1)).execute(captor.capture());

    boolean hasBatch = captor.getAllValues().stream().anyMatch(sql -> sql.equals("ALTER EDGE `orders_edge` ADD (`score` double,`flag` bool)"));

    assertTrue(hasBatch, "Expected batch ALTER EDGE ADD not found");
  }

  @Test
  void addEdgeColumnsBatchFailsThenDegradePerColumn() throws Exception {
    NebulaGraphClient client = mock(NebulaGraphClient.class);
    StatementBuilder sb = new StatementBuilder();
    SchemaManager sm = new SchemaManager(client, sb);

    // Throw on batch ADD, succeed on per-column ADD
    doAnswer(inv -> {
      String sql = inv.getArgument(0);
      if (sql.startsWith("ALTER EDGE `orders_edge` ADD (") && sql.contains(",")) {
        throw new Exception("already exists");
      }
      return null;
    }).when(client).execute(anyString());

    Map<String, Class<?>> cols = new LinkedHashMap<>();
    cols.put("score", Double.class);
    cols.put("flag", Boolean.class);

    sm.addEdgeColumnsIfMissing("orders_edge", cols);

    ArgumentCaptor<String> captor = ArgumentCaptor.forClass(String.class);
    verify(client, atLeast(3)).execute(captor.capture());

    boolean hasScore = captor.getAllValues().stream()
        .anyMatch(sql -> sql.equals("ALTER EDGE `orders_edge` ADD (`score` double)"));
    boolean hasFlag = captor.getAllValues().stream()
        .anyMatch(sql -> sql.equals("ALTER EDGE `orders_edge` ADD (`flag` bool)"));

    assertTrue(hasScore, "Missing per-column ADD for score");
    assertTrue(hasFlag, "Missing per-column ADD for flag");
  }

  @Test
  void addTagColumnsTypePromotionAndCovers() throws Exception {
    NebulaGraphClient client = mock(NebulaGraphClient.class);
    StatementBuilder sb = new StatementBuilder();
    SchemaManager sm = new SchemaManager(client, sb);

    doNothing().when(client).execute(anyString());

    // First add INT
    Map<String, Class<?>> v1 = new LinkedHashMap<>();
    v1.put("age", Long.class); // -> int64
    sm.addTagColumnsIfMissing("public__users", v1);

    // Then promote to DOUBLE
    Map<String, Class<?>> v2 = new LinkedHashMap<>();
    v2.put("age", Double.class); // -> double (promote from int64)
    sm.addTagColumnsIfMissing("public__users", v2);

    ArgumentCaptor<String> captor = ArgumentCaptor.forClass(String.class);
    verify(client, atLeast(2)).execute(captor.capture());

    boolean hasInt = captor.getAllValues().stream()
        .anyMatch(sql -> sql.equals("ALTER TAG `public__users` ADD (`age` int64)"));
    boolean hasDouble = captor.getAllValues().stream()
        .anyMatch(sql -> sql.equals("ALTER TAG `public__users` ADD (`age` double)"));

    assertTrue(hasInt, "Expected initial INT add");
    assertTrue(hasDouble, "Expected promotion to DOUBLE");
  }

  @Test
  void addEdgeColumnsTypePromotionAndNoDegrade() throws Exception {
    NebulaGraphClient client = mock(NebulaGraphClient.class);
    StatementBuilder sb = new StatementBuilder();
    SchemaManager sm = new SchemaManager(client, sb);

    doNothing().when(client).execute(anyString());

    // Add DOUBLE first
    Map<String, Class<?>> a = new LinkedHashMap<>();
    a.put("score", Double.class);
    sm.addEdgeColumnsIfMissing("orders_edge", a);

    // Then attempt to "degrade" to INT; should keep/promote as DOUBLE
    Map<String, Class<?>> b = new LinkedHashMap<>();
    b.put("score", Long.class);
    sm.addEdgeColumnsIfMissing("orders_edge", b);

    ArgumentCaptor<String> captor = ArgumentCaptor.forClass(String.class);
    verify(client, atLeast(2)).execute(captor.capture());

    boolean hasDouble = captor.getAllValues().stream()
        .anyMatch(sql -> sql.equals("ALTER EDGE `orders_edge` ADD (`score` double)"));

    assertTrue(hasDouble, "Expected DOUBLE add to remain effective");
  }

  @Test
  void addTagColumnsBatchOtherErrorPropagates() throws Exception {
    NebulaGraphClient client = mock(NebulaGraphClient.class);
    StatementBuilder sb = new StatementBuilder();
    SchemaManager sm = new SchemaManager(client, sb);

    doAnswer(inv -> {
      throw new Exception("fatal");
    }).when(client).execute(anyString());

    Map<String, Class<?>> cols = new LinkedHashMap<>();
    cols.put("x", String.class);
    cols.put("y", Boolean.class);

    assertThrows(RuntimeException.class, () -> sm.addTagColumnsIfMissing("t", cols));
  }

}
