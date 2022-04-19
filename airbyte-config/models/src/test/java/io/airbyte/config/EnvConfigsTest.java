/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import io.airbyte.commons.version.AirbyteVersion;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
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
    Assertions.assertNull(System.getenv("MY_RANDOM_VAR_1234"));
  }

  @Test
  void testAirbyteRole() {
    envMap.put(EnvConfigs.AIRBYTE_ROLE, null);
    Assertions.assertNull(config.getAirbyteRole());

    envMap.put(EnvConfigs.AIRBYTE_ROLE, "dev");
    Assertions.assertEquals("dev", config.getAirbyteRole());
  }

  @Test
  void testAirbyteVersion() {
    envMap.put(EnvConfigs.AIRBYTE_VERSION, null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getAirbyteVersion());

    envMap.put(EnvConfigs.AIRBYTE_VERSION, "dev");
    Assertions.assertEquals(new AirbyteVersion("dev"), config.getAirbyteVersion());
  }

  @Test
  void testWorkspaceRoot() {
    envMap.put(EnvConfigs.WORKSPACE_ROOT, null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getWorkspaceRoot());

    envMap.put(EnvConfigs.WORKSPACE_ROOT, "abc/def");
    Assertions.assertEquals(Paths.get("abc/def"), config.getWorkspaceRoot());
  }

  @Test
  void testLocalRoot() {
    envMap.put(EnvConfigs.LOCAL_ROOT, null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getLocalRoot());

    envMap.put(EnvConfigs.LOCAL_ROOT, "abc/def");
    Assertions.assertEquals(Paths.get("abc/def"), config.getLocalRoot());
  }

  @Test
  void testConfigRoot() {
    envMap.put(EnvConfigs.CONFIG_ROOT, null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getConfigRoot());

    envMap.put(EnvConfigs.CONFIG_ROOT, "a/b");
    Assertions.assertEquals(Paths.get("a/b"), config.getConfigRoot());
  }

  @Test
  void testGetDatabaseUser() {
    envMap.put(EnvConfigs.DATABASE_USER, null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getDatabaseUser());

    envMap.put(EnvConfigs.DATABASE_USER, "user");
    Assertions.assertEquals("user", config.getDatabaseUser());
  }

  @Test
  void testGetDatabasePassword() {
    envMap.put(EnvConfigs.DATABASE_PASSWORD, null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getDatabasePassword());

    envMap.put(EnvConfigs.DATABASE_PASSWORD, "password");
    Assertions.assertEquals("password", config.getDatabasePassword());
  }

  @Test
  void testGetDatabaseUrl() {
    envMap.put(EnvConfigs.DATABASE_URL, null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getDatabaseUrl());

    envMap.put(EnvConfigs.DATABASE_URL, "url");
    Assertions.assertEquals("url", config.getDatabaseUrl());
  }

  @Test
  void testGetWorkspaceDockerMount() {
    envMap.put(EnvConfigs.WORKSPACE_DOCKER_MOUNT, null);
    envMap.put(EnvConfigs.WORKSPACE_ROOT, "abc/def");
    Assertions.assertEquals("abc/def", config.getWorkspaceDockerMount());

    envMap.put(EnvConfigs.WORKSPACE_DOCKER_MOUNT, "root");
    envMap.put(EnvConfigs.WORKSPACE_ROOT, "abc/def");
    Assertions.assertEquals("root", config.getWorkspaceDockerMount());

    envMap.put(EnvConfigs.WORKSPACE_DOCKER_MOUNT, null);
    envMap.put(EnvConfigs.WORKSPACE_ROOT, null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getWorkspaceDockerMount());
  }

  @Test
  void testGetLocalDockerMount() {
    envMap.put(EnvConfigs.LOCAL_DOCKER_MOUNT, null);
    envMap.put(EnvConfigs.LOCAL_ROOT, "abc/def");
    Assertions.assertEquals("abc/def", config.getLocalDockerMount());

    envMap.put(EnvConfigs.LOCAL_DOCKER_MOUNT, "root");
    envMap.put(EnvConfigs.LOCAL_ROOT, "abc/def");
    Assertions.assertEquals("root", config.getLocalDockerMount());

    envMap.put(EnvConfigs.LOCAL_DOCKER_MOUNT, null);
    envMap.put(EnvConfigs.LOCAL_ROOT, null);
    Assertions.assertThrows(IllegalArgumentException.class, () -> config.getLocalDockerMount());
  }

  @Test
  void testDockerNetwork() {
    envMap.put(EnvConfigs.DOCKER_NETWORK, null);
    Assertions.assertEquals("host", config.getDockerNetwork());

    envMap.put(EnvConfigs.DOCKER_NETWORK, "abc");
    Assertions.assertEquals("abc", config.getDockerNetwork());
  }

  @Test
  void testTrackingStrategy() {
    envMap.put(EnvConfigs.TRACKING_STRATEGY, null);
    Assertions.assertEquals(Configs.TrackingStrategy.LOGGING, config.getTrackingStrategy());

    envMap.put(EnvConfigs.TRACKING_STRATEGY, "abc");
    Assertions.assertEquals(Configs.TrackingStrategy.LOGGING, config.getTrackingStrategy());

    envMap.put(EnvConfigs.TRACKING_STRATEGY, "logging");
    Assertions.assertEquals(Configs.TrackingStrategy.LOGGING, config.getTrackingStrategy());

    envMap.put(EnvConfigs.TRACKING_STRATEGY, "segment");
    Assertions.assertEquals(Configs.TrackingStrategy.SEGMENT, config.getTrackingStrategy());

    envMap.put(EnvConfigs.TRACKING_STRATEGY, "LOGGING");
    Assertions.assertEquals(Configs.TrackingStrategy.LOGGING, config.getTrackingStrategy());
  }

  @Test
  void testworkerKubeTolerations() {
    envMap.put(EnvConfigs.JOB_KUBE_TOLERATIONS, null);
    Assertions.assertEquals(config.getJobKubeTolerations(), List.of());

    envMap.put(EnvConfigs.JOB_KUBE_TOLERATIONS, ";;;");
    Assertions.assertEquals(config.getJobKubeTolerations(), List.of());

    envMap.put(EnvConfigs.JOB_KUBE_TOLERATIONS, "key=k,value=v;");
    Assertions.assertEquals(config.getJobKubeTolerations(), List.of());

    envMap.put(EnvConfigs.JOB_KUBE_TOLERATIONS, "key=airbyte-server,operator=Exists,effect=NoSchedule");
    Assertions.assertEquals(config.getJobKubeTolerations(), List.of(new TolerationPOJO("airbyte-server", "NoSchedule", null, "Exists")));

    envMap.put(EnvConfigs.JOB_KUBE_TOLERATIONS, "key=airbyte-server,operator=Equals,value=true,effect=NoSchedule");
    Assertions.assertEquals(config.getJobKubeTolerations(), List.of(new TolerationPOJO("airbyte-server", "NoSchedule", "true", "Equals")));

    envMap.put(EnvConfigs.JOB_KUBE_TOLERATIONS,
        "key=airbyte-server,operator=Exists,effect=NoSchedule;key=airbyte-server,operator=Equals,value=true,effect=NoSchedule");
    Assertions.assertEquals(config.getJobKubeTolerations(), List.of(
        new TolerationPOJO("airbyte-server", "NoSchedule", null, "Exists"),
        new TolerationPOJO("airbyte-server", "NoSchedule", "true", "Equals")));
  }

  @Test
  void testworkerKubeNodeSelectors() {
    envMap.put(EnvConfigs.JOB_KUBE_NODE_SELECTORS, null);
    Assertions.assertEquals(config.getJobKubeNodeSelectors(), Map.of());

    envMap.put(EnvConfigs.JOB_KUBE_NODE_SELECTORS, ",,,");
    Assertions.assertEquals(config.getJobKubeNodeSelectors(), Map.of());

    envMap.put(EnvConfigs.JOB_KUBE_NODE_SELECTORS, "key=k,,;$%&^#");
    Assertions.assertEquals(config.getJobKubeNodeSelectors(), Map.of("key", "k"));

    envMap.put(EnvConfigs.JOB_KUBE_NODE_SELECTORS, "one=two");
    Assertions.assertEquals(config.getJobKubeNodeSelectors(), Map.of("one", "two"));

    envMap.put(EnvConfigs.JOB_KUBE_NODE_SELECTORS, "airbyte=server,something=nothing");
    Assertions.assertEquals(config.getJobKubeNodeSelectors(), Map.of("airbyte", "server", "something", "nothing"));
  }

  @Test
  void testEmptyEnvMapRetrieval() {
    Assertions.assertEquals(Map.of(), config.getJobDefaultEnvMap());
  }

  @Test
  void testEnvMapRetrieval() {
    envMap.put(EnvConfigs.JOB_DEFAULT_ENV_PREFIX + "ENV1", "VAL1");
    envMap.put(EnvConfigs.JOB_DEFAULT_ENV_PREFIX + "ENV2", "VAL\"2WithQuotesand$ymbols");

    final var expected = Map.of("ENV1", "VAL1", "ENV2", "VAL\"2WithQuotesand$ymbols");
    Assertions.assertEquals(expected, config.getJobDefaultEnvMap());
  }

}
