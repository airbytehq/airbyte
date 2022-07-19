/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.config.Configs.JobErrorReportingStrategy;
import io.airbyte.config.Configs.WorkerEnvironment;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

@SuppressWarnings("PMD.NullAssignment")
class EnvConfigsTest {

  private Map<String, String> envMap;
  private EnvConfigs config;
  private final static String DEV = "dev";
  private final static String ABCDEF = "abc/def";
  private final static String ROOT = "root";
  private final static String KEY = "key";
  private final static String ONE = "one";
  private final static String TWO = "two";
  private final static String ONE_EQ_TWO = "one=two";
  private final static String NOTHING = "nothing";
  private final static String SOMETHING = "something";
  private final static String AIRBYTE = "airbyte";
  private final static String SERVER = "server";
  private final static String AIRB_SERV_SOME_NOTHING = "airbyte=server,something=nothing";
  private final static String ENV_STRING = "key=k,,;$%&^#";
  private final static String NODE_SELECTORS = ",,,";

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

    envMap.put(EnvConfigs.AIRBYTE_ROLE, DEV);
    assertEquals(DEV, config.getAirbyteRole());
  }

  @Test
  void testAirbyteVersion() {
    envMap.put(EnvConfigs.AIRBYTE_VERSION, null);
    assertThrows(IllegalArgumentException.class, () -> config.getAirbyteVersion());

    envMap.put(EnvConfigs.AIRBYTE_VERSION, DEV);
    assertEquals(new AirbyteVersion(DEV), config.getAirbyteVersion());
  }

  @Test
  void testWorkspaceRoot() {
    envMap.put(EnvConfigs.WORKSPACE_ROOT, null);
    assertThrows(IllegalArgumentException.class, () -> config.getWorkspaceRoot());

    envMap.put(EnvConfigs.WORKSPACE_ROOT, ABCDEF);
    assertEquals(Paths.get(ABCDEF), config.getWorkspaceRoot());
  }

  @Test
  void testLocalRoot() {
    envMap.put(EnvConfigs.LOCAL_ROOT, null);
    assertThrows(IllegalArgumentException.class, () -> config.getLocalRoot());

    envMap.put(EnvConfigs.LOCAL_ROOT, ABCDEF);
    assertEquals(Paths.get(ABCDEF), config.getLocalRoot());
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
    envMap.put(EnvConfigs.WORKSPACE_ROOT, ABCDEF);
    assertEquals(ABCDEF, config.getWorkspaceDockerMount());

    envMap.put(EnvConfigs.WORKSPACE_DOCKER_MOUNT, ROOT);
    envMap.put(EnvConfigs.WORKSPACE_ROOT, ABCDEF);
    assertEquals(ROOT, config.getWorkspaceDockerMount());

    envMap.put(EnvConfigs.WORKSPACE_DOCKER_MOUNT, null);
    envMap.put(EnvConfigs.WORKSPACE_ROOT, null);
    assertThrows(IllegalArgumentException.class, () -> config.getWorkspaceDockerMount());
  }

  @Test
  void testGetLocalDockerMount() {
    envMap.put(EnvConfigs.LOCAL_DOCKER_MOUNT, null);
    envMap.put(EnvConfigs.LOCAL_ROOT, ABCDEF);
    assertEquals(ABCDEF, config.getLocalDockerMount());

    envMap.put(EnvConfigs.LOCAL_DOCKER_MOUNT, ROOT);
    envMap.put(EnvConfigs.LOCAL_ROOT, ABCDEF);
    assertEquals(ROOT, config.getLocalDockerMount());

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
  void testErrorReportingStrategy() {
    envMap.put(EnvConfigs.JOB_ERROR_REPORTING_STRATEGY, null);
    assertEquals(JobErrorReportingStrategy.LOGGING, config.getJobErrorReportingStrategy());

    envMap.put(EnvConfigs.JOB_ERROR_REPORTING_STRATEGY, "abc");
    assertEquals(JobErrorReportingStrategy.LOGGING, config.getJobErrorReportingStrategy());

    envMap.put(EnvConfigs.JOB_ERROR_REPORTING_STRATEGY, "logging");
    assertEquals(JobErrorReportingStrategy.LOGGING, config.getJobErrorReportingStrategy());

    envMap.put(EnvConfigs.JOB_ERROR_REPORTING_STRATEGY, "sentry");
    assertEquals(JobErrorReportingStrategy.SENTRY, config.getJobErrorReportingStrategy());

    envMap.put(EnvConfigs.JOB_ERROR_REPORTING_STRATEGY, "LOGGING");
    assertEquals(JobErrorReportingStrategy.LOGGING, config.getJobErrorReportingStrategy());

    envMap.put(EnvConfigs.JOB_ERROR_REPORTING_STRATEGY, "SENTRY");
    assertEquals(JobErrorReportingStrategy.SENTRY, config.getJobErrorReportingStrategy());
  }

  @Test
  void testDeploymentMode() {
    envMap.put(EnvConfigs.DEPLOYMENT_MODE, null);
    assertEquals(Configs.DeploymentMode.OSS, config.getDeploymentMode());

    envMap.put(EnvConfigs.DEPLOYMENT_MODE, "CLOUD");
    assertEquals(Configs.DeploymentMode.CLOUD, config.getDeploymentMode());

    envMap.put(EnvConfigs.DEPLOYMENT_MODE, "oss");
    assertEquals(Configs.DeploymentMode.OSS, config.getDeploymentMode());

    envMap.put(EnvConfigs.DEPLOYMENT_MODE, "OSS");
    assertEquals(Configs.DeploymentMode.OSS, config.getDeploymentMode());
  }

  @Test
  void testworkerKubeTolerations() {
    final String airbyteServer = "airbyte-server";
    final String noSchedule = "NoSchedule";

    envMap.put(EnvConfigs.JOB_KUBE_TOLERATIONS, null);
    assertEquals(config.getJobKubeTolerations(), List.of());

    envMap.put(EnvConfigs.JOB_KUBE_TOLERATIONS, ";;;");
    assertEquals(config.getJobKubeTolerations(), List.of());

    envMap.put(EnvConfigs.JOB_KUBE_TOLERATIONS, "key=k,value=v;");
    assertEquals(config.getJobKubeTolerations(), List.of());

    envMap.put(EnvConfigs.JOB_KUBE_TOLERATIONS, "key=airbyte-server,operator=Exists,effect=NoSchedule");
    assertEquals(config.getJobKubeTolerations(), List.of(new TolerationPOJO(airbyteServer, noSchedule, null, "Exists")));

    envMap.put(EnvConfigs.JOB_KUBE_TOLERATIONS, "key=airbyte-server,operator=Equals,value=true,effect=NoSchedule");
    assertEquals(config.getJobKubeTolerations(), List.of(new TolerationPOJO(airbyteServer, noSchedule, "true", "Equals")));

    envMap.put(EnvConfigs.JOB_KUBE_TOLERATIONS,
        "key=airbyte-server,operator=Exists,effect=NoSchedule;key=airbyte-server,operator=Equals,value=true,effect=NoSchedule");
    assertEquals(config.getJobKubeTolerations(), List.of(
        new TolerationPOJO(airbyteServer, noSchedule, null, "Exists"),
        new TolerationPOJO(airbyteServer, noSchedule, "true", "Equals")));
  }

  @Test
  void testSplitKVPairsFromEnvString() {
    String input = "key1=value1,key2=value2";
    Map<String, String> map = config.splitKVPairsFromEnvString(input);
    assertNotNull(map);
    assertEquals(2, map.size());
    assertEquals(map, Map.of("key1", "value1", "key2", "value2"));

    input = ENV_STRING;
    map = config.splitKVPairsFromEnvString(input);
    assertNotNull(map);
    assertEquals(map, Map.of(KEY, "k"));

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

    envMap.put(EnvConfigs.JOB_KUBE_NODE_SELECTORS, NODE_SELECTORS);
    assertNull(config.getJobKubeNodeSelectors());

    envMap.put(EnvConfigs.JOB_KUBE_NODE_SELECTORS, ENV_STRING);
    assertEquals(config.getJobKubeNodeSelectors(), Map.of(KEY, "k"));

    envMap.put(EnvConfigs.JOB_KUBE_NODE_SELECTORS, ONE_EQ_TWO);
    assertEquals(config.getJobKubeNodeSelectors(), Map.of(ONE, TWO));

    envMap.put(EnvConfigs.JOB_KUBE_NODE_SELECTORS, AIRB_SERV_SOME_NOTHING);
    assertEquals(config.getJobKubeNodeSelectors(), Map.of(AIRBYTE, SERVER, SOMETHING, NOTHING));
  }

  @Test
  void testSpecKubeNodeSelectors() {
    envMap.put(EnvConfigs.SPEC_JOB_KUBE_NODE_SELECTORS, null);
    assertNull(config.getSpecJobKubeNodeSelectors());

    envMap.put(EnvConfigs.SPEC_JOB_KUBE_NODE_SELECTORS, NODE_SELECTORS);
    assertNull(config.getSpecJobKubeNodeSelectors());

    envMap.put(EnvConfigs.SPEC_JOB_KUBE_NODE_SELECTORS, ENV_STRING);
    assertEquals(config.getSpecJobKubeNodeSelectors(), Map.of(KEY, "k"));

    envMap.put(EnvConfigs.SPEC_JOB_KUBE_NODE_SELECTORS, ONE_EQ_TWO);
    assertEquals(config.getSpecJobKubeNodeSelectors(), Map.of(ONE, TWO));

    envMap.put(EnvConfigs.SPEC_JOB_KUBE_NODE_SELECTORS, AIRB_SERV_SOME_NOTHING);
    assertEquals(config.getSpecJobKubeNodeSelectors(), Map.of(AIRBYTE, SERVER, SOMETHING, NOTHING));
  }

  @Test
  void testCheckKubeNodeSelectors() {
    envMap.put(EnvConfigs.CHECK_JOB_KUBE_NODE_SELECTORS, null);
    assertNull(config.getCheckJobKubeNodeSelectors());

    envMap.put(EnvConfigs.CHECK_JOB_KUBE_NODE_SELECTORS, NODE_SELECTORS);
    assertNull(config.getCheckJobKubeNodeSelectors());

    envMap.put(EnvConfigs.CHECK_JOB_KUBE_NODE_SELECTORS, ENV_STRING);
    assertEquals(config.getCheckJobKubeNodeSelectors(), Map.of(KEY, "k"));

    envMap.put(EnvConfigs.CHECK_JOB_KUBE_NODE_SELECTORS, ONE_EQ_TWO);
    assertEquals(config.getCheckJobKubeNodeSelectors(), Map.of(ONE, TWO));

    envMap.put(EnvConfigs.CHECK_JOB_KUBE_NODE_SELECTORS, AIRB_SERV_SOME_NOTHING);
    assertEquals(config.getCheckJobKubeNodeSelectors(), Map.of(AIRBYTE, SERVER, SOMETHING, NOTHING));
  }

  @Test
  void testDiscoverKubeNodeSelectors() {
    envMap.put(EnvConfigs.DISCOVER_JOB_KUBE_NODE_SELECTORS, null);
    assertNull(config.getDiscoverJobKubeNodeSelectors());

    envMap.put(EnvConfigs.DISCOVER_JOB_KUBE_NODE_SELECTORS, NODE_SELECTORS);
    assertNull(config.getDiscoverJobKubeNodeSelectors());

    envMap.put(EnvConfigs.DISCOVER_JOB_KUBE_NODE_SELECTORS, ENV_STRING);
    assertEquals(config.getDiscoverJobKubeNodeSelectors(), Map.of(KEY, "k"));

    envMap.put(EnvConfigs.DISCOVER_JOB_KUBE_NODE_SELECTORS, ONE_EQ_TWO);
    assertEquals(config.getDiscoverJobKubeNodeSelectors(), Map.of(ONE, TWO));

    envMap.put(EnvConfigs.DISCOVER_JOB_KUBE_NODE_SELECTORS, AIRB_SERV_SOME_NOTHING);
    assertEquals(config.getDiscoverJobKubeNodeSelectors(), Map.of(AIRBYTE, SERVER, SOMETHING, NOTHING));
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
  class CheckJobResourceSettings {

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
    envMap.put(EnvConfigs.AIRBYTE_VERSION, DEV);
    envMap.put(EnvConfigs.WORKER_ENVIRONMENT, WorkerEnvironment.KUBERNETES.name());
    final Map<String, String> expected = Map.of("AIRBYTE_VERSION", DEV,
        "AIRBYTE_ROLE", "",
        "DEPLOYMENT_MODE", "OSS",
        "WORKER_ENVIRONMENT", "KUBERNETES");
    assertEquals(expected, config.getJobDefaultEnvMap());
  }

  @Test
  void testAllJobEnvMapRetrieval() {
    envMap.put(EnvConfigs.AIRBYTE_VERSION, DEV);
    envMap.put(EnvConfigs.AIRBYTE_ROLE, "UNIT_TEST");
    envMap.put(EnvConfigs.JOB_DEFAULT_ENV_PREFIX + "ENV1", "VAL1");
    envMap.put(EnvConfigs.JOB_DEFAULT_ENV_PREFIX + "ENV2", "VAL\"2WithQuotesand$ymbols");
    envMap.put(EnvConfigs.DEPLOYMENT_MODE, DeploymentMode.CLOUD.name());

    final Map<String, String> expected = Map.of("ENV1", "VAL1",
        "ENV2", "VAL\"2WithQuotesand$ymbols",
        "AIRBYTE_VERSION", DEV,
        "AIRBYTE_ROLE", "UNIT_TEST",
        "DEPLOYMENT_MODE", "CLOUD",
        "WORKER_ENVIRONMENT", "DOCKER");
    assertEquals(expected, config.getJobDefaultEnvMap());
  }

}
