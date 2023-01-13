package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.internal.DefaultAirbyteSource;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.KubePortManagerSingleton;
import io.airbyte.workers.process.KubeProcessFactory;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.net.InetAddress;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class PostgresSourcePerformanceProcessTest {

  public static final int PORT1 = 9877;
  public static final int PORT2 = 9878;
  public static final int PORT3 = 9879;
  public static final int PORT4 = 9880;

  public static final Set<Integer> PORTS = Set.of(PORT1, PORT2, PORT3, PORT4);
  private static final String PERFORMANCE_SECRET_CREDS = "secrets/performance-config.json";

  final JsonNode plainConfig = Jsons.deserialize(IOs.readFile(Path.of(PERFORMANCE_SECRET_CREDS)));

  final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
      .put("method", "Standard")
      .build());

  public static void main(String[] args) throws Exception {
    // Unfortunately, not getting picked up.
    //    var creds = PostgresSourcePerformanceProcessTest.class.getClassLoader().getResource(PERFORMANCE_SECRET_CREDS).getPath();
    ObjectMapper mapper = new ObjectMapper();
    final JsonNode plainConfig = mapper.readTree(
            "{\"host\": \"34.172.209.107\", \"port\": 5432, \"schemas\": [\"public\"], \"database\": \"\", \"password\": \"\", \"ssl_mode\": {\"mode\": \"require\"}, \"username\": \"\", \"tunnel_method\": {\"tunnel_method\": \"NO_TUNNEL\"}, \"replication_method\": {\"method\": \"Standard\"}}");


    var config = Jsons.jsonNode(ImmutableMap.builder()
      .put(JdbcUtils.HOST_KEY, plainConfig.get(JdbcUtils.HOST_KEY))
      .put(JdbcUtils.PORT_KEY, plainConfig.get(JdbcUtils.PORT_KEY))
      .put(JdbcUtils.DATABASE_KEY, "postgres")
        .put(JdbcUtils.SCHEMAS_KEY, List.of("public"))
      .put(JdbcUtils.USERNAME_KEY, plainConfig.get(JdbcUtils.USERNAME_KEY))
      .put(JdbcUtils.PASSWORD_KEY, plainConfig.get(JdbcUtils.PASSWORD_KEY))
      .put(JdbcUtils.SSL_KEY, true)
        .put("replication_method", "Standard")
        .build());

    KubePortManagerSingleton.init(PORTS);
    final KubernetesClient fabricClient = new DefaultKubernetesClient();
    final String localIp = InetAddress.getLocalHost().getHostAddress();
    final String kubeHeartbeatUrl = localIp + ":" + 9000;
    var workerConfigs = new WorkerConfigs(new EnvConfigs());
    var processFactory = new KubeProcessFactory(workerConfigs, "default", fabricClient, kubeHeartbeatUrl, false);

//    final Path testDir = Path.of("/tmp/airbyte_tests/");
//    final Path workspaceRoot = Files.createTempDirectory(testDir, "test");
//    var localRoot = Files.createTempDirectory(testDir, "output");
//    var processFactory = new DockerProcessFactory(
//        workerConfigs,
//        workspaceRoot,
//        workspaceRoot.toString(),
//        localRoot.toString(),
//        "host");

    ResourceRequirements resourceReqs = null;

    var integrationLauncher =
          new AirbyteIntegrationLauncher("1", 0, "airbyte/source-postgres:1.0.35", processFactory, resourceReqs, false);
    var source = new DefaultAirbyteSource(integrationLauncher);
    var jobRoot = "/";

    final ConfiguredAirbyteCatalog catalog = Jsons.deserialize(
        "{\"streams\":[{\"stream\":{\"name\":\"towns\",\"namespace\":\"public\",\"json_schema\":{\"type\":\"object\",\"properties\":{\"id\":{\"type\":\"number\",\"airbyte_type\":\"integer\"},\"code\":{\"type\":\"string\"},\"name\":{\"type\":\"string\"},\"article\":{\"type\":\"string\"}}},\"default_cursor_field\":[],\"supported_sync_modes\":[\"full_refresh\",\"incremental\"],\"source_defined_primary_key\":[]},\"sync_mode\":\"full_refresh\",\"primary_key\":[],\"cursor_field\":[],\"destination_sync_mode\":\"overwrite\"}]}",
        ConfiguredAirbyteCatalog.class);

    final WorkerSourceConfig sourceConfig = new WorkerSourceConfig()
        .withSourceConnectionConfiguration(plainConfig)
        .withState(null)
        .withCatalog(convertProtocolObject(catalog, io.airbyte.protocol.models.ConfiguredAirbyteCatalog.class));

    source.start(sourceConfig, Path.of(jobRoot));
    var totalBytes = 0;
    var counter = 0;
    var start = System.currentTimeMillis();
    while (!source.isFinished()) {
      final Optional<AirbyteMessage> airbyteMessageOptional = source.attemptRead();

      final io.airbyte.protocol.models.AirbyteMessage airbyteMessage = airbyteMessageOptional.get();
      if (airbyteMessage.getRecord() != null) {
        totalBytes += airbyteMessage.getRecord().getData().toString().getBytes().length;
        counter++;
      }

      if (counter % 1_000_000 == 0) {
        break;
      }

    }

    var end = System.currentTimeMillis();
    var totalMB = totalBytes / 1_000_000.0;
    var totalTimeSecs = (end - start) / 1000.0;
    log.info("total secs: {}. total MB read: {}, throughput: {}", totalTimeSecs, totalMB, totalMB / totalTimeSecs);
    source.close();
  }

  private static <V0, V1> V0 convertProtocolObject(final V1 v1, final Class<V0> klass) {
    return Jsons.object(Jsons.jsonNode(v1), klass);
  }

}
