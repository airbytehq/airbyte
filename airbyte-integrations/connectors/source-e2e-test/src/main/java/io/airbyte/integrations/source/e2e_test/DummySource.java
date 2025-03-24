package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.BaseConnector;
import io.airbyte.cdk.integrations.base.*;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.v0.*;

import java.util.List;


public class DummySource extends BaseConnector implements Source {

    public static void main(final String[] args) throws Exception {
        final CliParse integrationCliParser = new CliParse();
        final IntegrationConfig parse = integrationCliParser.parse(args);

        final DummySource source = new DummySource();

        switch (parse.getCommand()) {
            case SPEC, DISCOVER, CHECK -> {
                new IntegrationRunner(source).run(args);
            }
            case READ -> {
                JavaSocketWriter writer = new JavaSocketWriter();
                writer.startJavaUnixSocketWriter();
            }

            case WRITE -> {
            }
        }
    }

    private static final String FIVE_STRING_COLUMNS_SCHEMA = """
                {
                      "type": "object",
                      "properties": {
                        "field1": {
                          "type": "string"
                        },
                        "field2": {
                          "type": "string"
                        },
                        "field3": {
                          "type": "string"
                        },
                        "field4": {
                          "type": "string"
                        },
                        "field5": {
                          "type": "string"
                        }
                      }
                    }
            """;

    private static final AirbyteCatalog FIVE_STRING_COLUMNS_CATALOG = new AirbyteCatalog().withStreams(List.of(
            new AirbyteStream().withName("stream1").withJsonSchema(Jsons.deserialize(FIVE_STRING_COLUMNS_SCHEMA))
                    .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH))));


    @Override
    public AirbyteCatalog discover(JsonNode jsonNode) {
        return FIVE_STRING_COLUMNS_CATALOG;
    }

    @Override
    public AutoCloseableIterator<AirbyteMessage> read(JsonNode jsonNode, ConfiguredAirbyteCatalog configuredAirbyteCatalog, JsonNode jsonNode1) {
        return new DummyIterator();
    }

    public AutoCloseableIterator<AirbyteMessage> read() {
        return new DummyIterator();
    }

    @Override
    public AirbyteConnectionStatus check(JsonNode jsonNode) {
        return new AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    }
}
