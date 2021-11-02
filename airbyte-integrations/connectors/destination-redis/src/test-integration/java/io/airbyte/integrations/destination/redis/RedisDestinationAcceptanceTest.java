/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeAll;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedisDestinationAcceptanceTest extends DestinationAcceptanceTest {

    private static final Logger LOGGER = LoggerFactory.getLogger(RedisDestinationAcceptanceTest.class);

    private JsonNode configJson;

    private RedisOpsProvider redisOpsProvider;

    private RedisNameTransformer redisNameTransformer;

    private static RedisContainerInitializr.RedisContainer redisContainer;

    @BeforeAll
    static void initContainer() {
        redisContainer = RedisContainerInitializr.initContainer();
    }

    @Override
    protected void setup(TestDestinationEnv testEnv) {
        configJson = TestDataFactory.jsonConfig(
            redisContainer.getHost(),
            redisContainer.getFirstMappedPort()
        );
        var redisConfig = new RedisConfig(configJson);
        redisOpsProvider = new RedisOpsProvider(redisConfig);
        redisNameTransformer = new RedisNameTransformer();
    }

    @Override
    protected void tearDown(TestDestinationEnv testEnv) {
        redisOpsProvider.flush();
    }

    @Override
    protected String getImageName() {
        return "airbyte/destination-redis:dev";
    }

    @Override
    protected JsonNode getConfig() {
        return configJson;
    }

    @Override
    protected boolean implementsNamespaces() {
        return true;
    }

    @Override
    protected JsonNode getFailCheckConfig() {
        return TestDataFactory.jsonConfig(
            "127.0.0.9",
            8080
        );
    }

    @Override
    protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                             String streamName,
                                             String namespace,
                                             JsonNode streamSchema) {
        var nm = redisNameTransformer.outputNamespace(namespace);
        var key = redisNameTransformer.outputKey(streamName);
        return redisOpsProvider.getAll(nm, key).stream()
            .sorted(Comparator.comparing(RedisRecord::getTimestamp))
            .map(RedisRecord::getData)
            .map(Jsons::deserialize)
            .collect(Collectors.toList());
    }

}
