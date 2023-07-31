package io.airbyte.integrations.source.mongodb.v3;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;

public class MongoDbSource implements Source, AutoCloseable {

    @Override
    public AirbyteConnectionStatus check(JsonNode config) throws Exception {
        return null;
    }

    @Override
    public AirbyteCatalog discover(JsonNode config) throws Exception {
        return null;
    }

    @Override
    public AutoCloseableIterator<AirbyteMessage> read(JsonNode config, ConfiguredAirbyteCatalog catalog, JsonNode state) throws Exception {
        return null;
    }

    @Override
    public ConnectorSpecification spec() throws Exception {
        return null;
    }

    @Override
    public void close() throws Exception {

    }
}
