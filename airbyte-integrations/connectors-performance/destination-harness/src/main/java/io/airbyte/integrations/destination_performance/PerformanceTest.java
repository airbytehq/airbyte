/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_performance;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AllowedHosts;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.workers.RecordSchemaValidator;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.internal.DefaultAirbyteDestination;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.KubePortManagerSingleton;
import io.airbyte.workers.process.KubeProcessFactory;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.InetAddress;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.regex.Pattern;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.tuple.ImmutablePair;

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
        .withCpuLimit("2.5")
        .withCpuRequest("2.5")
        .withMemoryLimit("2Gi")
        .withMemoryRequest("2Gi");
    final var allowedHosts = new AllowedHosts().withHosts(List.of("*"));
    final var jobRoot = "/";

    final var dstIntegtationLauncher = new AirbyteIntegrationLauncher(
        "2",
        0,
        this.imageName,
        processFactory,
        resourceReqs,
        allowedHosts,
        false,
        new EnvVariableFeatureFlags());
    this.destination = new DefaultAirbyteDestination(dstIntegtationLauncher);
    final WorkerDestinationConfig dstConfig = new WorkerDestinationConfig()
        .withDestinationConnectionConfiguration(this.config)
        .withState(null)
        .withCatalog(convertProtocolObject(this.catalog, io.airbyte.protocol.models.ConfiguredAirbyteCatalog.class));
    log.info("Destination starting");
    destination.start(dstConfig, Path.of(jobRoot));

    BufferedReader reader = new BufferedReader(new InputStreamReader(
        new URL("https://storage.googleapis.com/airbyte-performance-testing-public/sample-data/faker_1m/users.csv").openStream(),
        StandardCharsets.UTF_8));

    var totalBytes = 0.0;
    var counter = 0L;
    final Pattern pattern = Pattern.compile(",");
    final var start = System.currentTimeMillis();

    log.info("Starting Test");
    final var columns = Arrays.asList(pattern.split(reader.readLine()));
    while (!destination.isFinished()) {
      try (reader) {
        final var row = Arrays.asList(pattern.split(reader.readLine()));
        assert (row.size() == columns.size());
        StringBuilder sb = new StringBuilder();
        sb.append("{");
        Iterator<String> rowIterator = row.iterator();
        Iterator<String> colIterator = columns.iterator();
        ArrayList<String> combined = new ArrayList<>(columns.size());
        while (colIterator.hasNext() && rowIterator.hasNext()) {
          combined.add("\"%s\":\"%s\"".formatted(colIterator.next(), rowIterator.next()));
        }
        sb.append(String.join(",", combined));
        sb.append("}");
        final String recordString = sb.toString();
        totalBytes += recordString.length();

        final AirbyteMessage airbyteMessage = new AirbyteMessage().withRecord(new AirbyteRecordMessage()
            .withStream(catalog.getStreams().get(0).getStream().getName())
            .withNamespace(catalog.getStreams().get(0).getStream().getNamespace())
            .withData(Jsons.deserialize(recordString)));
        destination.accept(airbyteMessage);
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
    destination.close();
  }

  private static void populateStreamToAllFields(final ConfiguredAirbyteCatalog catalog,
                                                final Map<AirbyteStreamNameNamespacePair, Set<String>> streamToAllFields) {
    final Iterator var2 = catalog.getStreams().iterator();

    while (var2.hasNext()) {
      final ConfiguredAirbyteStream s = (ConfiguredAirbyteStream) var2.next();
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

  private static void validateSchema(final RecordSchemaValidator recordSchemaValidator,
                                     final Map<AirbyteStreamNameNamespacePair, Set<String>> streamToAllFields,
                                     final Map<AirbyteStreamNameNamespacePair, Set<String>> unexpectedFields,
                                     final ConcurrentHashMap<AirbyteStreamNameNamespacePair, ImmutablePair<Set<String>, Integer>> validationErrors,
                                     final AirbyteMessage message) {
    if (message.getRecord() != null) {
      final AirbyteRecordMessage record = message.getRecord();
      final AirbyteStreamNameNamespacePair messageStream = AirbyteStreamNameNamespacePair.fromRecordMessage(record);
      final boolean streamHasLessThenTenErrs =
          validationErrors.get(messageStream) == null || (Integer) ((ImmutablePair) validationErrors.get(messageStream)).getRight() < 10;
      if (streamHasLessThenTenErrs) {
        recordSchemaValidator.validateSchema(record, messageStream, validationErrors);
        final Set<String> unexpectedFieldNames = (Set) unexpectedFields.getOrDefault(messageStream, new HashSet());
        populateUnexpectedFieldNames(record, (Set) streamToAllFields.get(messageStream), unexpectedFieldNames);
        unexpectedFields.put(messageStream, unexpectedFieldNames);
      }

    }
  }

  private static void populateUnexpectedFieldNames(final AirbyteRecordMessage record,
                                                   final Set<String> fieldsInCatalog,
                                                   final Set<String> unexpectedFieldNames) {
    final JsonNode data = record.getData();
    if (data.isObject()) {
      final Iterator<String> fieldNamesInRecord = data.fieldNames();

      while (fieldNamesInRecord.hasNext()) {
        final String fieldName = (String) fieldNamesInRecord.next();
        if (!fieldsInCatalog.contains(fieldName)) {
          unexpectedFieldNames.add(fieldName);
        }
      }
    }

  }

  private static <V0, V1> V0 convertProtocolObject(final V1 v1, final Class<V0> klass) {
    return Jsons.object(Jsons.jsonNode(v1), klass);
  }

  // Uncomment to add destination
  /*
   * void readFromDst() { if (this.destination != null) { log.info("Start read from destination");
   * while (!this.destination.isFinished()) { final Optional messageOptional =
   * this.destination.attemptRead();
   *
   * if (messageOptional.isPresent()) { log.info("msg"); final AirbyteMessage message =
   * (AirbyteMessage)messageOptional.get(); if (message.getType() == Type.STATE) { message.getState();
   * } } } } log.info("Done read from destination"); }
   */
}
