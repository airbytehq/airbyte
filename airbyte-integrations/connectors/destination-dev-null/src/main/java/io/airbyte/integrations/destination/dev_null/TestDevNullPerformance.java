package io.airbyte.integrations.destination.dev_null;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.internal.DefaultAirbyteDestination;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.KubePortManagerSingleton;
import io.airbyte.workers.process.KubeProcessFactory;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.net.InetAddress;
import java.nio.file.Path;
import java.time.Instant;
import java.util.Map;
import java.util.Set;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class TestDevNullPerformance {

  public static final int PORT1 = 9877;
  public static final int PORT2 = 9878;
  public static final int PORT3 = 9879;
  public static final int PORT4 = 9880;

  public static final Set<Integer> PORTS = Set.of(PORT1, PORT2, PORT3, PORT4);

  public static final ConfiguredAirbyteCatalog catalog = Jsons.deserialize(
      "{\"streams\":[{\"stream\":{\"name\":\"towns\",\"namespace\":\"public\",\"json_schema\":{\"type\":\"object\",\"properties\":{\"id\":{\"type\":\"number\",\"airbyte_type\":\"integer\"},\"code\":{\"type\":\"string\"},\"name\":{\"type\":\"string\"},\"article\":{\"type\":\"string\"}}},\"default_cursor_field\":[],\"supported_sync_modes\":[\"full_refresh\",\"incremental\"],\"source_defined_primary_key\":[]},\"sync_mode\":\"full_refresh\",\"primary_key\":[],\"cursor_field\":[],\"destination_sync_mode\":\"overwrite\"}]}",
      ConfiguredAirbyteCatalog.class);
  public static ObjectMapper mapper = new ObjectMapper();

  public static JsonNode config;

  {
    try {
      config = mapper.readTree("{\"type\": \"SILENT\"}");
    } catch (JsonProcessingException e) {
      throw new RuntimeException(e);
    }
  }

  public static void main(String[] args) throws Exception {
    KubePortManagerSingleton.init(PORTS);
    final KubernetesClient fabricClient = new DefaultKubernetesClient();
    final String localIp = InetAddress.getLocalHost().getHostAddress();
    final String kubeHeartbeatUrl = localIp + ":" + 9000;
    var workerConfigs = new WorkerConfigs(new EnvConfigs());
    var processFactory = new KubeProcessFactory(workerConfigs, "default", fabricClient, kubeHeartbeatUrl, false);

    var integrationLauncher =
        new AirbyteIntegrationLauncher("1", 0, "airbyte/destination-dev-null:snapshot-0", processFactory, null, false);
    var destination = new DefaultAirbyteDestination(integrationLauncher);

    final WorkerDestinationConfig destConfig = new WorkerDestinationConfig()
        .withDestinationConnectionConfiguration(config)
        .withCatalog(convertProtocolObject(catalog, io.airbyte.protocol.models.ConfiguredAirbyteCatalog.class));

    var jobRoot = "/";
    destination.start(destConfig, Path.of(jobRoot));

    log.info("------ destination started...");

    var start = System.currentTimeMillis();
    for (int i = 0; i < 1_000_000; i++) {
      if (i % 100_00 == 0) {
        log.info("emitted {} records: ", i);
      }
      
      final var msg = new io.airbyte.protocol.models.AirbyteMessage()
          .withType(io.airbyte.protocol.models.AirbyteMessage.Type.RECORD)
          .withRecord(new io.airbyte.protocol.models.AirbyteRecordMessage()
              .withData(Jsons.jsonNode(
                  Map.of("data", "This is a fairly long sentence to provide some bytes here. More bytes is better as it helps us measure performance."
                      + "Random append to prevent dead code generation:" + i)))
              .withStream("s1")
              .withEmittedAt(Instant.now().getEpochSecond()));
      destination.accept(msg);
    }
    var end = System.currentTimeMillis();
    var timeTaken = end - start;

    // This seems like it's taking 420 ms.
    log.info("time taken ms: " + timeTaken);
    destination.close();

  }

  private static <V0, V1> V0 convertProtocolObject(final V1 v1, final Class<V0> klass) {
    return Jsons.object(Jsons.jsonNode(v1), klass);
  }

  private static void testJustDevNullSource() throws Exception {
    JsonNode config = mapper.readTree("{\"type\": \"SILENT\"}");

    // emit into dev null destination
    var a = new DevNullDestination().getConsumer(
        config,
        catalog,
        Destination::defaultOutputRecordCollector);
    a.start();

    var start = System.currentTimeMillis();
    for (int i = 0; i < 1_000_000; i++) {
      final var msg = new AirbyteMessage()
          .withType(AirbyteMessage.Type.RECORD)
          .withRecord(new AirbyteRecordMessage()
              .withData(Jsons.jsonNode(
                  Map.of("data", "This is a fairly long sentence to provide some bytes here. More bytes is better as it helps us measure performance."
                      + "Random append to prevent dead code generation:" + i)))
              .withStream("s1")
              .withEmittedAt(Instant.now().getEpochSecond()));
      a.accept(msg);
    }
    var end = System.currentTimeMillis();
    var timeTaken = end - start;

    // This seems like it's taking 420 ms.
    log.info("time taken ms: " + timeTaken);
    a.close();
  }

}
