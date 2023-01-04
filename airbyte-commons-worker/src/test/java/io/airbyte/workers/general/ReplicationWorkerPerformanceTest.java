/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.metrics.lib.NotImplementedMetricClient;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.workers.RecordSchemaValidator;
import io.airbyte.workers.WorkerMetricReporter;
import io.airbyte.workers.exception.WorkerException;
import io.airbyte.workers.internal.book_keeping.AirbyteMessageTracker;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicReference;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ReplicationWorkerPerformanceTest {

  public static void main(String[] args) throws WorkerException, InterruptedException {
    var perSource = new LimitedAirbyteSource();
    var perDestination = new EmptyAirbyteDestination();
    var messageTracker = new AirbyteMessageTracker();
    var metricReporter = new WorkerMetricReporter(new NotImplementedMetricClient(), "test-image:0.01");
    var mapper = new StubAirbyteMapper();
    var validator = new RecordSchemaValidator(Map.of());

    var worker = new DefaultReplicationWorker("1", 0,
        perSource,
        mapper,
        perDestination,
        messageTracker,
        validator,
        metricReporter,
        false);
    AtomicReference<ReplicationOutput> output = new AtomicReference<>();
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
    var summary = output.get().getReplicationAttemptSummary();
    var mbRead = summary.getBytesSynced() / 1_000_000;
    var timeTakenSec = (summary.getEndTime() - summary.getStartTime()) / 1000.0;
    log.info("MBs read: {}, Time taken sec: {}, MB/s: {}", mbRead, timeTakenSec, mbRead / timeTakenSec);
  }

}
