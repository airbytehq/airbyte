package io.airbyte.integrations.destination.azure_blob_storage.file.uploader;

import io.airbyte.integrations.destination.azure_blob_storage.file.formatter.AzureRecordFormatter;
import io.airbyte.integrations.destination.s3.writer.S3Writer;
import io.airbyte.protocol.models.AirbyteMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.UUID;
import java.util.function.Consumer;

import static io.airbyte.integrations.destination.azure_blob_storage.file.helpers.LoggerHelper.printHeapMemoryConsumption;

public abstract class AbstractAzureUploader<T extends S3Writer> {

    private static final Logger LOGGER = LoggerFactory.getLogger(AbstractAzureUploader.class);

    protected final T writer;
    protected final AzureRecordFormatter recordFormatter;

    public AbstractAzureUploader(T writer,
                                 AzureRecordFormatter recordFormatter) {
        this.writer = writer;
        this.recordFormatter = recordFormatter;
    }

    protected void postProcessAction(boolean hasFailed) throws Exception {
        // Do nothing by default
    }

    public void upload(AirbyteMessage airbyteMessage) {
        try {
            writer.write(UUID.randomUUID(), airbyteMessage.getRecord());
        } catch (final IOException | RuntimeException e) {
            LOGGER.error("Got an error while writing message: {}", e.getMessage(), e);
            LOGGER.error(String.format(
                    "Failed to process a message for job: \n%s, \nAirbyteMessage: %s",
                    writer.toString(),
                    airbyteMessage.getRecord()));
            printHeapMemoryConsumption();
            throw new RuntimeException(e);
        }
    }

    public void close(boolean hasFailed, Consumer<AirbyteMessage> outputRecordCollector, AirbyteMessage lastStateMessage) {
        try {
            LOGGER.info("Field fails during format : ");
            recordFormatter.printAndCleanFieldFails();

            LOGGER.info("Closing connector:" + this);
            this.writer.close(hasFailed);

            if (!hasFailed) {
                uploadData(outputRecordCollector, lastStateMessage);
            }
            this.postProcessAction(hasFailed);
            LOGGER.info("Closed connector:" + this);
        } catch (final Exception e) {
            LOGGER.error(String.format("Failed to close %s writer, \n details: %s", this, e.getMessage()));
            printHeapMemoryConsumption();
            throw new RuntimeException(e);
        }
    }

    protected void uploadData(Consumer<AirbyteMessage> outputRecordCollector, AirbyteMessage lastStateMessage) throws Exception {
        try {
            outputRecordCollector.accept(lastStateMessage);
            LOGGER.info("Final state message is accepted.");
        } catch (Exception e) {
            LOGGER.error("Upload data is failed!");
            throw e;
        }
    }
}
