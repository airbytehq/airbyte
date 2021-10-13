package io.airbyte.integrations.destination.elasticsearch;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

import java.util.Map;
import java.util.UUID;

public class ElasticsearchAirbyteMessageConsumer extends FailureTrackingAirbyteMessageConsumer {

    private final ElasticsearchConnection connection;
    private final ConfiguredAirbyteCatalog catalog;
    private final Map<String, String> writeConfigs;

    public ElasticsearchAirbyteMessageConsumer(ElasticsearchConnection connection,
                                               ConfiguredAirbyteCatalog catalog,
                                               Map<String, String> writeConfigs) {
        this.connection = connection;
        this.catalog = catalog;
        this.writeConfigs = writeConfigs;
    }

    @Override
    protected void startTracked() throws Exception {

    }

    @Override
    protected void acceptTracked(AirbyteMessage message) throws Exception {
        if (message.getType() != AirbyteMessage.Type.RECORD) {
            return;
        }
        final AirbyteRecordMessage recordMessage = message.getRecord();

        // ignore other message types.
        if (!writeConfigs.containsKey(recordMessage.getStream())) {
            throw new IllegalArgumentException(
                    String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                            Jsons.serialize(catalog), Jsons.serialize(recordMessage)));
        }

        var index = writeConfigs.get(recordMessage.getStream());

        connection.writeRecord(
                index,
                UUID.randomUUID().toString(),
                recordMessage.getData());
    }

    @Override
    protected void close(boolean hasFailed) throws Exception {
        connection.close();
    }

}
