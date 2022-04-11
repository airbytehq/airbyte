/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs.WorkerEnvironment;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class EnvConfigsTest {

  private Map<String, String> envMap;
  private EnvConfigs config;

  @BeforeEach
  void setUp() {
    envMap = new HashMap<>();
    config = new EnvConfigs(envMap);
  }

  @Test
  void ensureGetEnvBehavior() {
    assertNull(System.getenv("MY_RANDOM_VAR_1234"));
  }

  @Test
  void testAirbyteRole() {
    envMap.put(EnvConfigs.AIRBYTE_ROLE, null);
    assertNull(config.getAirbyteRole());

    envMap.put(EnvConfigs.AIRBYTE_ROLE, "dev");
    assertEquals("dev", config.getAirbyteRole());
  }

  @Test
  void testAirbyteVersion() {
    envMap.put(EnvConfigs.AIRBYTE_VERSION, null);
    assertThrows(IllegalArgumentException.class, () -> config.getAirbyteVersion());

    envMap.put(EnvConfigs.AIRBYTE_VERSION, "dev");
    assertEquals(new AirbyteVersion("dev"), config.getAirbyteVersion());
  }

  @Test
  void testWorkspaceRoot() {
    envMap.put(EnvConfigs.WORKSPACE_ROOT, null);
    assertThrows(IllegalArgumentException.class, () -> config.getWorkspaceRoot());

    envMap.put(EnvConfigs.WORKSPACE_ROOT, "abc/def");
    assertEquals(Paths.get("abc/def"), config.getWorkspaceRoot());
  }

  @Test
  void testLocalRoot() {
    envMap.put(EnvConfigs.LOCAL_ROOT, null);
    assertThrows(IllegalArgumentException.class, () -> config.getLocalRoot());

    envMap.put(EnvConfigs.LOCAL_ROOT, "abc/def");
    assertEquals(Paths.get("abc/def"), config.getLocalRoot());
  }

  @Test
  void testConfigRoot() {
    envMap.put(EnvConfigs.CONFIG_ROOT, null);
    assertThrows(IllegalArgumentException.class, () -> config.getConfigRoot());

    envMap.put(EnvConfigs.CONFIG_ROOT, "a/b");
    assertEquals(Paths.get("a/b"), config.getConfigRoot());
  }

  @Test
  void testGetDatabaseUser() {
    envMap.put(EnvConfigs.DATABASE_USER, null);
    assertThrows(IllegalArgumentException.class, () -> config.getDatabaseUser());

    envMap.put(EnvConfigs.DATABASE_USER, "user");
    assertEquals("user", config.getDatabaseUser());
  }

  @Test
  void testGetDatabasePassword() {
    envMap.put(EnvConfigs.DATABASE_PASSWORD, null);
    assertThrows(IllegalArgumentException.class, () -> config.getDatabasePassword());

    envMap.put(EnvConfigs.DATABASE_PASSWORD, "password");
    assertEquals("password", config.getDatabasePassword());
  }

  @Test
  void testGetDatabaseUrl() {
    envMap.put(EnvConfigs.DATABASE_URL, null);
    assertThrows(IllegalArgumentException.class, () -> config.getDatabaseUrl());

    envMap.put(EnvConfigs.DATABASE_URL, "url");
    assertEquals("url", config.getDatabaseUrl());
  }

  @Test
  void testGetWorkspaceDockerMount() {
    envMap.put(EnvConfigs.WORKSPACE_DOCKER_MOUNT, null);
    envMap.put(EnvConfigs.WORKSPACE_ROOT, "abc/def");
    assertEquals("abc/def", config.getWorkspaceDockerMount());

    envMap.put(EnvConfigs.WORKSPACE_DOCKER_MOUNT, "root");
    envMap.put(EnvConfigs.WORKSPACE_ROOT, "abc/def");
    assertEquals("root", config.getWorkspaceDockerMount());

    envMap.put(EnvConfigs.WORKSPACE_DOCKER_MOUNT, null);
    envMap.put(EnvConfigs.WORKSPACE_ROOT, null);
    assertThrows(IllegalArgumentException.class, () -> config.getWorkspaceDockerMount());
  }

  @Test
  void testGetLocalDockerMount() {
    envMap.put(EnvConfigs.LOCAL_DOCKER_MOUNT, null);
    envMap.put(EnvConfigs.LOCAL_ROOT, "abc/def");
    assertEquals("abc/def", config.getLocalDockerMount());

    envMap.put(EnvConfigs.LOCAL_DOCKER_MOUNT, "root");
    envMap.put(EnvConfigs.LOCAL_ROOT, "abc/def");
    assertEquals("root", config.getLocalDockerMount());

    envMap.put(EnvConfigs.LOCAL_DOCKER_MOUNT, null);
    envMap.put(EnvConfigs.LOCAL_ROOT, null);
    assertThrows(IllegalArgumentException.class, () -> config.getLocalDockerMount());
  }

  @Test
  void testDockerNetwork() {
    envMap.put(EnvConfigs.DOCKER_NETWORK, null);
    assertEquals("host", config.getDockerNetwork());

    envMap.put(EnvConfigs.DOCKER_NETWORK, "abc");
    assertEquals("abc", config.getDockerNetwork());
  }

  @Test
  void testTrackingStrategy() {
    envMap.put(EnvConfigs.TRACKING_STRATEGY, null);
    assertEquals(Configs.TrackingStrategy.LOGGING, config.getTrackingStrategy());

    envMap.put(EnvConfigs.TRACKING_STRATEGY, "abc");
    assertEquals(Configs.TrackingStrategy.LOGGING, config.getTrackingStrategy());

    envMap.put(EnvConfigs.TRACKING_STRATEGY, "logging");
    assertEquals(Configs.TrackingStrategy.LOGGING, config.getTrackingStrategy());

    envMap.put(EnvConfigs.TRACKING_STRATEGY, "segment");
    assertEquals(Configs.TrackingStrategy.SEGMENT, config.getTrackingStrategy());

    envMap.put(EnvConfigs.TRACKING_STRATEGY, "LOGGING");
    assertEquals(Configs.TrackingStrategy.LOGGING, config.getTrackingStrategy());
  }

  @Test
  void testworkerKubeTolerations() {
    envMap.put(EnvConfigs.JOB_KUBE_TOLERATIONS, null);
    assertEquals(config.getJobKubeTolerations(), List.of());

    envMap.put(EnvConfigs.JOB_KUBE_TOLERATIONS, ";;;");
    assertEquals(config.getJobKubeTolerations(), List.of());

    envMap.put(EnvConfigs.JOB_KUBE_TOLERATIONS, "key=k,value=v;");
    assertEquals(config.getJobKubeTolerations(), List.of());

    envMap.put(EnvConfigs.JOB_KUBE_TOLERATIONS, "key=airbyte-server,operator=Exists,effect=NoSchedule");
    assertEquals(config.getJobKubeTolerations(), List.of(new TolerationPOJO("airbyte-server", "NoSchedule", null, "Exists")));

    envMap.put(EnvConfigs.JOB_KUBE_TOLERATIONS, "key=airbyte-server,operator=Equals,value=true,effect=NoSchedule");
    assertEquals(config.getJobKubeTolerations(), List.of(new TolerationPOJO("airbyte-server", "NoSchedule", "true", "Equals")));

    envMap.put(EnvConfigs.JOB_KUBE_TOLERATIONS,
        "key=airbyte-server,operator=Exists,effect=NoSchedule;key=airbyte-server,operator=Equals,value=true,effect=NoSchedule");
    assertEquals(config.getJobKubeTolerations(), List.of(
        new TolerationPOJO("airbyte-server", "NoSchedule", null, "Exists"),
        new TolerationPOJO("airbyte-server", "NoSchedule", "true", "Equals")));
  }

  @Test
  void testSplitKVPairsFromEnvString() {
    String input = "key1=value1,key2=value2";
    Map<String, String> map = config.splitKVPairsFromEnvString(input);
    assertNotNull(map);
    assertEquals(2, map.size());
    assertEquals(map, Map.of("key1", "value1", "key2", "value2"));

    input = "key=k,,;$%&^#";
    map = config.splitKVPairsFromEnvString(input);
    assertNotNull(map);
    assertEquals(map, Map.of("key", "k"));

    input = null;
    map = config.splitKVPairsFromEnvString(input);
    assertNull(map);

    input = " key1= value1,  key2 =    value2";
    map = config.splitKVPairsFromEnvString(input);
    assertNotNull(map);
    assertEquals(map, Map.of("key1", "value1", "key2", "value2"));

    input = "key1:value1,key2:value2";
    map = config.splitKVPairsFromEnvString(input);
    assertNull(map);
  }

  @Test
  void testJobKubeNodeSelectors() {
    envMap.put(EnvConfigs.JOB_KUBE_NODE_SELECTORS, null);
    assertNull(config.getJobKubeNodeSelectors());

    envMap.put(EnvConfigs.JOB_KUBE_NODE_SELECTORS, ",,,");
    assertNull(config.getJobKubeNodeSelectors());

    envMap.put(EnvConfigs.JOB_KUBE_NODE_SELECTORS, "key=k,,;$%&^#");
    assertEquals(config.getJobKubeNodeSelectors(), Map.of("key", "k"));

    envMap.put(EnvConfigs.JOB_KUBE_NODE_SELECTORS, "one=two");
    assertEquals(config.getJobKubeNodeSelectors(), Map.of("one", "two"));

    envMap.put(EnvConfigs.JOB_KUBE_NODE_SELECTORS, "airbyte=server,something=nothing");
    assertEquals(config.getJobKubeNodeSelectors(), Map.of("airbyte", "server", "something", "nothing"));
  }

  @Test
  void testSpecKubeNodeSelectors() {
    envMap.put(EnvConfigs.SPEC_JOB_KUBE_NODE_SELECTORS, null);
    assertNull(config.getSpecJobKubeNodeSelectors());

    envMap.put(EnvConfigs.SPEC_JOB_KUBE_NODE_SELECTORS, ",,,");
    assertNull(config.getSpecJobKubeNodeSelectors());

    envMap.put(EnvConfigs.SPEC_JOB_KUBE_NODE_SELECTORS, "key=k,,;$%&^#");
    assertEquals(config.getSpecJobKubeNodeSelectors(), Map.of("key", "k"));

    envMap.put(EnvConfigs.SPEC_JOB_KUBE_NODE_SELECTORS, "one=two");
    assertEquals(config.getSpecJobKubeNodeSelectors(), Map.of("one", "two"));

    envMap.put(EnvConfigs.SPEC_JOB_KUBE_NODE_SELECTORS, "airbyte=server,something=nothing");
    assertEquals(config.getSpecJobKubeNodeSelectors(), Map.of("airbyte", "server", "something", "nothing"));
  }

  @Test
  void testCheckKubeNodeSelectors() {
    envMap.put(EnvConfigs.CHECK_JOB_KUBE_NODE_SELECTORS, null);
    assertNull(config.getCheckJobKubeNodeSelectors());

    envMap.put(EnvConfigs.CHECK_JOB_KUBE_NODE_SELECTORS, ",,,");
    assertNull(config.getCheckJobKubeNodeSelectors());

    envMap.put(EnvConfigs.CHECK_JOB_KUBE_NODE_SELECTORS, "key=k,,;$%&^#");
    assertEquals(config.getCheckJobKubeNodeSelectors(), Map.of("key", "k"));

    envMap.put(EnvConfigs.CHECK_JOB_KUBE_NODE_SELECTORS, "one=two");
    assertEquals(config.getCheckJobKubeNodeSelectors(), Map.of("one", "two"));

    envMap.put(EnvConfigs.CHECK_JOB_KUBE_NODE_SELECTORS, "airbyte=server,something=nothing");
    assertEquals(config.getCheckJobKubeNodeSelectors(), Map.of("airbyte", "server", "something", "nothing"));
  }

  @Test
  void testDiscoverKubeNodeSelectors() {
    envMap.put(EnvConfigs.DISCOVER_JOB_KUBE_NODE_SELECTORS, null);
    assertNull(config.getDiscoverJobKubeNodeSelectors());

    envMap.put(EnvConfigs.DISCOVER_JOB_KUBE_NODE_SELECTORS, ",,,");
    assertNull(config.getDiscoverJobKubeNodeSelectors());

    envMap.put(EnvConfigs.DISCOVER_JOB_KUBE_NODE_SELECTORS, "key=k,,;$%&^#");
    assertEquals(config.getDiscoverJobKubeNodeSelectors(), Map.of("key", "k"));

    envMap.put(EnvConfigs.DISCOVER_JOB_KUBE_NODE_SELECTORS, "one=two");
    assertEquals(config.getDiscoverJobKubeNodeSelectors(), Map.of("one", "two"));

    envMap.put(EnvConfigs.DISCOVER_JOB_KUBE_NODE_SELECTORS, "airbyte=server,something=nothing");
    assertEquals(config.getDiscoverJobKubeNodeSelectors(), Map.of("airbyte", "server", "something", "nothing"));
  }

  @Test
  void testPublishMetrics() {
    envMap.put(EnvConfigs.PUBLISH_METRICS, "true");
    assertTrue(config.getPublishMetrics());

    envMap.put(EnvConfigs.PUBLISH_METRICS, "false");
    assertFalse(config.getPublishMetrics());

    envMap.put(EnvConfigs.PUBLISH_METRICS, null);
    assertFalse(config.getPublishMetrics());

    envMap.put(EnvConfigs.PUBLISH_METRICS, "");
    assertFalse(config.getPublishMetrics());
  }

  @Nested
  @DisplayName("CheckJobResourceSettings")
  public class CheckJobResourceSettings {

    @Test
    @DisplayName("should default to JobMainCpuRequest if not set")
    void testCpuRequestDefaultToJobMainCpuRequest() {
      envMap.put(EnvConfigs.CHECK_JOB_MAIN_CONTAINER_CPU_REQUEST, null);
      envMap.put(EnvConfigs.JOB_MAIN_CONTAINER_CPU_REQUEST, "1");
      assertEquals("1", config.getCheckJobMainContainerCpuRequest());
    }

    @Test
    @DisplayName("checkJobCpuRequest should take precedent if set")
    void testCheckJobCpuRequestTakePrecedentIfSet() {
      envMap.put(EnvConfigs.CHECK_JOB_MAIN_CONTAINER_CPU_REQUEST, "1");
      envMap.put(EnvConfigs.JOB_MAIN_CONTAINER_CPU_REQUEST, "2");
      assertEquals("1", config.getCheckJobMainContainerCpuRequest());
    }

    @Test
    @DisplayName("should default to JobMainCpuLimit if not set")
    void testCpuLimitDefaultToJobMainCpuLimit() {
      envMap.put(EnvConfigs.CHECK_JOB_MAIN_CONTAINER_CPU_LIMIT, null);
      envMap.put(EnvConfigs.JOB_MAIN_CONTAINER_CPU_LIMIT, "1");
      assertEquals("1", config.getCheckJobMainContainerCpuLimit());
    }

    @Test
    @DisplayName("checkJobCpuLimit should take precedent if set")
    void testCheckJobCpuLimitTakePrecedentIfSet() {
      envMap.put(EnvConfigs.CHECK_JOB_MAIN_CONTAINER_CPU_LIMIT, "1");
      envMap.put(EnvConfigs.JOB_MAIN_CONTAINER_CPU_LIMIT, "2");
      assertEquals("1", config.getCheckJobMainContainerCpuLimit());
    }

    @Test
    @DisplayName("should default to JobMainMemoryRequest if not set")
    void testMemoryRequestDefaultToJobMainMemoryRequest() {
      envMap.put(EnvConfigs.CHECK_JOB_MAIN_CONTAINER_MEMORY_REQUEST, null);
      envMap.put(EnvConfigs.JOB_MAIN_CONTAINER_MEMORY_REQUEST, "1");
      assertEquals("1", config.getCheckJobMainContainerMemoryRequest());
    }

    @Test
    @DisplayName("checkJobMemoryRequest should take precedent if set")
    void testCheckJobMemoryRequestTakePrecedentIfSet() {
      envMap.put(EnvConfigs.CHECK_JOB_MAIN_CONTAINER_MEMORY_REQUEST, "1");
      envMap.put(EnvConfigs.JOB_MAIN_CONTAINER_MEMORY_REQUEST, "2");
      assertEquals("1", config.getCheckJobMainContainerMemoryRequest());
    }

    @Test
    @DisplayName("should default to JobMainMemoryLimit if not set")
    void testMemoryLimitDefaultToJobMainMemoryLimit() {
      envMap.put(EnvConfigs.CHECK_JOB_MAIN_CONTAINER_MEMORY_LIMIT, null);
      envMap.put(EnvConfigs.JOB_MAIN_CONTAINER_MEMORY_LIMIT, "1");
      assertEquals("1", config.getCheckJobMainContainerMemoryLimit());
    }

    @Test
    @DisplayName("checkJobMemoryLimit should take precedent if set")
    void testCheckJobMemoryLimitTakePrecedentIfSet() {
      envMap.put(EnvConfigs.CHECK_JOB_MAIN_CONTAINER_MEMORY_LIMIT, "1");
      envMap.put(EnvConfigs.JOB_MAIN_CONTAINER_MEMORY_LIMIT, "2");
      assertEquals("1", config.getCheckJobMainContainerMemoryLimit());
    }

  }

  @Test
  void testSharedJobEnvMapRetrieval() {
    envMap.put(EnvConfigs.AIRBYTE_VERSION, "dev");
    envMap.put(EnvConfigs.WORKER_ENVIRONMENT, WorkerEnvironment.KUBERNETES.name());
    final Map<String, String> expected = Map.of("AIRBYTE_VERSION", "dev",
        "AIRBYTE_ROLE", "",
        "WORKER_ENVIRONMENT", "KUBERNETES");
    assertEquals(expected, config.getJobDefaultEnvMap());
  }

  @Test
  void testAllJobEnvMapRetrieval() {
    envMap.put(EnvConfigs.AIRBYTE_VERSION, "dev");
    envMap.put(EnvConfigs.AIRBYTE_ROLE, "UNIT_TEST");
    envMap.put(EnvConfigs.JOB_DEFAULT_ENV_PREFIX + "ENV1", "VAL1");
    envMap.put(EnvConfigs.JOB_DEFAULT_ENV_PREFIX + "ENV2", "VAL\"2WithQuotesand$ymbols");

    final Map<String, String> expected = Map.of("ENV1", "VAL1",
        "ENV2", "VAL\"2WithQuotesand$ymbols",
        "AIRBYTE_VERSION", "dev",
        "AIRBYTE_ROLE", "UNIT_TEST",
        "WORKER_ENVIRONMENT", "DOCKER");
    assertEquals(expected, config.getJobDefaultEnvMap());
  }

}
