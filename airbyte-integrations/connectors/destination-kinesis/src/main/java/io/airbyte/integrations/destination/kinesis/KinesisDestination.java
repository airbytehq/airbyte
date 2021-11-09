/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class KinesisDestination extends BaseConnector implements Destination {

    private static final Logger LOGGER = LoggerFactory.getLogger(KinesisDestination.class);

    public static void main(String[] args) throws Exception {
        new IntegrationRunner(new KinesisDestination()).run(args);
    }

    @Override
    public AirbyteConnectionStatus check(JsonNode config) {
        KinesisStream kinesisStream = null;
        var streamName = "test_stream";
        try {
            var kinesisConfig = new KinesisConfig(config);
            kinesisStream = new KinesisStream(kinesisConfig);
            kinesisStream.createStream(streamName);
            var partitionKey = KinesisUtils.buildPartitionKey();
            kinesisStream.putRecord(streamName, partitionKey, "{}");
            return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
        } catch (Exception e) {
            LOGGER.error("Error while trying to connect to Kinesis: ", e);
            return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.FAILED);
        } finally {
            if (kinesisStream != null) {
                try {
                    kinesisStream.flush();
                    kinesisStream.deleteStream(streamName);
                } catch (Exception e) {
                    LOGGER.error("Error while deleting kinesis stream: ", e);
                }
                kinesisStream.close();
            }
        }
    }

    @Override
    public AirbyteMessageConsumer getConsumer(JsonNode config,
                                              ConfiguredAirbyteCatalog configuredCatalog,
                                              Consumer<AirbyteMessage> outputRecordCollector) {
        return new KinesisMessageConsumer(new KinesisConfig(config), configuredCatalog, outputRecordCollector);
    }

}
