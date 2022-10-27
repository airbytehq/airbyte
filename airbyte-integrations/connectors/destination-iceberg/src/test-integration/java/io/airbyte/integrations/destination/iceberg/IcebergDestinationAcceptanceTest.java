/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class IcebergDestinationAcceptanceTest extends DestinationAcceptanceTest {

    private static final Logger LOGGER = LoggerFactory.getLogger(IcebergDestinationAcceptanceTest.class);


    private final String secretFilePath = "secrets/iceberg.json";

    private final List<AirbyteMessage> messageList = new ArrayList<>();
    private ConfiguredAirbyteCatalog catalog;

    @Override
    protected String getImageName() {
        return "airbyte/destination-iceberg:dev";
    }

    @Override
    protected JsonNode getConfig() throws IOException {
        return Jsons.deserialize(IOs.readFile(Path.of(secretFilePath)));
    }

    @Override
    protected JsonNode getFailCheckConfig() {
        final JsonNode failCheckJson = Jsons.jsonNode(Collections.emptyMap());
        // invalid credential
        ((ObjectNode) failCheckJson).put("access_key_id", "fake-key");
        ((ObjectNode) failCheckJson).put("secret_access_key", "fake-secret");
        return failCheckJson;
    }

    @Override
    protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
        String streamName,
        String namespace,
        JsonNode streamSchema)
        throws IOException {
        // TODO Implement this method to retrieve records which written to the destination by the connector.
        // Records returned from this method will be compared against records provided to the connector
        // to verify they were written correctly
        return null;
    }

    @Override
    protected void setup(TestDestinationEnv testEnv) throws IOException {
        //messages
        final Instant now = Instant.now();
        final String usersStreamName = "users";
        final String tasksStreamName = "tasks";
        final AirbyteMessage messageUsers1 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(usersStreamName)
                .withData(Jsons.jsonNode(ImmutableMap.builder().put("name", "john").put("id", "10").build()))
                .withEmittedAt(now.toEpochMilli()));
        final AirbyteMessage messageUsers2 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(usersStreamName)
                .withData(Jsons.jsonNode(ImmutableMap.builder().put("name", "susan").put("id", "30").build()))
                .withEmittedAt(now.toEpochMilli()));
        final AirbyteMessage messageTasks1 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(tasksStreamName)
                .withData(Jsons.jsonNode(ImmutableMap.builder().put("goal", "announce the game.").build()))
                .withEmittedAt(now.toEpochMilli()));
        final AirbyteMessage messageTasks2 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage().withStream(tasksStreamName)
                .withData(Jsons.jsonNode(ImmutableMap.builder().put("goal", "ship some code.").build()))
                .withEmittedAt(now.toEpochMilli()));
        final AirbyteMessage messageState = new AirbyteMessage().withType(AirbyteMessage.Type.STATE)
            .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.builder()
                .put("checkpoint", "now!")
                .build())));
        this.messageList.add(messageUsers1);
        this.messageList.add(messageTasks1);
        this.messageList.add(messageUsers2);
        this.messageList.add(messageTasks2);
        this.messageList.add(messageState);

        //catalog
        this.catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
            CatalogHelpers.createConfiguredAirbyteStream(usersStreamName, null, Field.of("name", JsonSchemaType.STRING),
                Field.of("id", JsonSchemaType.STRING)),
            CatalogHelpers.createConfiguredAirbyteStream(tasksStreamName,
                null,
                Field.of("goal", JsonSchemaType.STRING))));

    }

    @Override
    protected void tearDown(TestDestinationEnv testEnv) {
    }


    @Test
    void testWriteSuccess() throws Exception {
        final AirbyteMessageConsumer consumer = new IcebergDestination()
            .getConsumer(getConfig(), catalog, Destination::defaultOutputRecordCollector);
        messageList.forEach(m -> {
            try {
                consumer.accept(m);
            } catch (Exception e) {
                LOGGER.error(e.getMessage(), e);
            }
        });
        consumer.close();
    }

}
