package io.airbyte.integrations.destination.iceberg;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.CommitOnStateAirbyteMessageConsumer;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.iceberg.config.WriteConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import org.apache.spark.sql.SparkSession;

/**
 * @author Leibniz on 2022/10/26.
 */
public class IcebergConsumer extends CommitOnStateAirbyteMessageConsumer {

    private final StandardNameTransformer namingResolver = new StandardNameTransformer();

    private final SparkSession spark;
    private final ConfiguredAirbyteCatalog catalog;
    private Map<String, WriteConfig> configs;

    public IcebergConsumer(SparkSession spark,
        Consumer<AirbyteMessage> outputRecordCollector,
        ConfiguredAirbyteCatalog catalog) {
        super(outputRecordCollector);
        this.spark = spark;
        this.catalog = catalog;
    }

    /**
     * call this method to initialize any resources that need to be created BEFORE the consumer consumes any messages
     */
    @Override
    protected void startTracked() throws Exception {
        Map<String, WriteConfig> configs = new HashMap<>();
        for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
            final String streamName = stream.getStream().getName();
            final String tableName = namingResolver.getRawTableName(streamName);
            final String tmpTableName = namingResolver.getTmpTableName(streamName);
            final DestinationSyncMode syncMode = stream.getDestinationSyncMode();
            if (syncMode == null) {
                throw new IllegalStateException("Undefined destination sync mode");
            }
            final boolean isAppendMode = syncMode != DestinationSyncMode.OVERWRITE;
            configs.put(streamName, new WriteConfig(tableName, tmpTableName, isAppendMode));
        }
        this.configs = configs;
    }

    /**
     * call this method when receive a non-STATE AirbyteMessage Ref to <a
     * href="https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#airbytemessage">AirbyteMessage</a>
     */
    @Override
    protected void acceptTracked(AirbyteMessage msg) throws Exception {
        if (msg.getType() != Type.RECORD) {
            return;
        }
        final AirbyteRecordMessage recordMessage = msg.getRecord();

        // ignore other message types.
        if (!configs.containsKey(recordMessage.getStream())) {
            throw new IllegalArgumentException(
                String.format(
                    "Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                    Jsons.serialize(catalog),
                    Jsons.serialize(recordMessage)));
        }

        //TODO write data
    }

    /**
     * call this method when receive a STATE AirbyteMessage
     */
    @Override
    public void commit() throws Exception {

    }

    @Override
    protected void close(boolean hasFailed) throws Exception {

    }
}
