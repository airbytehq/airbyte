package io.airbyte.integrations.destination.staging;

import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.jdbc.WriteConfig;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.s3.csv.CsvSerializedBuffer;
import io.airbyte.integrations.destination.s3.csv.StagingDatabaseCsvSheetGenerator;
import io.airbyte.integrations.destination_async.StreamDestinationFlusher;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Stream;

import static io.airbyte.integrations.destination.staging.StagingConsumerFactory.copyIntoTableFromStage;

@Slf4j
public class StagingAsyncFlusher implements StreamDestinationFlusher {

    private static final UUID RANDOM_CONNECTION_ID = UUID.randomUUID();
    private final Map<StreamDescriptor, WriteConfig> streamDescToWriteConfig;
    private final StagingOperations stagingOperations;
    private final JdbcDatabase database;
    private final ConfiguredAirbyteCatalog catalog;

    public StagingAsyncFlusher(final Map<StreamDescriptor, WriteConfig> streamDescToWriteConfig,
                               final StagingOperations stagingOperations,
                               final JdbcDatabase database,
                               final ConfiguredAirbyteCatalog catalog) {
        this.streamDescToWriteConfig = streamDescToWriteConfig;
        this.stagingOperations = stagingOperations;
        this.database = database;
        this.catalog = catalog;
    }

    // todo(davin): exceptions are too broad.
    @Override
    public void flush(final StreamDescriptor decs, final Stream<AirbyteMessage> stream) throws Exception {
        var start = System.currentTimeMillis();
        final CsvSerializedBuffer writer = getCsvSerializedBuffer(stream);
        writer.flush();
        log.info("CSV Conversion took {} secs", (System.currentTimeMillis() - start)/1000);
        log.info("Flushing buffer for stream {} ({}) to staging", decs.getName(), FileUtils.byteCountToDisplaySize(writer.getByteCount()));

        if (!streamDescToWriteConfig.containsKey(decs)) {
            throw new IllegalArgumentException(
                    String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s", Jsons.serialize(catalog)));
        }

        final WriteConfig writeConfig = streamDescToWriteConfig.get(decs);
        final String schemaName = writeConfig.getOutputSchemaName();
        final String stageName = stagingOperations.getStageName(schemaName, writeConfig.getStreamName());
        final String stagingPath =
                stagingOperations.getStagingPath(RANDOM_CONNECTION_ID, schemaName, writeConfig.getStreamName(), writeConfig.getWriteDatetime());
        try {
            log.info("Starting upload to stage..");
            start = System.currentTimeMillis();
            final String stagedFile = stagingOperations.uploadRecordsToStage(database, writer, schemaName, stageName, stagingPath);
            log.info("Upload to stage took {} secs", (System.currentTimeMillis() - start)/1000);

            start = System.currentTimeMillis();
            copyIntoTableFromStage(database, stageName, stagingPath, List.of(stagedFile), writeConfig.getOutputTableName(), schemaName,
                    stagingOperations);
            log.info("Copy into table took {} secs", (System.currentTimeMillis() - start)/1000);
        } catch (final Exception e) {
            log.error("Failed to flush and commit buffer data into destination's raw table", e);
            throw new RuntimeException("Failed to upload buffer to stage and commit to destination", e);
        }

        writer.close();
    }

    private static CsvSerializedBuffer getCsvSerializedBuffer(Stream<AirbyteMessage> stream) {
        CsvSerializedBuffer writer = null;
        try {
            writer = new CsvSerializedBuffer(
                    new FileBuffer(CsvSerializedBuffer.CSV_GZ_SUFFIX),
                    new StagingDatabaseCsvSheetGenerator(),
                    true);

            CsvSerializedBuffer finalWriter = writer;
            stream.forEach(record -> {
                try {
                    // todo(davin): handle non-record airbyte messages.
                    finalWriter.accept(record.getRecord());
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
            });
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
        return writer;
    }

    @Override
    public long getOptimalBatchSizeBytes() {
        return 200 * 1024 * 1024;
    }
}
