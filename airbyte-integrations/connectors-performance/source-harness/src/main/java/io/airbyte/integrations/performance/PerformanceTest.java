package io.airbyte.integrations.performance;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.db.jdbc.JdbcUtils;
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
import java.net.UnknownHostException;
import java.nio.charset.Charset;
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

    final var runConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, this.config.get(JdbcUtils.HOST_KEY))
        .put(JdbcUtils.PORT_KEY, this.config.get(JdbcUtils.PORT_KEY))
        .put(JdbcUtils.DATABASE_KEY, "postgres")
        .put(JdbcUtils.SCHEMAS_KEY, List.of("public"))
        .put(JdbcUtils.USERNAME_KEY, this.config.get(JdbcUtils.USERNAME_KEY))
        .put(JdbcUtils.PASSWORD_KEY, this.config.get(JdbcUtils.PASSWORD_KEY))
        .put(JdbcUtils.SSL_KEY, true)
        .put("replication_method", "Standard")
        .build());
    KubePortManagerSingleton.init(PORTS);

    final KubernetesClient fabricClient = new DefaultKubernetesClient();
    final String localIp = InetAddress.getLocalHost().getHostAddress();
    final String kubeHeartbeatUrl = localIp + ":" + 9000;
    final var workerConfigs = new WorkerConfigs(new EnvConfigs());
    final var processFactory = new KubeProcessFactory(workerConfigs, "default", fabricClient, kubeHeartbeatUrl, false);
    final ResourceRequirements resourceReqs = null;
    final var heartbeatMonitor = new HeartbeatMonitor(Duration.ofSeconds(1));
    final var integrationLauncher =
        new AirbyteIntegrationLauncher("1", 0, this.imageName, processFactory, resourceReqs, null, false, new EnvVariableFeatureFlags());
    final var source = new DefaultAirbyteSource(integrationLauncher, new EnvVariableFeatureFlags(), heartbeatMonitor);
    final var jobRoot = "/";
    final WorkerSourceConfig sourceConfig = new WorkerSourceConfig()
        .withSourceConnectionConfiguration(runConfig)
        .withState(null)
        .withCatalog(this.catalog);

    source.start(sourceConfig, Path.of(jobRoot));
    var totalBytes = 0.0;
    var counter = 0L;
    final var start = System.currentTimeMillis();
    log.info("Starting");
    while (!source.isFinished()) {
      final Optional<AirbyteMessage> airbyteMessageOptional = source.attemptRead();
      if (airbyteMessageOptional.isPresent()) {
        final AirbyteMessage airbyteMessage = airbyteMessageOptional.get();

        if (airbyteMessage.getRecord() != null) {
          totalBytes += airbyteMessage.getRecord().getData().toString().getBytes(Charset.defaultCharset()).length;
          counter++;
        }

        if (counter % 1_000_000 == 0) {
          break;
        }
      }

      final var end = System.currentTimeMillis();
      final var totalMB = totalBytes / 1_000_000.0;
      final var totalTimeSecs = (end - start) / 1000.0;
      final var rps = counter / totalTimeSecs;
      log.info("total secs: {}. total MB read: {}, rps: {}, throughput: {}", totalTimeSecs, totalMB, rps, totalMB / totalTimeSecs);
      source.close();
    }
  }
}
