package io.airbyte.integrations.destination.doris;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.CommitOnStateAirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import org.apache.commons.csv.CSVPrinter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Iterator;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;

public class DorisConsumer extends CommitOnStateAirbyteMessageConsumer {
    private static final Logger LOGGER = LoggerFactory.getLogger(DorisConsumer.class);

//    private static List<Long> txnList = new ArrayList<>();

    private final ConfiguredAirbyteCatalog catalog;
    private final Map<String, DorisWriteConfig> writeConfigs;


    public DorisConsumer(
            final Map<String,DorisWriteConfig> writeConfigs,
            final ConfiguredAirbyteCatalog catalog,
            final Consumer<AirbyteMessage> outputRecordCollector) {
        super(outputRecordCollector);
        this.catalog = catalog;
        this.writeConfigs = writeConfigs;
        LOGGER.info("initializing DorisConsumer.");
    }

    @Override
    public void commit() throws Exception {
        for (final DorisWriteConfig writeConfig : writeConfigs.values()) {
            writeConfig.getWriter().flush();
        }
    }

    @Override
    protected void startTracked() throws Exception {
    }

    @Override
    protected void acceptTracked(AirbyteMessage msg) throws Exception {
        if (msg.getType() != AirbyteMessage.Type.RECORD) {
            return;
        }

        final AirbyteRecordMessage recordMessage = msg.getRecord();
        if (!writeConfigs.containsKey(recordMessage.getStream())) {
            throw new IllegalArgumentException(
                    String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                            Jsons.serialize(catalog), Jsons.serialize(recordMessage)));
        }

        JsonNode data = recordMessage.getData();
        StringBuilder stringBuilder = new StringBuilder();
        for (String s : writeConfigs.get(recordMessage.getStream()).getFormat().getHeader()) {
            if (!stringBuilder.isEmpty()) stringBuilder.append(DorisStreamLoad.CSV_COLUMN_SEPARATOR);
            stringBuilder.append(data.get(s).asText());
        }

        writeConfigs.get(recordMessage.getStream()).getWriter().printRecord(
                stringBuilder.toString()
        );

    }

    @Override
    protected void close(boolean hasFailed) throws Exception {
        LOGGER.info("finalizing DorisConsumer");
        for (final Map.Entry<String, DorisWriteConfig> entries : writeConfigs.entrySet()) {
            try {
                entries.getValue().getWriter().flush();
                entries.getValue().getWriter().close();
            } catch (final Exception e) {
                hasFailed = true;
                LOGGER.error("failed to close writer for: {}", entries.getKey());
            }
        }

        // firstCommit
        try{
            for (final DorisWriteConfig value : writeConfigs.values()) {
                value.getDorisStreamLoad().firstCommit();
            }
        }catch (final Exception e) {
            hasFailed = true;
            final String message = "Failed to pre-commit doris in destination: ";
            LOGGER.error(message+e.getMessage());
            for (final DorisWriteConfig value : writeConfigs.values()) {
                if(value.getDorisStreamLoad().getTxnID() > 0) value.getDorisStreamLoad().abortTransaction();
            }
        }

        //
        try {
            if (!hasFailed) {
                for (final DorisWriteConfig writeConfig : writeConfigs.values()) {
                    if(writeConfig.getDorisStreamLoad().getTxnID()>0) writeConfig.getDorisStreamLoad().commitTransaction();
                    LOGGER.info(String.format("stream load commit (TxnID:  %s ) successed ", writeConfig.getDorisStreamLoad().getTxnID()));
                }
            } else {
                final String message = "Failed to commit doris in destination";
                LOGGER.error(message);
                for (final DorisWriteConfig writeConfig : writeConfigs.values()) {
                    if(writeConfig.getDorisStreamLoad().getTxnID()>0) writeConfig.getDorisStreamLoad().abortTransaction();
                }
                throw new IOException(message);
            }
        } finally {
            for (final DorisWriteConfig writeConfig : writeConfigs.values()) {
                writeConfig.getDorisStreamLoad().close();
                Files.deleteIfExists(writeConfig.getTmpPath());
            }
        }





    }
}
