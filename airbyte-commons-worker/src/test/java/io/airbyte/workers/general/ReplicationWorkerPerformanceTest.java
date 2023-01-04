package io.airbyte.workers.general;

import com.google.common.collect.Lists;
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
import io.airbyte.workers.internal.book_keeping.AirbyteMessageTracker;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicReference;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ReplicationWorkerPerformanceTest {

  public static void main(String[] args) throws InterruptedException {
    final var perSource = new LimitedAirbyteSource();
    final var perDestination = new EmptyAirbyteDestination();
    final var messageTracker = new AirbyteMessageTracker();
    final var metricReporter = new WorkerMetricReporter(new NotImplementedMetricClient(), "test-image:0.01");
    final var mapper = new StubAirbyteMapper();
    final var validator = new RecordSchemaValidator(Map.of(
        new AirbyteStreamNameNamespacePair("s1", null),
        CatalogHelpers.fieldsToJsonSchema(io.airbyte.protocol.models.Field.of("data", JsonSchemaType.STRING))));
//    final var validator = new RecordSchemaValidator(Map.of());

    final var worker = new DefaultReplicationWorker("1", 0,
        perSource,
        mapper,
        perDestination,
        messageTracker,
        validator,
        metricReporter,
        false
        );
    final AtomicReference<ReplicationOutput> output = new AtomicReference<>();
    final Thread workerThread = new Thread(() -> {
      try {
        output.set(worker.run(new StandardSyncInput().withCatalog(new ConfiguredAirbyteCatalog()
                .withStreams(List.of(
                    new ConfiguredAirbyteStream().withSyncMode(SyncMode.FULL_REFRESH).withStream(
                        CatalogHelpers.createAirbyteStream(
                                "s1",
                                "models_schema",
                                io.airbyte.protocol.models.Field.of("data", JsonSchemaType.STRING)))
                ))),
            Path.of("/")));
      } catch (final WorkerException e) {
        throw new RuntimeException(e);
      }
    });

    workerThread.start();
    workerThread.join();
    final var summary = output.get().getReplicationAttemptSummary();
    final var mbRead = summary.getBytesSynced()/1_000_000;
    final var timeTakenSec = (summary.getEndTime() - summary.getStartTime())/1000.0;
    log.info("MBs read: {}, Time taken sec: {}, MB/s: {}", mbRead, timeTakenSec, mbRead/timeTakenSec);
  }
}
