/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.ResourceRequirements;
import java.util.Map;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class WorkerConfigsTest {

  private static final String JOB = "job";
  private static final Map<String, String> DEFAULT_NODE_SELECTORS = ImmutableMap.of(JOB, "default");
  private static final Map<String, String> SPEC_NODE_SELECTORS = ImmutableMap.of(JOB, "spec");
  private static final Map<String, String> CHECK_NODE_SELECTORS = ImmutableMap.of(JOB, "check");
  private static final Map<String, String> DISCOVER_NODE_SELECTORS = ImmutableMap.of(JOB, "discover");
  private static final String DEFAULT_CPU_REQUEST = "0.1";
  private static final String DEFAULT_CPU_LIMIT = "0.2";
  private static final String DEFAULT_MEMORY_REQUEST = "100Mi";
  private static final String DEFAULT_MEMORY_LIMIT = "200Mi";
  private static final ResourceRequirements DEFAULT_RESOURCE_REQUIREMENTS = new ResourceRequirements()
      .withCpuRequest(DEFAULT_CPU_REQUEST)
      .withCpuLimit(DEFAULT_CPU_LIMIT)
      .withMemoryRequest(DEFAULT_MEMORY_REQUEST)
      .withMemoryLimit(DEFAULT_MEMORY_LIMIT);

  private static final String REPLICATION_CPU_REQUEST = "0.3";
  private static final String REPLICATION_CPU_LIMIT = "0.4";
  private static final String REPLICATION_MEMORY_REQUEST = "300Mi";
  private static final String REPLICATION_MEMORY_LIMIT = "400Mi";
  private static final ResourceRequirements REPLICATION_RESOURCE_REQUIREMENTS = new ResourceRequirements()
      .withCpuRequest(REPLICATION_CPU_REQUEST)
      .withCpuLimit(REPLICATION_CPU_LIMIT)
      .withMemoryRequest(REPLICATION_MEMORY_REQUEST)
      .withMemoryLimit(REPLICATION_MEMORY_LIMIT);

  private Configs configs;

  @BeforeEach
  void setup() {
    configs = mock(EnvConfigs.class);
    when(configs.getJobKubeNodeSelectors()).thenReturn(DEFAULT_NODE_SELECTORS);
    when(configs.getJobMainContainerCpuRequest()).thenReturn(DEFAULT_CPU_REQUEST);
    when(configs.getJobMainContainerCpuLimit()).thenReturn(DEFAULT_CPU_LIMIT);
    when(configs.getJobMainContainerMemoryRequest()).thenReturn(DEFAULT_MEMORY_REQUEST);
    when(configs.getJobMainContainerMemoryLimit()).thenReturn(DEFAULT_MEMORY_LIMIT);
  }

  @Test
  @DisplayName("default workerConfigs use default node selectors")
  void testDefaultNodeSelectors() {
    final WorkerConfigs defaultWorkerConfigs = new WorkerConfigs(configs);

    Assertions.assertEquals(DEFAULT_NODE_SELECTORS, defaultWorkerConfigs.getworkerKubeNodeSelectors());
  }

  @Test
  @DisplayName("spec, check, and discover workerConfigs use job-specific node selectors if set")
  void testCustomNodeSelectors() {
    when(configs.getCheckJobKubeNodeSelectors()).thenReturn(CHECK_NODE_SELECTORS);
    when(configs.getSpecJobKubeNodeSelectors()).thenReturn(SPEC_NODE_SELECTORS);
    when(configs.getDiscoverJobKubeNodeSelectors()).thenReturn(DISCOVER_NODE_SELECTORS);

    final WorkerConfigs specWorkerConfigs = WorkerConfigs.buildSpecWorkerConfigs(configs);
    final WorkerConfigs checkWorkerConfigs = WorkerConfigs.buildCheckWorkerConfigs(configs);
    final WorkerConfigs discoverWorkerConfigs = WorkerConfigs.buildDiscoverWorkerConfigs(configs);

    Assertions.assertEquals(SPEC_NODE_SELECTORS, specWorkerConfigs.getworkerKubeNodeSelectors());
    Assertions.assertEquals(CHECK_NODE_SELECTORS, checkWorkerConfigs.getworkerKubeNodeSelectors());
    Assertions.assertEquals(DISCOVER_NODE_SELECTORS, discoverWorkerConfigs.getworkerKubeNodeSelectors());
  }

  @Test
  @DisplayName("spec, check, and discover workerConfigs use default node selectors when custom selectors are not set")
  void testNodeSelectorsFallbackToDefault() {
    when(configs.getCheckJobKubeNodeSelectors()).thenReturn(null);
    when(configs.getSpecJobKubeNodeSelectors()).thenReturn(null);
    when(configs.getDiscoverJobKubeNodeSelectors()).thenReturn(null);

    final WorkerConfigs specWorkerConfigs = WorkerConfigs.buildSpecWorkerConfigs(configs);
    final WorkerConfigs checkWorkerConfigs = WorkerConfigs.buildCheckWorkerConfigs(configs);
    final WorkerConfigs discoverWorkerConfigs = WorkerConfigs.buildDiscoverWorkerConfigs(configs);

    Assertions.assertEquals(DEFAULT_NODE_SELECTORS, specWorkerConfigs.getworkerKubeNodeSelectors());
    Assertions.assertEquals(DEFAULT_NODE_SELECTORS, checkWorkerConfigs.getworkerKubeNodeSelectors());
    Assertions.assertEquals(DEFAULT_NODE_SELECTORS, discoverWorkerConfigs.getworkerKubeNodeSelectors());
  }

  @Test
  @DisplayName("default workerConfigs use default resourceRequirements")
  void testDefaultResourceRequirements() {
    final WorkerConfigs defaultWorkerConfigs = new WorkerConfigs(configs);

    Assertions.assertEquals(DEFAULT_RESOURCE_REQUIREMENTS, defaultWorkerConfigs.getResourceRequirements());
  }

  @Test
  @DisplayName("replication workerConfigs use replication-specific resourceRequirements")
  void testCustomResourceRequirements() {
    when(configs.getReplicationOrchestratorCpuRequest()).thenReturn(REPLICATION_CPU_REQUEST);
    when(configs.getReplicationOrchestratorCpuLimit()).thenReturn(REPLICATION_CPU_LIMIT);
    when(configs.getReplicationOrchestratorMemoryRequest()).thenReturn(REPLICATION_MEMORY_REQUEST);
    when(configs.getReplicationOrchestratorMemoryLimit()).thenReturn(REPLICATION_MEMORY_LIMIT);

    final WorkerConfigs replicationWorkerConfigs = WorkerConfigs.buildReplicationWorkerConfigs(configs);

    Assertions.assertEquals(REPLICATION_RESOURCE_REQUIREMENTS, replicationWorkerConfigs.getResourceRequirements());
  }

}
