/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

public class WorkerConfigsTest {

  private Configs configs;
  private WorkerConfigs specWorkerConfigs;
  private WorkerConfigs checkWorkerConfigs;
  private WorkerConfigs discoverWorkerConfigs;
  private WorkerConfigs syncWorkerConfigs;

  @Nested
  public class NodeSelectorsSetForJobType {

    private static final Map<String, String> SPEC_NODE_SELECTORS = ImmutableMap.of("job", "spec");
    private static final Map<String, String> CHECK_NODE_SELECTORS = ImmutableMap.of("job", "check");
    private static final Map<String, String> DISCOVER_NODE_SELECTORS = ImmutableMap.of("job", "discover");
    private static final Map<String, String> SYNC_NODE_SELECTORS = ImmutableMap.of("job", "sync");

    @BeforeEach
    public void setup() {
      configs = mock(EnvConfigs.class);
      when(configs.getCheckJobKubeNodeSelectors()).thenReturn(Optional.of(CHECK_NODE_SELECTORS));
      when(configs.getSpecJobKubeNodeSelectors()).thenReturn(Optional.of(SPEC_NODE_SELECTORS));
      when(configs.getDiscoverJobKubeNodeSelectors()).thenReturn(Optional.of(DISCOVER_NODE_SELECTORS));
      when(configs.getSyncJobKubeNodeSelectors()).thenReturn(Optional.of(SYNC_NODE_SELECTORS));

      specWorkerConfigs = WorkerConfigs.buildSpecWorkerConfigs(configs);
      checkWorkerConfigs = WorkerConfigs.buildCheckWorkerConfigs(configs);
      discoverWorkerConfigs = WorkerConfigs.buildDiscoverWorkerConfigs(configs);
      syncWorkerConfigs = WorkerConfigs.buildSyncWorkerConfigs(configs);
    }

    @Test
    @DisplayName("worker configs use job-specific node selectors")
    public void testNodeSelectors() {
      Assertions.assertEquals(SPEC_NODE_SELECTORS, specWorkerConfigs.getworkerKubeNodeSelectors().get());
      Assertions.assertEquals(CHECK_NODE_SELECTORS, checkWorkerConfigs.getworkerKubeNodeSelectors().get());
      Assertions.assertEquals(DISCOVER_NODE_SELECTORS, discoverWorkerConfigs.getworkerKubeNodeSelectors().get());
      Assertions.assertEquals(SYNC_NODE_SELECTORS, syncWorkerConfigs.getworkerKubeNodeSelectors().get());
    }

  }

  @Nested
  public class DefaultNodeSelectors {

    private static final Map<String, String> NODE_SELECTORS = ImmutableMap.of("job", "all");

    @BeforeEach
    public void setup() {
      configs = mock(EnvConfigs.class);
      when(configs.getCheckJobKubeNodeSelectors()).thenReturn(Optional.empty());
      when(configs.getSpecJobKubeNodeSelectors()).thenReturn(Optional.empty());
      when(configs.getDiscoverJobKubeNodeSelectors()).thenReturn(Optional.empty());
      when(configs.getSyncJobKubeNodeSelectors()).thenReturn(Optional.empty());

      when(configs.getJobKubeNodeSelectors()).thenReturn(Optional.of(NODE_SELECTORS));

      specWorkerConfigs = WorkerConfigs.buildSpecWorkerConfigs(configs);
      checkWorkerConfigs = WorkerConfigs.buildCheckWorkerConfigs(configs);
      discoverWorkerConfigs = WorkerConfigs.buildDiscoverWorkerConfigs(configs);
      syncWorkerConfigs = WorkerConfigs.buildSyncWorkerConfigs(configs);
    }

    @Test
    @DisplayName("worker configs use default node selectors when no job-specific selectors set")
    public void testNodeSelectors() {
      Assertions.assertEquals(NODE_SELECTORS, specWorkerConfigs.getworkerKubeNodeSelectors().get());
      Assertions.assertEquals(NODE_SELECTORS, checkWorkerConfigs.getworkerKubeNodeSelectors().get());
      Assertions.assertEquals(NODE_SELECTORS, discoverWorkerConfigs.getworkerKubeNodeSelectors().get());
      Assertions.assertEquals(NODE_SELECTORS, syncWorkerConfigs.getworkerKubeNodeSelectors().get());
    }

  }

}
