package io.airbyte.integrations.destination.parquet;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.CommitOnStateAirbyteMessageConsumer;
import io.airbyte.integrations.destination.s3.avro.AvroRecordFactory;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import org.apache.commons.io.FileUtils;
import org.apache.hadoop.fs.FileUtil;
import org.apache.parquet.hadoop.ParquetWriter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;

public class ParquetConsumer extends CommitOnStateAirbyteMessageConsumer {
    private static final Logger LOGGER = LoggerFactory.getLogger(ParquetDestination.class);
    private final Map<String, ParquetDestination.WriteConfig> writeConfigs;
    private final ConfiguredAirbyteCatalog catalog;

    public ParquetConsumer(final Map<String, ParquetDestination.WriteConfig> writeConfigs,
                           final ConfiguredAirbyteCatalog catalog,
                           final Consumer<AirbyteMessage> outputRecordCollector) {

        super(outputRecordCollector);
        this.catalog = catalog;
        LOGGER.info("initializing consumer.");

        this.writeConfigs = writeConfigs;
    }

    @Override
    protected void startTracked() {
        // todo (cgardens) - move contents of #write into this method.
    }

    @Override
    protected void acceptTracked(final AirbyteMessage message) throws Exception {
        if (message.getType() != AirbyteMessage.Type.RECORD) {
            return;
        }
        final AirbyteRecordMessage recordMessage = message.getRecord();
        LOGGER.info(recordMessage.toString());

        // ignore other message types.
        if (!writeConfigs.containsKey(recordMessage.getStream())) {
            throw new IllegalArgumentException(
                    String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                            Jsons.serialize(catalog), Jsons.serialize(recordMessage)));
        }

        LOGGER.info(recordMessage.getStream());
        LOGGER.info(recordMessage.getData().toString());

        final ParquetWriter writer = writeConfigs.get(recordMessage.getStream()).writer();
        final AvroRecordFactory avroRecordFactory = writeConfigs.get(recordMessage.getStream()).avroRecordFactory();
        final UUID id = UUID.randomUUID();
        writer.write(avroRecordFactory.getAvroRecord(id, recordMessage));

    }



    @Override
    public void commit() throws Exception {
        for (final ParquetDestination.WriteConfig writeConfig : writeConfigs.values()) {
            writeConfig.writer().close();
        }
    }

    @Override
    protected void close(boolean hasFailed) throws IOException {
        LOGGER.info("finalizing consumer.");

        for (final Map.Entry<String, ParquetDestination.WriteConfig> entries : writeConfigs.entrySet()) {
            try {
                entries.getValue().writer().close();
            } catch (final Exception e) {
                hasFailed = true;
                LOGGER.error("failed to close writer for: {}.", entries.getKey());
            }
        }
        // do not persist the data, if there are any failures.
        try {
            if (!hasFailed) {
                for (final ParquetDestination.WriteConfig writeConfig : writeConfigs.values()) {

                    FileUtils.copyFile(writeConfig.tmpPathFile(), writeConfig.finalPathFile());
                    LOGGER.info(String.format("File output: %s", writeConfig.finalPathFile()));
                }
            } else {
                final String message = "Failed to output files in destination";
                LOGGER.error(message);
                throw new IOException(message);
            }
        } finally {
            // clean up tmp files.
            for (final ParquetDestination.WriteConfig writeConfig : writeConfigs.values()) {
                FileUtil.fullyDelete(writeConfig.tmpPathFile());
            }
        }
    }

}
