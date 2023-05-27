/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.function.Consumer;
import java.util.stream.IntStream;
import lombok.extern.slf4j.Slf4j;

/**
 * This source is optimized for creating records very fast. It optimizes for speed over flexibility.
 */
@Slf4j
public class SpeedBenchmarkSource extends BaseConnector implements Source {

  @Override
  public AirbyteConnectionStatus check(final JsonNode jsonConfig) {
    try {
      final SpeedBenchmarkConfig sourceConfig = SpeedBenchmarkConfig.parseFromConfig(jsonConfig);
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED).withMessage("Source config: " + sourceConfig);
    } catch (final Exception e) {
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(e.getMessage());
    }
  }

  @Override
  public AirbyteCatalog discover(final JsonNode jsonConfig) {
    final SpeedBenchmarkConfig sourceConfig = SpeedBenchmarkConfig.parseFromConfig(jsonConfig);
    return sourceConfig.getCatalog();
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config, final ConfiguredAirbyteCatalog catalog, final JsonNode state) {
    return null;
  }

  @Override
  public void read(final JsonNode config,
                   final ConfiguredAirbyteCatalog catalog,
                   final JsonNode state,
                   final Consumer<AirbyteMessage> outputRecordCollector) {
    final SpeedBenchmarkConfig sourceConfig = SpeedBenchmarkConfig.parseFromConfig(config);
    // if (sourceConfig.threadCount() == 1) {
    // thread(1, sourceConfig, outputRecordCollector);
    // } else {
    final int threadCount = 2;
    log.info("using {} threads", threadCount);
    // final ExecutorService workerPool = Executors.newFixedThreadPool(sourceConfig.streamCount());
    final ExecutorService workerPool = Executors.newFixedThreadPool(threadCount);
    // keep counting 1 indexed to be consistent with the rest of the source.
    final CompletableFuture<?>[] futures = IntStream.range(1, sourceConfig.threadCount() + 1)
        .mapToObj(i -> CompletableFuture.runAsync(() -> thread(i, sourceConfig, outputRecordCollector), workerPool))
        .toArray(CompletableFuture[]::new);

    CompletableFuture.allOf(futures);
    workerPool.shutdown();
    // }
  }

  void thread(final int threadNum, final SpeedBenchmarkConfig sourceConfig, final Consumer<AirbyteMessage> outputRecordCollector) {
    try (final AutoCloseableIterator<AirbyteMessage> itr = AutoCloseableIterators.fromIterator(new SpeedBenchmark5ColumnGeneratorIterator(
        sourceConfig.maxRecords(),
        sourceConfig.streamCount(),
        threadNum))) {
      itr.forEachRemaining(outputRecordCollector::accept);
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

}
