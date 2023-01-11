/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.metrics.lib.NotImplementedMetricClient;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.workers.RecordSchemaValidator;
import io.airbyte.workers.WorkerMetricReporter;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.helper.ConnectorConfigUpdater;
import io.airbyte.workers.internal.NamespacingMapper;
import io.airbyte.workers.internal.book_keeping.AirbyteMessageTracker;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicReference;
import lombok.extern.slf4j.Slf4j;
import org.mockito.Mockito;
import org.openjdk.jmh.annotations.Benchmark;
import org.openjdk.jmh.annotations.BenchmarkMode;
import org.openjdk.jmh.annotations.Fork;
import org.openjdk.jmh.annotations.Measurement;
import org.openjdk.jmh.annotations.Mode;
import org.openjdk.jmh.annotations.Warmup;

@Slf4j
public class ReplicationWorkerPerformanceTest {

  /**
   * Hook up the DefaultReplicationWorker to a test harness with an insanely quick Source
   * {@link LimitedAirbyteSource} and Destination {@link EmptyAirbyteDestination}.
   * <p>
   * Harness uses Java Micro Benchmark to run the E2E sync a configured number of times. It then
   * reports a time distribution for the time taken to run the E2E sync.
   * <p>
   * Because the reported time does not explicitly include throughput numbers, throughput logging has
   * been added. This class is intended to help devs understand the impact of changes on throughput.
   * <p>
   * To use this, simply run the main method, make yourself a cup of coffee for 5 mins, then look the
   * logs.
   */
  @Benchmark
  // SampleTime = the time taken to run the benchmarked method. Use this because we only care about
  // the time taken to sync the entire dataset.
  @BenchmarkMode(Mode.SampleTime)
  // Warming up the JVM stabilises results however takes longer. Skip this for now since we don't need
  // that fine a result.
  @Warmup(iterations = 0)
  // How many runs to do.
  @Fork(1)
  // Within each run, how many iterations to do.
  @Measurement(iterations = 2)
  public void executeOneSync() throws InterruptedException {
    final var perSource = new LimitedAirbyteSource();
    final var perDestination = new EmptyAirbyteDestination();
    final var messageTracker = new AirbyteMessageTracker(new EnvVariableFeatureFlags());
    final var connectorConfigUpdater = Mockito.mock(ConnectorConfigUpdater.class);
    final var metricReporter = new WorkerMetricReporter(new NotImplementedMetricClient(), "test-image:0.01");
    final var dstNamespaceMapper = new NamespacingMapper(NamespaceDefinitionType.DESTINATION, "", "");
    final var validator = new RecordSchemaValidator(Map.of(
        new AirbyteStreamNameNamespacePair("s1", null),
        CatalogHelpers.fieldsToJsonSchema(io.airbyte.protocol.models.Field.of("data", JsonSchemaType.STRING))));

    final var worker = new DefaultReplicationWorker("1", 0,
        perSource,
        dstNamespaceMapper,
        perDestination,
        messageTracker,
        validator,
        metricReporter,
        connectorConfigUpdater,
        false);
    final AtomicReference<ReplicationOutput> output = new AtomicReference<>();
    final Thread workerThread = new Thread(() -> {
      try {
        output.set(worker.run(new StandardSyncInput().withCatalog(new ConfiguredAirbyteCatalog()
            .withStreams(List.of(new ConfiguredAirbyteStream().withSyncMode(SyncMode.FULL_REFRESH).withStream(new AirbyteStream().withName("s1"))))),
            Path.of("/")));
      } catch (final WorkerException e) {
        throw new RuntimeException(e);
      }
    });

    workerThread.start();
    workerThread.join();
    final var summary = output.get().getReplicationAttemptSummary();
    final var mbRead = summary.getBytesSynced() / 1_000_000;
    final var timeTakenSec = (summary.getEndTime() - summary.getStartTime()) / 1000.0;
    log.info("MBs read: {}, Time taken sec: {}, MB/s: {}", mbRead, timeTakenSec, mbRead / timeTakenSec);
  }

  public static void main(final String[] args) throws IOException {
    // Run this main class to start benchmarking.
    org.openjdk.jmh.Main.main(args);
  }

}
