/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.performance;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.protocol.AirbyteMessageMigrator;
import io.airbyte.commons.protocol.AirbyteMessageSerDeProvider;
import io.airbyte.commons.protocol.AirbyteProtocolVersionedMigratorFactory;
import io.airbyte.commons.protocol.ConfiguredAirbyteCatalogMigrator;
import io.airbyte.commons.protocol.serde.AirbyteMessageV0Deserializer;
import io.airbyte.commons.protocol.serde.AirbyteMessageV0Serializer;
import io.airbyte.commons.version.Version;
import io.airbyte.config.AllowedHosts;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.workers.RecordSchemaValidator;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.internal.DefaultAirbyteDestination;
import io.airbyte.workers.internal.DefaultAirbyteSource;
import io.airbyte.workers.internal.HeartbeatMonitor;
import io.airbyte.workers.internal.NamespacingMapper;
import io.airbyte.workers.internal.VersionedAirbyteMessageBufferedWriterFactory;
import io.airbyte.workers.internal.VersionedAirbyteStreamFactory;
import io.airbyte.workers.internal.book_keeping.AirbyteMessageTracker;
import io.airbyte.workers.internal.book_keeping.DefaultSyncStatsTracker;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.KubePortManagerSingleton;
import io.airbyte.workers.process.KubeProcessFactory;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.net.InetAddress;
import java.nio.file.Path;
import java.sql.Timestamp;
import java.time.Duration;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.regex.Pattern;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.logging.log4j.util.Strings;

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
    final var processFactory = new KubeProcessFactory(workerConfigs, "jobs", fabricClient, kubeHeartbeatUrl, false);
    final ResourceRequirements resourceReqs = new ResourceRequirements()
        .withCpuLimit("1.5")
        .withCpuRequest("1.5")
        .withMemoryLimit("2.5Gi")
        .withMemoryRequest("2.5Gi");
    final var heartbeatMonitor = new HeartbeatMonitor(Duration.ofMillis(1));
    final var allowedHosts = new AllowedHosts().withHosts(List.of("*"));
    final var integrationLauncher =
        new AirbyteIntegrationLauncher("1", 0, this.imageName, processFactory, resourceReqs, allowedHosts, false, new EnvVariableFeatureFlags());

    final var serDeProvider = new AirbyteMessageSerDeProvider(List.of(new AirbyteMessageV0Deserializer()), List.of(new AirbyteMessageV0Serializer()));
    serDeProvider.initialize();

    final var msgMigrator = new AirbyteMessageMigrator(List.of());
    msgMigrator.initialize();
    final ConfiguredAirbyteCatalogMigrator catalogMigrator = new ConfiguredAirbyteCatalogMigrator(List.of());
    catalogMigrator.initialize();
    final var migratorFactory = new AirbyteProtocolVersionedMigratorFactory(msgMigrator, catalogMigrator);

    final var versionFac =
        new VersionedAirbyteStreamFactory(serDeProvider, migratorFactory, new Version("0.2.0"), Optional.of(catalog),
            Optional.of(RuntimeException.class));

    final var source = new DefaultAirbyteSource(integrationLauncher, versionFac, heartbeatMonitor, migratorFactory.getProtocolSerializer(new Version("0.2.0")), new EnvVariableFeatureFlags());

    final WorkerSourceConfig sourceConfig = new WorkerSourceConfig()
        .withSourceConnectionConfiguration(this.config)
        .withState(null)
        .withCatalog(convertProtocolObject(this.catalog, io.airbyte.protocol.models.ConfiguredAirbyteCatalog.class));

    // Uncomment to add destination

    /////////// destination ///////////
    final var dstIntegtationLauncher = new AirbyteIntegrationLauncher("1", 0, "airbyte/destination-dev-null:0.2.7", processFactory, resourceReqs,
        allowedHosts, false, new EnvVariableFeatureFlags());

    final var bufferedWriterFac = new VersionedAirbyteMessageBufferedWriterFactory(serDeProvider, migratorFactory, new Version("0.2.0"), Optional.of(catalog));
    this.destination = new DefaultAirbyteDestination(dstIntegtationLauncher,
        versionFac, bufferedWriterFac, migratorFactory.getProtocolSerializer(new Version("0.2.0")));

    final WorkerDestinationConfig dstConfig =
        new WorkerDestinationConfig().withDestinationConnectionConfiguration(Jsons.jsonNode(Collections.singletonMap("type", "SILENT")));
//    destination.start(dstConfig, Path.of(jobRoot));

    // threaded time tracker
    // logging?

//    log.info("Source starting");
//    source.start(sourceConfig, Path.of(jobRoot));
    var totalBytes = 0.0;
    var counter = 0L;
    final var start = System.currentTimeMillis();
    log.info("Starting Test");

    final ConcurrentHashMap<AirbyteStreamNameNamespacePair, ImmutablePair<Set<String>, Integer>> validationErrors = new ConcurrentHashMap();
     final Map<AirbyteStreamNameNamespacePair, List<String>> streamToSelectedFields = new HashMap();
    final Map<AirbyteStreamNameNamespacePair, Set<String>> streamToAllFields = new HashMap();
    final Map<AirbyteStreamNameNamespacePair, Set<String>> unexpectedFields = new HashMap();

    // Examine whether the maps are correct.
//    populatedStreamToSelectedFields(this.catalog, streamToSelectedFields);
//    populateStreamToAllFields(this.catalog, streamToAllFields);

    final String streamName0 = sourceConfig.getCatalog().getStreams().get(0).getStream().getName();
    final String streamNamespace0 = sourceConfig.getCatalog().getStreams().get(0).getStream().getNamespace();
//    final String streamName1 = sourceConfig.getCatalog().getStreams().get(1).getStream().getName();
//    final String streamNamespace1 = sourceConfig.getCatalog().getStreams().get(1).getStream().getNamespace();
//    final String streamName2 = sourceConfig.getCatalog().getStreams().get(2).getStream().getName();
//    final String streamNamespace2 = sourceConfig.getCatalog().getStreams().get(2).getStream().getNamespace();

    final var namespaceMapper = new NamespacingMapper(NamespaceDefinitionType.DESTINATION, "", "");

    final var recordSchemaValidator = new RecordSchemaValidator(
        Map.of(
            new AirbyteStreamNameNamespacePair(streamName0, streamNamespace0),
            sourceConfig.getCatalog().getStreams().get(0).getStream().getJsonSchema()));
//            new AirbyteStreamNameNamespacePair(streamName1, streamNamespace1),
//            sourceConfig.getCatalog().getStreams().get(1).getStream().getJsonSchema(),
//            new AirbyteStreamNameNamespacePair(streamName2, streamNamespace2),
//            sourceConfig.getCatalog().getStreams().get(2).getStream().getJsonSchema()),);

//    while (!source.isFinished()) {
//      final Optional<AirbyteMessage> airbyteMessageOptional = source.attemptRead();
//      if (airbyteMessageOptional.isPresent()) {
//        final AirbyteMessage airbyteMessage = airbyteMessageOptional.get();
//
//        if (airbyteMessage.getRecord() != null) {
//          totalBytes += Jsons.getEstimatedByteSize(airbyteMessage.getRecord().getData());
//
//          validateSchema(recordSchemaValidator, streamToAllFields, unexpectedFields, validationErrors, airbyteMessage);
//
//          // map message function - change to regex?
////          airbyteMessage.getRecord().setStream(airbyteMessage.getRecord().getStream() + "SUFFIX");
//          namespaceMapper.mapMessage(airbyteMessage);
//
//          // filter selected fields function
//          ((ObjectNode) airbyteMessage.getRecord().getData()).retain("id", "user_id", "product_id", "added_to_cart_at", "purchased_at", "name",
//              "email",
//              "title", "gender", "height", "language", "blood_type", "created_at", "occupation", "updated_at", "nationality");
//
//          // message tracker?
//
//          counter++;
//          destination.accept(airbyteMessage);
//        }
//
//      }
//
//      // In the platform, we log every 1000.
//      if (counter > 0 && counter % 1_000_000 == 0) {
//        log.info("current throughput: {} total MB {}", (totalBytes / 1_000_000.0) / ((System.currentTimeMillis() - start) / 1000.0),
//            totalBytes / 1_000_000.0);
//      }
//    }
    var syncStats = new DefaultSyncStatsTracker();
    var tracker = new AirbyteMessageTracker(syncStats, new EnvVariableFeatureFlags());
//    var runner = TestRunnable.readFromSrcAndWriteToDstRunnable(
//        source, destination, catalog, new AtomicBoolean(false), namespaceMapper, tracker, Map.of(), recordSchemaValidator, new ThreadedTimeTracker(), UUID.randomUUID(), true);
//
//    // TWO MAIN RUNNABLES
//    final ExecutorService executors = Executors.newFixedThreadPool(2);
//    final CompletableFuture<Void> readSrcAndWriteDstThread = CompletableFuture.runAsync(() -> {
//      try {
//        runner.run();
//      } catch (final Exception e) {
//        throw new RuntimeException(e);
//      }
//    }, executors);
//
//    final CompletableFuture<Void> readFromDstThread = CompletableFuture.runAsync(() -> {
//      try {
//        Thread.sleep(20_000);
//        readFromDst();
//      } catch (final InterruptedException e) {
//        throw new RuntimeException(e);
//      }
//    }, executors);
//
//    CompletableFuture.anyOf(readSrcAndWriteDstThread, readFromDstThread).get();
//    LogClientSingleton.getInstance().setJobMdc(WorkerEnvironment.KUBERNETES, new EnvConfigs().getLogConfigs(), Path.of("/16-april/" +
//        new Timestamp(System.currentTimeMillis()).toInstant()));
    var worker = new DefaultReplicationWorkerTester(
        "1", 0, source, namespaceMapper, destination, tracker,  recordSchemaValidator,  true, false, null);
    var output = worker.run(sourceConfig, dstConfig, Path.of("/"));

    log.info("Test Ended");
    final var end = System.currentTimeMillis();
//    final var totalMB = totalBytes / 1_000_000.0;
    final var totalMB = syncStats.getTotalBytesEmitted() / 1_000_000.0;
//    final var totalTimeSecs = (end - start) / 1000.0;
    final var totalTimeSecs = (output.getReplicationAttemptSummary().getTotalStats().getDestinationWriteEndTime() -
        output.getReplicationAttemptSummary().getTotalStats().getDestinationWriteStartTime()) / 1000.0;
    counter = syncStats.getTotalRecordsEmitted();
    final var rps = counter / totalTimeSecs;
    log.info("total secs: {}. total MB read: {}, rps: {}, throughput: {}", totalTimeSecs, totalMB, rps, totalMB / totalTimeSecs);
    source.close();
  }

  private static <V0, V1> V0 convertProtocolObject(final V1 v1, final Class<V0> klass) {
    return Jsons.object(Jsons.jsonNode(v1), klass);
  }

  // Uncomment to add destination

  void readFromDst() {
    if (this.destination != null) {
      log.info("Start read from destination");
      while (!this.destination.isFinished()) {
        final Optional messageOptional =
            this.destination.attemptRead();

        if (messageOptional.isPresent()) {
          log.info("msg");
          final AirbyteMessage message =
              (AirbyteMessage) messageOptional.get();
          if (message.getType() == Type.STATE) {
            message.getState();
          }
        }
      }
    }
    log.info("Done read from destination");
  }

}
