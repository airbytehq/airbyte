/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source_performance;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AllowedHosts;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.internal.DefaultAirbyteSource;
import io.airbyte.workers.internal.HeartbeatMonitor;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.KubePortManagerSingleton;
import io.airbyte.workers.process.KubeProcessFactory;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.net.InetAddress;
import java.nio.file.Path;
import java.time.Duration;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class PerformanceTest {

  public static final int PORT1 = 9877;
  public static final int PORT2 = 9878;
  public static final int PORT3 = 9879;
  public static final int PORT4 = 9880;

  public static final Set<Integer> PORTS = Set.of(PORT1, PORT2, PORT3, PORT4);

  public static final double MEGABYTE = Math.pow(1024, 2);
  private final String imageName;
  private final JsonNode config;
  private final ConfiguredAirbyteCatalog catalog;

  PerformanceTest(final String imageName, final String config, final String catalog) throws JsonProcessingException {
    final ObjectMapper mapper = new ObjectMapper();
    this.imageName = imageName;
    this.config = mapper.readTree(config);
    this.catalog = Jsons.deserialize(catalog, ConfiguredAirbyteCatalog.class);
  }

  void runTest() throws Exception {
    KubePortManagerSingleton.init(PORTS);

    final KubernetesClient fabricClient = new DefaultKubernetesClient();
    final String localIp = InetAddress.getLocalHost().getHostAddress();
    final String kubeHeartbeatUrl = localIp + ":" + 9000;
    final var workerConfigs = new WorkerConfigs(new EnvConfigs());
    final var processFactory = new KubeProcessFactory(workerConfigs, "default", fabricClient, kubeHeartbeatUrl, false);
    final ResourceRequirements resourceReqs = new ResourceRequirements()
        .withCpuLimit("2.5")
        .withCpuRequest("2.5")
        .withMemoryLimit("2Gi")
        .withMemoryRequest("2Gi");
    final var heartbeatMonitor = new HeartbeatMonitor(Duration.ofMillis(1));
    final var allowedHosts = new AllowedHosts().withHosts(List.of("*"));
    final var integrationLauncher =
        new AirbyteIntegrationLauncher("1", 0, this.imageName, processFactory, resourceReqs, allowedHosts, false, new EnvVariableFeatureFlags());
    final var source = new DefaultAirbyteSource(integrationLauncher, new EnvVariableFeatureFlags(), heartbeatMonitor);
    final var jobRoot = "/";
    final WorkerSourceConfig sourceConfig = new WorkerSourceConfig()
        .withSourceConnectionConfiguration(this.config)
        .withState(null)
        .withCatalog(convertProtocolObject(this.catalog, io.airbyte.protocol.models.ConfiguredAirbyteCatalog.class));

    log.info("Source starting");
    source.start(sourceConfig, Path.of(jobRoot));
    var totalBytes = 0.0;
    var counter = 0L;
    final var start = System.currentTimeMillis();
    log.info("Starting Test");
    while (!source.isFinished()) {
      final Optional<AirbyteMessage> airbyteMessageOptional = source.attemptRead();
      if (airbyteMessageOptional.isPresent()) {
        final AirbyteMessage airbyteMessage = airbyteMessageOptional.get();

        if (airbyteMessage.getRecord() != null) {
          totalBytes += Jsons.getEstimatedByteSize(airbyteMessage.getRecord().getData());
          counter++;
        }

      }

      if (counter > 0 && counter % MEGABYTE == 0) {
        log.info("current throughput: {} total MB {}", (totalBytes / MEGABYTE) / ((System.currentTimeMillis() - start) / 1000.0),
            totalBytes / MEGABYTE);
      }
    }
    log.info("Test ended successfully");
    final var end = System.currentTimeMillis();
    final var totalMB = totalBytes / MEGABYTE;
    final var totalTimeSecs = (end - start) / 1000.0;
    final var rps = counter / totalTimeSecs;
    log.info("total secs: {}. total MB read: {}, rps: {}, throughput: {}", totalTimeSecs, totalMB, rps, totalMB / totalTimeSecs);
    source.close();
  }

  private static <V0, V1> V0 convertProtocolObject(final V1 v1, final Class<V0> klass) {
    return Jsons.object(Jsons.jsonNode(v1), klass);
  }

}
