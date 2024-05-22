/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import io.airbyte.cdk.integrations.destination.async.AsyncStreamConsumer;
import io.airbyte.cdk.integrations.destination.async.buffers.BufferManager;
import io.airbyte.cdk.integrations.destination.async.state.FlushFailure;
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction;
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.integrations.destination.bigquery.uploader.BigQueryDirectUploader;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.Optional;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.Executors;
import java.util.function.Consumer;
import java.util.function.Supplier;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@SuppressWarnings("try")
public class BigQueryRecordStandardConsumer extends AsyncStreamConsumer {

  public BigQueryRecordStandardConsumer(Consumer<AirbyteMessage> outputRecordCollector,
                                        OnStartFunction onStart,
                                        OnCloseFunction onClose,
                                        ConfiguredAirbyteCatalog catalog,
                                        String defaultNamespace,
                                        Supplier<ConcurrentMap<AirbyteStreamNameNamespacePair, BigQueryDirectUploader>> uploaderMap) {
    super(outputRecordCollector,
        onStart,
        onClose,
        new BigQueryAsyncStandardFlush(uploaderMap),
        catalog,
        new BufferManager((long) (Runtime.getRuntime().maxMemory() * 0.5)),
        Optional.ofNullable(defaultNamespace),
        new FlushFailure(),
        Executors.newFixedThreadPool(2));
  }

}
