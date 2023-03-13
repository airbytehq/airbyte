package io.airbyte.integrations.performance;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AllowedHosts;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.workers.RecordSchemaValidator;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.internal.DefaultAirbyteDestination;
import io.airbyte.workers.internal.DefaultAirbyteSource;
import io.airbyte.workers.internal.HeartbeatMonitor;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.KubePortManagerSingleton;
import io.airbyte.workers.process.KubeProcessFactory;
import io.airbyte.workers.test_utils.TestConfigHelpers;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.io.BufferedWriter;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.InetAddress;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.time.Duration;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.tuple.ImmutablePair;

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

  private DefaultAirbyteDestination destination;

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
        .withCpuLimit("1")
        .withCpuRequest("1")
        .withMemoryLimit("1000Mi")
        .withMemoryRequest("1000Mi");
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

    /////////// destiantion ///////////
    final var dstIntegtationLauncher = new AirbyteIntegrationLauncher("2", 0, "airbyte/destination-dev-null:0.2.7", processFactory, resourceReqs, allowedHosts, false, new EnvVariableFeatureFlags());
    this.destination = new DefaultAirbyteDestination(dstIntegtationLauncher);
    final WorkerDestinationConfig dstConfig = new WorkerDestinationConfig()
        .withDestinationConnectionConfiguration(Jsons.jsonNode(Collections.singletonMap("type", "SILENT")));
    destination.start(dstConfig, Path.of(jobRoot));

    final ConcurrentHashMap<AirbyteStreamNameNamespacePair, ImmutablePair<Set<String>, Integer>> validationErrors = new ConcurrentHashMap();
    final Map<AirbyteStreamNameNamespacePair, List<String>> streamToSelectedFields = new HashMap();
    final Map<AirbyteStreamNameNamespacePair, Set<String>> streamToAllFields = new HashMap();
    final Map<AirbyteStreamNameNamespacePair, Set<String>> unexpectedFields = new HashMap();
    populateStreamToAllFields(this.catalog, streamToAllFields);
    final String streamName0 = sourceConfig.getCatalog().getStreams().get(0).getStream().getName();
    final String streamNamespace0 = sourceConfig.getCatalog().getStreams().get(0).getStream().getNamespace();
    final String streamName1 = sourceConfig.getCatalog().getStreams().get(1).getStream().getName();
    final String streamNamespace1 = sourceConfig.getCatalog().getStreams().get(1).getStream().getNamespace();
    final String streamName2 = sourceConfig.getCatalog().getStreams().get(2).getStream().getName();
    final String streamNamespace2 = sourceConfig.getCatalog().getStreams().get(2).getStream().getNamespace();

    final var recordSchemaValidator = new RecordSchemaValidator(
        Map.of(
            new AirbyteStreamNameNamespacePair(streamName0, streamNamespace0),
            sourceConfig.getCatalog().getStreams().get(0).getStream().getJsonSchema(),
            new AirbyteStreamNameNamespacePair(streamName1, streamNamespace1),
            sourceConfig.getCatalog().getStreams().get(1).getStream().getJsonSchema(),
            new AirbyteStreamNameNamespacePair(streamName2, streamNamespace2),
            sourceConfig.getCatalog().getStreams().get(2).getStream().getJsonSchema()
        ),
        true);
    ///////////////////////////////////

    source.start(sourceConfig, Path.of(jobRoot));
    var totalBytes = 0.0;
//    var totalBytesAlt = 0.0;
    var counter = 0L;
    final var start = System.currentTimeMillis();
    log.info("Starting Test");
    while (!source.isFinished()) {
      final Optional<AirbyteMessage> airbyteMessageOptional = source.attemptRead();
      if (airbyteMessageOptional.isPresent()) {
        final AirbyteMessage airbyteMessage = airbyteMessageOptional.get();

        if (airbyteMessage.getRecord() != null) {
          totalBytes += Jsons.getEstimatedByteSize(airbyteMessage.getRecord().getData());
//          totalBytesAlt += airbyteMessage.getRecord().getData().toString().getBytes(Charset.defaultCharset()).length;
          counter++;

          validateSchema(recordSchemaValidator, streamToAllFields, unexpectedFields, validationErrors, airbyteMessage);
          airbyteMessage.getRecord().setStream(airbyteMessage.getRecord().getStream() + "SUFFIX");
          destination.accept(airbyteMessage);
        }

      }

      if (counter > 0 && counter % 1_000_000 == 0) {
        log.info("current throughput: {} totalBytes {}", (totalBytes / 1_000_000.0) / ((System.currentTimeMillis() - start)/ 1000.0), totalBytes);
      }
    }
    log.info("Test Ended");
    final var end = System.currentTimeMillis();
    final var totalMB = totalBytes / 1_000_000.0;
    final var totalTimeSecs = (end - start) / 1000.0;
    final var rps = counter / totalTimeSecs;
    log.info("total secs: {}. total MB read: {}, rps: {}, throughput: {}", totalTimeSecs, totalMB, rps, totalMB / totalTimeSecs);
    source.close();
  }

  private static void populateStreamToAllFields(final ConfiguredAirbyteCatalog catalog, final Map<AirbyteStreamNameNamespacePair, Set<String>> streamToAllFields) {
    final Iterator var2 = catalog.getStreams().iterator();

    while(var2.hasNext()) {
      final ConfiguredAirbyteStream s = (ConfiguredAirbyteStream)var2.next();
      final Set<String> fields = new HashSet();
      final JsonNode propertiesNode = s.getStream().getJsonSchema().findPath("properties");
      if (!propertiesNode.isObject()) {
        throw new RuntimeException("No properties node in stream schema");
      }

      propertiesNode.fieldNames().forEachRemaining((fieldName) -> {
        fields.add(fieldName);
      });
      streamToAllFields.put(AirbyteStreamNameNamespacePair.fromConfiguredAirbyteSteam(s), fields);
    }

  }

  private static void validateSchema(final RecordSchemaValidator recordSchemaValidator, final Map<AirbyteStreamNameNamespacePair, Set<String>> streamToAllFields, final Map<AirbyteStreamNameNamespacePair, Set<String>> unexpectedFields, final ConcurrentHashMap<AirbyteStreamNameNamespacePair, ImmutablePair<Set<String>, Integer>> validationErrors, final AirbyteMessage message) {
    if (message.getRecord() != null) {
      final AirbyteRecordMessage record = message.getRecord();
      final AirbyteStreamNameNamespacePair messageStream = AirbyteStreamNameNamespacePair.fromRecordMessage(record);
      final boolean streamHasLessThenTenErrs = validationErrors.get(messageStream) == null || (Integer)((ImmutablePair)validationErrors.get(messageStream)).getRight() < 10;
      if (streamHasLessThenTenErrs) {
        recordSchemaValidator.validateSchema(record, messageStream, validationErrors);
        final Set<String> unexpectedFieldNames = (Set)unexpectedFields.getOrDefault(messageStream, new HashSet());
        populateUnexpectedFieldNames(record, (Set)streamToAllFields.get(messageStream), unexpectedFieldNames);
        unexpectedFields.put(messageStream, unexpectedFieldNames);
      }

    }
  }

  private static void populateUnexpectedFieldNames(final AirbyteRecordMessage record, final Set<String> fieldsInCatalog, final Set<String> unexpectedFieldNames) {
    final JsonNode data = record.getData();
    if (data.isObject()) {
      final Iterator<String> fieldNamesInRecord = data.fieldNames();

      while(fieldNamesInRecord.hasNext()) {
        final String fieldName = (String)fieldNamesInRecord.next();
        if (!fieldsInCatalog.contains(fieldName)) {
          unexpectedFieldNames.add(fieldName);
        }
      }
    }

  }

  private static <V0, V1> V0 convertProtocolObject(final V1 v1, final Class<V0> klass) {
    return Jsons.object(Jsons.jsonNode(v1), klass);
  }

  void readFromDst() {
    if (this.destination != null) {
      log.info("Start read from destination");
      while (!this.destination.isFinished()) {
        final Optional messageOptional = this.destination.attemptRead();

        if (messageOptional.isPresent()) {
          log.info("msg");
          final AirbyteMessage message = (AirbyteMessage)messageOptional.get();
          if (message.getType() == Type.STATE) {
            message.getState();
          }
        }
      }
    }
    log.info("Done read from destination");
  }
}
