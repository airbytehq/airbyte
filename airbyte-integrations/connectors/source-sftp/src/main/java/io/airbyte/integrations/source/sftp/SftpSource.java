/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sftp;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.*;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class SftpSource extends BaseConnector implements Source {

    private static final Logger LOGGER = LoggerFactory.getLogger(SftpSource.class);

    public static void main(String[] args) throws Exception {
        new IntegrationRunner(new SftpSource()).run(args);
    }

    @Override
    public AirbyteConnectionStatus check(JsonNode config) throws Exception {
        final SftpClient client = new SftpClient(config);
        try {
            final SftpCommand command = new SftpCommand(client, config);
            client.connect();
            String workingDirectory = config.has("folder_path") ? config.get("folder_path").asText() : "";
            if (StringUtils.isNotBlank(workingDirectory)) {
                command.tryChangeWorkingDirectory(workingDirectory);
            }
            client.disconnect();
            return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
        } catch (Exception e) {
            LOGGER.error("Exception attempting to connect to the server: ", e);
            return new AirbyteConnectionStatus()
                    .withStatus(AirbyteConnectionStatus.Status.FAILED)
                    .withMessage("Could not connect to the server with provided configuration. \n" + e.getMessage());
        } finally {
            client.disconnect();
        }
    }


    @Override
    public AirbyteCatalog discover(JsonNode config) throws Exception {
        final SftpClient client = new SftpClient(config);
        try {
            final SftpCommand command = new SftpCommand(client, config);
            client.connect();
            String workingDirectory = config.has("folder_path") ? config.get("folder_path").asText() : "";
            if (StringUtils.isNotBlank(workingDirectory)) {
                command.tryChangeWorkingDirectory(workingDirectory);
            }
            Map<String, JsonNode> fileSchemas = command.getFilesSchemas();
            List<AirbyteStream> streams = fileSchemas.keySet()
                    .stream()
                    .map(fileName -> new AirbyteStream()
                            .withName(fileName)
                            .withJsonSchema(fileSchemas.get(fileName))
                            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH)))
                    .toList();
            return new AirbyteCatalog().withStreams(streams);
        } catch (Exception e) {
            LOGGER.error("Exception attempting to discover the server: ", e);
            throw new RuntimeException(e);
        } finally {
            client.disconnect();
        }
    }

    @Override
    public AutoCloseableIterator<AirbyteMessage> read(JsonNode config, ConfiguredAirbyteCatalog catalog, JsonNode state) throws Exception {
        final SftpClient client = new SftpClient(config);
        final SftpCommand command = new SftpCommand(client, config);
        client.connect();
        String workingDirectory = config.has("folder_path") ? config.get("folder_path").asText() : "";
        if (StringUtils.isNotBlank(workingDirectory)) {
            command.tryChangeWorkingDirectory(workingDirectory);
        }

        final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = new ArrayList<>();

        catalog.getStreams()
                .stream()
                .map(ConfiguredAirbyteStream::getStream)
                .forEach(stream -> {
                    AutoCloseableIterator<JsonNode> fileData = getFileDataIterator(command, stream);
                    AutoCloseableIterator<AirbyteMessage> messageIterator = getMessageIterator(fileData, stream.getName());
                    iteratorList.add(messageIterator);
                });
        return AutoCloseableIterators
                .appendOnClose(AutoCloseableIterators.concatWithEagerClose(iteratorList), () -> {
                    LOGGER.info("Closing server connection.");
                    client.disconnect();
                    LOGGER.info("Closed server connection.");
                });
    }

    private AutoCloseableIterator<AirbyteMessage> getMessageIterator(final AutoCloseableIterator<JsonNode> recordIterator,
                                                                     final String streamName) {
        return AutoCloseableIterators.transform(recordIterator, r -> new AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(new AirbyteRecordMessage()
                        .withStream(streamName)
                        .withEmittedAt(Instant.now().toEpochMilli())
                        .withData(r)));
    }

    private AutoCloseableIterator<JsonNode> getFileDataIterator(final SftpCommand command,
                                                                final AirbyteStream stream) {
        return AutoCloseableIterators.lazyIterator(() -> {
            try {
                List<JsonNode> fileData = command.getFileData(stream.getName());
                return AutoCloseableIterators.fromIterator(fileData.iterator());
            } catch (final Exception e) {
                throw new RuntimeException(e);
            }
        });
    }
}
