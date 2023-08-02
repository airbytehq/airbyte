package io.airbyte.integrations.destination.staging;

import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.WriteConfig;
import io.airbyte.integrations.destination_async.DestinationFlushFunction;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import lombok.extern.slf4j.Slf4j;

import java.util.Map;
import java.util.stream.Stream;

@Slf4j
public class NonStagingAsyncFlush implements DestinationFlushFunction {

    private final Map<StreamDescriptor, WriteConfig> streamDescToWriteConfig;
    private final SqlOperations sqlOperations;
    private final JdbcDatabase database;
    private final ConfiguredAirbyteCatalog catalog;
    private final long optimalBatchSizeBytes;

    public NonStagingAsyncFlush(Map<StreamDescriptor, WriteConfig> streamDescToWriteConfig,
                                SqlOperations sqlOperations,
                                JdbcDatabase database,
                                ConfiguredAirbyteCatalog catalog,
                                long optimalBatchSizeBytes) {
        this.streamDescToWriteConfig = streamDescToWriteConfig;
        this.sqlOperations = sqlOperations;
        this.database = database;
        this.catalog = catalog;
        this.optimalBatchSizeBytes = optimalBatchSizeBytes;
    }

    @Override
    public void flush(final StreamDescriptor decs, final Stream<PartialAirbyteMessage> stream) throws Exception {
        if (!streamDescToWriteConfig.containsKey(decs)) {
            throw new IllegalArgumentException(
                    String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s", Jsons.serialize(catalog)));
        }

        final WriteConfig writeConfig = streamDescToWriteConfig.get(decs);
        final String schemaName = writeConfig.getOutputSchemaName();

        try {
            sqlOperations.insertRecords(
                    database,
                    stream.map(s -> new AirbyteRecordMessage().withStream(s.getRecord().getStream())
                            .withNamespace(s.getRecord().getNamespace())
                            .withData(s.getRecord().getData())
                            .withEmittedAt(s.getRecord().getEmittedAt())
                    ).toList(),
                    schemaName,
                    writeConfig.getOutputTableName()
            );
        } catch (final Exception e) {
            log.error("Failed to flush and commit buffer data into destination's raw table", e);
            throw new RuntimeException("Failed to upload buffer to stage and commit to destination", e);
        }
    }

    @Override
    public long getOptimalBatchSizeBytes() {
        return optimalBatchSizeBytes;
    }
}
