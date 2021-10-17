package io.airbyte.integrations.destination.elasticsearch;

import co.elastic.clients.elasticsearch._core.BulkResponse;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer;
import io.airbyte.integrations.destination.buffered_stream_consumer.RecordWriter;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Consumer;

public class ElasticsearchAirbyteMessageConsumerFactory {

    private static final Logger log = LoggerFactory.getLogger(ElasticsearchAirbyteMessageConsumerFactory.class);
    private static final StandardNameTransformer namingResolver = new StandardNameTransformer();
    private static final int MAX_BATCH_SIZE = 10000;

    private static AtomicLong recordsWritten = new AtomicLong(0);

    public static AirbyteMessageConsumer create(Consumer<AirbyteMessage> outputRecordCollector,
                                                ElasticsearchConnection connection,
                                                Map<String, ElasticsearchWriteConfig> writeConfigs,
                                                ConfiguredAirbyteCatalog catalog) {

        return new BufferedStreamConsumer(
                outputRecordCollector,
                onStartFunction(connection, writeConfigs),
                recordWriterFunction(connection, writeConfigs),
                onCloseFunction(connection),
                catalog,
                isValidFunction(connection),
                MAX_BATCH_SIZE);
    }

    // is there any json node that wont fit in the index?
    private static CheckedFunction<JsonNode, Boolean, Exception> isValidFunction(ElasticsearchConnection connection) {
        return jsonNode -> {
            return true;
        };
    }

    private static CheckedConsumer<Boolean, Exception> onCloseFunction(ElasticsearchConnection connection) {
        return aBoolean -> connection.close();
    }

    private static RecordWriter recordWriterFunction(
            ElasticsearchConnection connection, Map<String, ElasticsearchWriteConfig> writeConfigs) {
        return (pair, records) -> {
            log.info("writing {} records in bulk operation", records.size());
            var config = writeConfigs.get(pair.getName());
            BulkResponse response = null;
            switch (config.getSyncMode()){
                case APPEND -> {
                    response = connection.createDocuments(streamToIndexName(pair.getNamespace(), pair.getName()), records, config);
                }
                case APPEND_DEDUP, OVERWRITE -> {
                    response = connection.updateDocuments(streamToIndexName(pair.getNamespace(), pair.getName()), records, config);
                }
            }
            if (response.errors()){
                log.error("failed to write bulk records");
            } else {
                log.info("bulk write took: {}ms", response.took());
            }
        };
    }

    private static VoidCallable onStartFunction(ElasticsearchConnection connection, Map<String, ElasticsearchWriteConfig> writeConfigs) {
        return () -> {
            for (var config :
                    writeConfigs.entrySet()) {
                connection.createIndexIfMissing(streamToIndexName(config.getValue().getNamespace(), config.getKey()));
            }
        };
    }

    protected static String streamToIndexName(String namespace, String streamName) {
        String prefix = "";
        if (Objects.nonNull(namespace) && !namespace.isEmpty()) {
            prefix = String.format("%s_", namespace);
        }
        return String.format("%s%s", prefix, namingResolver.getIdentifier(streamName));
    }
}
