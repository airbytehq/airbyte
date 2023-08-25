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

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentMap;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@Slf4j
public class BigQueryAsyncStandardFlush  implements DestinationFlushFunction {

    private final BigQuery bigQuery;
    private final ConcurrentMap<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap;

    public BigQueryAsyncStandardFlush(BigQuery bigQuery, ConcurrentMap<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap) {
        this.bigQuery = bigQuery;
        this.uploaderMap = uploaderMap;
    }

    @Override
    public void flush(final StreamDescriptor decs, final Stream<PartialAirbyteMessage> stream) throws Exception {
        Map<AirbyteStreamNameNamespacePair, List<String>> messageByStreamDescriptor = stream.collect(Collectors.toMap(
                partialAirbyteMessage -> new AirbyteStreamNameNamespacePair(partialAirbyteMessage.getRecord().getStream(),
                        partialAirbyteMessage.getRecord().getNamespace()),
                partialAirbyteMessage -> List.of(partialAirbyteMessage.getSerialized()),
                (left, right) -> {
                    left.addAll(right);
                    return left;
                }
        ));

        messageByStreamDescriptor.forEach((key, value) -> {

            uploaderMap.get(key).uploadAll(key, value);
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
