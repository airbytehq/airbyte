/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_performance;

import static java.lang.Thread.sleep;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AllowedHosts;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.internal.DefaultAirbyteDestination;
import io.airbyte.workers.internal.exception.DestinationException;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.KubePortManagerSingleton;
import io.airbyte.workers.process.KubeProcessFactory;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import java.io.BufferedReader;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.InetAddress;
import java.net.URL;
import java.net.UnknownHostException;
import java.nio.channels.Channels;
import java.nio.channels.FileChannel;
import java.nio.channels.ReadableByteChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;
import java.util.Optional;
import java.util.Random;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.regex.Pattern;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This is a crude copy of {@link io.airbyte.workers.general.DefaultReplicationWorker} where if that
 * class changes this class will need to be updated to match as this class mocks the functionality
 * of the platform from the perspectives of the platform communicating with the destination by
 * sending AirbyteRecordMessages the same way platform pipes data into the destination
 */
public class PerformanceHarness {

  private static final Logger log = LoggerFactory.getLogger(PerformanceHarness.class);
  public static final int PORT1 = 9877;
  public static final int PORT2 = 9878;
  public static final int PORT3 = 9879;
  public static final int PORT4 = 9880;
  public static final int STATE_FREQUENCY = 10000;

  public static final Set<Integer> PORTS = Set.of(PORT1, PORT2, PORT3, PORT4);

  public static final double MEGABYTE = Math.pow(1024, 2);
  private final String imageName;
  private final JsonNode config;
  private final ConfiguredAirbyteCatalog catalog;
  private final String dataSourceURL;

  private DefaultAirbyteDestination destination;

  PerformanceHarness(final String imageName, final String config, final String catalog, final String datasource) throws JsonProcessingException {
    final ObjectMapper mapper = new ObjectMapper();
    this.imageName = imageName;
    this.config = mapper.readTree(config);
    this.catalog = Jsons.deserialize(catalog, ConfiguredAirbyteCatalog.class);
    this.dataSourceURL = datasource;
  }

  /**
   * Runs destination performance harness
   * <p>
   * 1. Spins up a destination connector
   * <p>
   * 2. Loads data from URL
   * <p>
   * 3. Processes each record and sends to destination
   * <p>
   * 4. Tears down destination after completion
   *
   * @throws Exception
   */
  void runTest() throws Exception {
    final List<String> streamNames = catalog.getStreams().stream().map(stream -> stream.getStream().getName()).toList();
    final Random random = new Random();
    final AirbyteIntegrationLauncher dstIntegtationLauncher = getAirbyteIntegrationLauncher();
    final WorkerDestinationConfig dstConfig = new WorkerDestinationConfig()
        .withDestinationConnectionConfiguration(this.config)
        .withState(null)
        .withCatalog(convertProtocolObject(this.catalog, ConfiguredAirbyteCatalog.class));
    this.destination = new DefaultAirbyteDestination(dstIntegtationLauncher);
    final var jobRoot = "/";
    log.info("Destination starting");
    destination.start(dstConfig, Path.of(jobRoot));

    // Try read logs.
    final var logListener = CompletableFuture.runAsync(() -> {
      log.info("Listening to destination logs");
      while (!destination.isFinished()) {
        final Optional<AirbyteMessage> messageOptional;
        try {
          messageOptional = destination.attemptRead();
          messageOptional.ifPresent(airbyteMessage -> log.info("dst log: {}", airbyteMessage));

        } catch (final Exception e) {
          throw new DestinationException("Destination process read attempt failed", e);
        }
      }
    });

    final String syncMode = this.catalog.getStreams().get(0).getSyncMode().name();

    final BufferedReader reader = loadFileFromUrl();

    final Pattern pattern = Pattern.compile(",");
    final String columnsString = reader.readLine();
    log.info("header line: {}", columnsString);
    final List<String> columns = Arrays.asList(pattern.split(columnsString));
    double totalBytes = 0.0;
    long counter = 0L;
    final long start = System.currentTimeMillis();

    try (reader) {
      while (true) {
        final String line = reader.readLine();
        if (line == null) {
          log.info("End of datasource after {} lines", counter);
          break;
        }
        final List<String> row;
        try {
          row = Arrays.asList(pattern.split(line));
        } catch (final NullPointerException npe) {
          log.warn("Bad line: {} {} {}", line, counter, totalBytes);
          continue;
        }
        assert (row.size() == columns.size());
        final String recordString = buildRecordString(columns, row);
        final AirbyteMessage airbyteMessage = new AirbyteMessage()
            .withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(getStreamName(streamNames, random))
                .withNamespace(catalog.getStreams().get(0).getStream().getNamespace())
                .withData(Jsons.deserialize(recordString)));
        airbyteMessage.getRecord().setEmittedAt(start);
        destination.accept(airbyteMessage);

        totalBytes += recordString.length();
        counter++;
        if (counter > 0 && counter % MEGABYTE == 0) {
          log.info("current throughput({}): {} total MB {}", counter, (totalBytes / MEGABYTE) / ((System.currentTimeMillis() - start) / 1000.0),
              totalBytes / MEGABYTE);
        }

        // If sync mode is incremental, send state message every 10,000 records
        if (syncMode.equals("INCREMENTAL") && counter % STATE_FREQUENCY == 0) {
          final AirbyteMessage stateMessage = new AirbyteMessage()
              .withType(Type.STATE)
              .withState(new AirbyteStateMessage()
                  .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                  .withData(Jsons.deserialize("{\"checkpoint\": \"" + counter + "\"}")));
          destination.accept(stateMessage);
        }
      }
    }
    destination.notifyEndOfInput();
    while (!destination.isFinished()) {
      log.info("Waiting for destination to finish");
      sleep(500);
    }
    destination.close();
    logListener.cancel(true);
    log.info("Test ended successfully");
    computeThroughput(totalBytes, counter, start);
    // TODO: (ryankfu) when incremental syncs are supported, add a tearDown method to clear table
  }

  // TODO: (ryankfu) get less hacky way to generate multiple streams
  @VisibleForTesting
  static String getStreamName(final List<String> listOfStreamNames, final Random random) {
    return listOfStreamNames.get(random.nextInt(listOfStreamNames.size()));
  }

  private void computeThroughput(final double totalBytes, final long counter, final long start) {
    final var end = System.currentTimeMillis();
    final var totalMB = totalBytes / MEGABYTE;
    final var totalTimeSecs = (end - start) / 1000.0;
    final var rps = counter / totalTimeSecs;
    log.info("total secs: {}. total MB read: {}, rps: {}, throughput: {}", totalTimeSecs, totalMB, rps, totalMB / totalTimeSecs);
  }

  private AirbyteIntegrationLauncher getAirbyteIntegrationLauncher() throws UnknownHostException {
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
    final AllowedHosts allowedHosts = new AllowedHosts().withHosts(List.of("*"));
    return new AirbyteIntegrationLauncher("1", 0, this.imageName, processFactory, resourceReqs,
        allowedHosts, false, new EnvVariableFeatureFlags());
  }

  private String buildRecordString(final List<String> columns, final List<String> row) {
    final StringBuilder sb = new StringBuilder();
    sb.append("{");
    final Iterator<String> rowIterator = row.iterator();
    final Iterator<String> colIterator = columns.iterator();
    final ArrayList<String> combined = new ArrayList<>(columns.size());
    while (colIterator.hasNext() && rowIterator.hasNext()) {
      combined.add("\"%s\":\"%s\"".formatted(colIterator.next(), rowIterator.next()));
    }
    sb.append(String.join(",", combined));
    sb.append("}");
    return sb.toString();
  }

  private BufferedReader loadFileFromUrl() throws IOException {
    log.info("Get datasource {}", this.dataSourceURL);
    final Path temp = Files.createTempFile("", ".tmp");
    final URL url = new URL(this.dataSourceURL.trim());
    final ReadableByteChannel readableByteChannel = Channels.newChannel(url.openStream());
    final FileOutputStream fileOutputStream = new FileOutputStream(temp.toString());
    final FileChannel fileChannel = fileOutputStream.getChannel();
    final long bytes = fileChannel.transferFrom(readableByteChannel, 0, Long.MAX_VALUE);
    readableByteChannel.close();
    fileOutputStream.close();
    log.info("done saving datasource {} ({})", temp, bytes);
    return Files.newBufferedReader(temp, StandardCharsets.UTF_8);
  }

  private static <V0, V1> V0 convertProtocolObject(final V1 v1, final Class<V0> klass) {
    return Jsons.object(Jsons.jsonNode(v1), klass);
  }

}
