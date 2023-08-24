package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.BigQuery;
import io.airbyte.integrations.destination.bigquery.uploader.AbstractBigQueryUploader;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.integrations.destination_async.AsyncStreamConsumer;
import io.airbyte.integrations.destination_async.OnCloseFunction;
import io.airbyte.integrations.destination_async.buffers.BufferManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import lombok.extern.slf4j.Slf4j;

import java.util.Map;
import java.util.function.Consumer;

@Slf4j
public class BigQueryRecordStandardConsumer extends AsyncStreamConsumer {
    public BigQueryRecordStandardConsumer(Consumer<AirbyteMessage> outputRecordCollector,
                                          OnStartFunction onStart,
                                          OnCloseFunction onClose,
                                          BigQuery bigQuery,
                                          ConfiguredAirbyteCatalog catalog,
                                          String defaultNamespace,
                                          Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap) {
        super(outputRecordCollector,
                onStart,
                onClose,
                new BigQueryAsyncStandardFlush(bigQuery, uploaderMap),
                catalog,
                new BufferManager(),
                defaultNamespace);
        log.info("____________________ Creating the new record consumer ____________________");
    }
}
