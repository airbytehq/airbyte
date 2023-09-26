/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.InsertAllRequest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.bigquery.uploader.AbstractBigQueryUploader;
import io.airbyte.integrations.destination_async.DestinationFlushFunction;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.StreamDescriptor;

import java.util.Map;
import java.util.concurrent.ConcurrentMap;
import java.util.function.Supplier;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class BigQueryAsyncStandardFlush implements DestinationFlushFunction {

  private final BigQuery bigQuery;
  private final Supplier<ConcurrentMap<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>>> uploaderMap;

  public BigQueryAsyncStandardFlush(BigQuery bigQuery,
                                    Supplier<ConcurrentMap<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>>> uploaderMap) {
    this.bigQuery = bigQuery;
    this.uploaderMap = uploaderMap;
  }

  @Override
  public void flush(final StreamDescriptor decs, final Stream<PartialAirbyteMessage> stream) throws Exception {
    // ConcurrentMap<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMapSupplied = uploaderMap.get();
    InsertAllRequest.Builder request = InsertAllRequest.newBuilder(decs.getNamespace(), decs.getName());
    stream.forEach(aibyteMessage -> {
      try {
        request.addRow(Jsons.deserialize(aibyteMessage.getSerialized(), Map.class));
         /*AirbyteStreamNameNamespacePair sd = new AirbyteStreamNameNamespacePair(aibyteMessage.getRecord().getStream(),
            aibyteMessage.getRecord().getNamespace());
        uploaderMapSupplied.get(sd).upload(aibyteMessage);*/
      } catch (Exception e) {
        log.error("BQ async standard flush");
        log.error(aibyteMessage.toString());
        throw e;
      }
    });
    bigQuery.insertAll(request.build());
    // uploaderMapSupplied.values().forEach(test -> test.closeAfterPush());
  }

  @Override
  public long getOptimalBatchSizeBytes() {
    // todo(ryankfu): this should be per-destination specific. currently this is for Snowflake.
    // The size chosen is currently for improving the performance of low memory connectors. With 1 Gi of
    // resource the connector will usually at most fill up around 150 MB in a single queue. By lowering
    // the batch size, the AsyncFlusher will flush in smaller batches which allows for memory to be
    // freed earlier similar to a sliding window effect
    return 25 * 1024 * 1024;
  }

}
