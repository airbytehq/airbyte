/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg;

import static io.airbyte.integrations.destination.iceberg.IcebergIntegrationTestUtil.ICEBERG_IMAGE_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class IcebergDestinationAcceptanceTest extends DestinationAcceptanceTest {

    private static final Logger LOGGER = LoggerFactory.getLogger(IcebergDestinationAcceptanceTest.class);

    private static final String SECRET_FILE_PATH = "secrets/config.json";

    @Override
    protected String getImageName() {
        return ICEBERG_IMAGE_NAME;
    }

    @Override
    protected JsonNode getConfig() throws IOException {
        return Jsons.deserialize(IOs.readFile(Path.of(SECRET_FILE_PATH)));
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
        JsonNode streamSchema) throws IOException {
        return IcebergIntegrationTestUtil.retrieveRecords(getConfig(), namespace, streamName);
    }

    @Override
    protected void setup(TestDestinationEnv testEnv) throws IOException {
    }

    @Override
    protected void tearDown(TestDestinationEnv testEnv) {
    }

}
