/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_performance;

import static java.lang.Thread.sleep;

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
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
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
import java.io.FileReader;
import java.net.InetAddress;
import java.net.URL;
import java.nio.channels.Channels;
import java.nio.channels.FileChannel;
import java.nio.channels.ReadableByteChannel;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.regex.Pattern;
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
  private final String dataSourceURL;

  private DefaultAirbyteDestination destination;

  PerformanceTest(final String imageName, final String config, final String catalog, final String datasource) throws JsonProcessingException {
    final ObjectMapper mapper = new ObjectMapper();
    this.imageName = imageName;
    this.config = mapper.readTree(config);
    this.catalog = Jsons.deserialize(catalog, ConfiguredAirbyteCatalog.class);
    this.dataSourceURL = datasource;
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
    var dstIntegtationLauncher = new AirbyteIntegrationLauncher("1", 0, this.imageName, processFactory, resourceReqs,
        allowedHosts, false, new EnvVariableFeatureFlags());
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

    log.info("Get datasource {}", this.dataSourceURL);
    Path temp = Files.createTempFile("", ".tmp");
    final URL url = new URL(this.dataSourceURL.trim());
    ReadableByteChannel readableByteChannel = Channels.newChannel(url.openStream());
    FileOutputStream fileOutputStream = new FileOutputStream(temp.toString());
    FileChannel fileChannel = fileOutputStream.getChannel();
    final var bytes = fileChannel.transferFrom(readableByteChannel, 0, Long.MAX_VALUE);
    readableByteChannel.close();
    fileOutputStream.close();
    log.info("done saving datasource {} ({})", temp.toString(), bytes);
    BufferedReader reader = new BufferedReader(new FileReader(temp.toString()));

    log.info("Reading datasource header");
    final var columnsString = reader.readLine();
    log.info("header line: {}", columnsString);
    final Pattern pattern = Pattern.compile(",");
    final var columns = Arrays.asList(pattern.split(columnsString));
    var totalBytes = 0.0;
    var counter = 0L;
    final var start = System.currentTimeMillis();

    try (reader) {
      while (true) {
        String line = reader.readLine();
        if (line == null) {
          log.info("End of datasource after {} lines", counter);
          break;
        }
        final List row;
        try {
          row = Arrays.asList(pattern.split(line));
        } catch (NullPointerException npe) {
          log.warn("Bad line: {} {} {}", line, counter, totalBytes);
          continue;
        }
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
        // log.info("*** RECORD: {}", recordString); // TEMP
        totalBytes += recordString.length();
        counter++;
        final AirbyteMessage airbyteMessage = new AirbyteMessage()
            .withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(catalog.getStreams().get(0).getStream().getName())
                .withNamespace(catalog.getStreams().get(0).getStream().getNamespace())
                .withData(Jsons.deserialize(recordString)));
        airbyteMessage.getRecord().setEmittedAt(start);
        destination.accept(airbyteMessage);

        if (counter > 0 && counter % MEGABYTE == 0) {
          log.info("current throughput({}): {} total MB {}", counter, (totalBytes / MEGABYTE) / ((System.currentTimeMillis() - start) / 1000.0),
              totalBytes / MEGABYTE);
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
    final var end = System.currentTimeMillis();
    final var totalMB = totalBytes / MEGABYTE;
    final var totalTimeSecs = (end - start) / 1000.0;
    final var rps = counter / totalTimeSecs;

    log.info("total secs: {}. total MB read: {}, rps: {}, throughput: {}", totalTimeSecs, totalMB, rps, totalMB / totalTimeSecs);
  }

  private static <V0, V1> V0 convertProtocolObject(final V1 v1, final Class<V0> klass) {
    return Jsons.object(Jsons.jsonNode(v1), klass);
  }

}
