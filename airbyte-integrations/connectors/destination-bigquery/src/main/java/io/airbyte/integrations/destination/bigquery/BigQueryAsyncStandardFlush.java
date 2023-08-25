package io.airbyte.integrations.destination.bigquery;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.InsertAllRequest;
import com.google.cloud.bigquery.TableId;
import io.airbyte.integrations.destination.bigquery.uploader.AbstractBigQueryUploader;
import io.airbyte.integrations.destination_async.DestinationFlushFunction;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import lombok.extern.slf4j.Slf4j;

import java.util.Map;
import java.util.stream.Stream;

@Slf4j
public class BigQueryAsyncStandardFlush  implements DestinationFlushFunction {

    private final BigQuery bigQuery;
    private final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap;

    public BigQueryAsyncStandardFlush(BigQuery bigQuery, Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap) {
        this.bigQuery = bigQuery;
        this.uploaderMap = uploaderMap;
    }

    @Override
    public void flush(final StreamDescriptor decs, final Stream<PartialAirbyteMessage> stream) throws Exception {
        stream.forEach(aibyteMessage -> {
            try {
                uploaderMap.get(
                        new AirbyteStreamNameNamespacePair(aibyteMessage.getRecord().getStream(),
                                aibyteMessage.getRecord().getNamespace())).upload(aibyteMessage);
            } catch (Exception e) {
                log.error("BQ async standard flush");
                log.error(aibyteMessage.toString());
                throw e;
            }
        });
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
