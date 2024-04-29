/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source_performance;

import com.datadog.api.client.ApiClient;
import com.datadog.api.client.ApiException;
import com.datadog.api.client.v2.api.MetricsApi;
import com.datadog.api.client.v2.model.IntakePayloadAccepted;
import com.datadog.api.client.v2.model.MetricIntakeType;
import com.datadog.api.client.v2.model.MetricPayload;
import com.datadog.api.client.v2.model.MetricPoint;
import com.datadog.api.client.v2.model.MetricResource;
import com.datadog.api.client.v2.model.MetricSeries;
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
import java.time.OffsetDateTime;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PerformanceTest {

  private static final Logger log = LoggerFactory.getLogger(PerformanceTest.class);
  public static final int PORT1 = 9877;
  public static final int PORT2 = 9878;
  public static final int PORT3 = 9879;
  public static final int PORT4 = 9880;

  public static final Set<Integer> PORTS = Set.of(PORT1, PORT2, PORT3, PORT4);

  public static final double MEGABYTE = Math.pow(1024, 2);
  private final String imageName;
  private final String dataset;
  private final String syncMode;
  private final boolean reportToDatadog;
  private final JsonNode config;
  private final ConfiguredAirbyteCatalog catalog;

  PerformanceTest(final String imageName,
                  final String dataset,
                  final String syncMode,
                  final Boolean reportToDatadog,
                  final String config,
                  final String catalog)
      throws JsonProcessingException {
    final ObjectMapper mapper = new ObjectMapper();
    this.imageName = imageName;
    this.dataset = dataset;
    this.syncMode = syncMode;
    this.reportToDatadog = reportToDatadog;
    this.config = mapper.readTree(config);
    this.catalog = Jsons.deserialize(catalog, ConfiguredAirbyteCatalog.class);
  }

  void runTest() throws Exception {

    // Initialize datadog.
    ApiClient defaultClient = ApiClient.getDefaultApiClient();
    MetricsApi apiInstance = new MetricsApi(defaultClient);

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
    if (source.getExitValue() > 0) {
      throw new RuntimeException("Source failed with exit code: " + source.getExitValue());
    }
    log.info("Test ended successfully");
    final var end = System.currentTimeMillis();
    final var totalMB = totalBytes / MEGABYTE;
    final var totalTimeSecs = (end - start) / 1000.0;
    final var rps = counter / totalTimeSecs;
    final var throughput = totalMB / totalTimeSecs;
    log.info("total secs: {}. total MB read: {}, rps: {}, throughput: {}", totalTimeSecs, totalMB, rps, throughput);
    source.close();
    if (!reportToDatadog) {
      return;
    }

    final long reportingTimeInEpochSeconds = OffsetDateTime.now().toInstant().getEpochSecond();

    List<MetricResource> metricResources = List.of(
        new MetricResource().name("github").type("runner"),
        new MetricResource().name(imageName).type("image"),
        new MetricResource().name(dataset).type("dataset"),
        new MetricResource().name(syncMode).type("syncMode"));
    MetricPayload body =
        new MetricPayload()
            .series(
                List.of(
                    new MetricSeries()
                        .metric("connectors.performance.rps")
                        .type(MetricIntakeType.GAUGE)
                        .points(
                            Collections.singletonList(
                                new MetricPoint()
                                    .timestamp(reportingTimeInEpochSeconds)
                                    .value(rps)))
                        .resources(metricResources),
                    new MetricSeries()
                        .metric("connectors.performance.throughput")
                        .type(MetricIntakeType.GAUGE)
                        .points(
                            Collections.singletonList(
                                new MetricPoint()
                                    .timestamp(reportingTimeInEpochSeconds)
                                    .value(throughput)))
                        .resources(metricResources)));
    try {
      IntakePayloadAccepted result = apiInstance.submitMetrics(body);
      System.out.println(result);
    } catch (ApiException e) {
      log.error("Exception when calling MetricsApi#submitMetrics.", e);
    }
  }

  private static <V0, V1> V0 convertProtocolObject(final V1 v1, final Class<V0> klass) {
    return Jsons.object(Jsons.jsonNode(v1), klass);
  }

}
