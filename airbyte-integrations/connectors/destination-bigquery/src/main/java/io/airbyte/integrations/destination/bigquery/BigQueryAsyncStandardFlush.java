/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.BigQuery;
import com.google.common.util.concurrent.RateLimiter;
import io.airbyte.cdk.integrations.destination_async.DestinationFlushFunction;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.integrations.destination.bigquery.uploader.AbstractBigQueryUploader;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class BigQueryAsyncStandardFlush implements DestinationFlushFunction {

  // TODO remove this once the async framework supports rate-limiting/backpressuring
  private static final RateLimiter rateLimiter = RateLimiter.create(0.07);

  private final BigQuery bigQuery;
  private final Supplier<ConcurrentMap<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>>> uploaderMap;

  public BigQueryAsyncStandardFlush(final BigQuery bigQuery,
                                    final Supplier<ConcurrentMap<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>>> uploaderMap) {
    this.bigQuery = bigQuery;
    this.uploaderMap = uploaderMap;
  }

  @Override
  public void flush(final StreamDescriptor decs, final Stream<PartialAirbyteMessage> stream) throws Exception {
    rateLimiter.acquire();
    final ConcurrentMap<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMapSupplied = uploaderMap.get();
    final AtomicInteger recordCount = new AtomicInteger();
    stream.forEach(aibyteMessage -> {
      try {
        final AirbyteStreamNameNamespacePair sd = new AirbyteStreamNameNamespacePair(aibyteMessage.getRecord().getStream(),
            aibyteMessage.getRecord().getNamespace());
        uploaderMapSupplied.get(sd).upload(aibyteMessage);
        recordCount.getAndIncrement();
      } catch (final Exception e) {
        log.error("An error happened while trying to flush a record to big query", e);
        throw e;
      }
    });
    uploaderMapSupplied.values().forEach(test -> test.closeAfterPush());
  }

  @Override
  public long getOptimalBatchSizeBytes() {
    // todo(ryankfu): this should be per-destination specific. currently this is for Snowflake.
    // The size chosen is currently for improving the performance of low memory connectors. With 1 Gi of
    // resource the connector will usually at most fill up around 150 MB in a single queue. By lowering
    // the batch size, the AsyncFlusher will flush in smaller batches which allows for memory to be
    // freed earlier similar to a sliding window effect
    return Double.valueOf(Runtime.getRuntime().maxMemory() * 0.2).longValue();
  }

}
