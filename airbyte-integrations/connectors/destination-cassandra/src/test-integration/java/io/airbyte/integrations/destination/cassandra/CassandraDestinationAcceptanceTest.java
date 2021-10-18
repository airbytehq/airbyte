/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.util.List;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CassandraDestinationAcceptanceTest extends DestinationAcceptanceTest {

    private static final Logger LOGGER = LoggerFactory.getLogger(CassandraDestinationAcceptanceTest.class);

    private JsonNode configJson;

    private CassandraCqlProvider cassandraCqlProvider;

    private CassandraNameTransformer cassandraNameTransformer;

    CassandraContainerInitializr.ConfiguredCassandraContainer cassandraContainer;

    @Override
    protected void setup(TestDestinationEnv testEnv) {
        cassandraContainer = CassandraContainerInitializr.initContainer();
        configJson = TestDataFactory.createJsonConfig(
            cassandraContainer.getUsername(),
            cassandraContainer.getPassword(),
            cassandraContainer.getHost(),
            cassandraContainer.getFirstMappedPort()
        );
        var cassandraConfig = new CassandraConfig(configJson);
        cassandraCqlProvider = new CassandraCqlProvider(cassandraConfig);
        cassandraNameTransformer = new CassandraNameTransformer(cassandraConfig);
    }

    @Override
    protected void tearDown(TestDestinationEnv testEnv) {

    }

    @Override
    protected String getDefaultSchema(JsonNode config) {
        return "";
    }

    @Override
    protected List<JsonNode> retrieveNormalizedRecords(TestDestinationEnv testEnv, String streamName,
                                                       String namespace) {
        return retrieveRecords(testEnv, streamName, namespace, null);
    }

    @Override
    protected String getImageName() {
        return "airbyte/destination-cassandra:dev";
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
        return TestDataFactory.createJsonConfig(
            "usr",
            "pw",
            "127.0.192.1",
            8080
        );
    }

    @Override
    protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                             String streamName,
                                             String namespace,
                                             JsonNode streamSchema) {
        var table = cassandraNameTransformer.outputTable(streamName);
        var keyspace = cassandraNameTransformer.outputKeyspace(namespace);
        return cassandraCqlProvider.select(keyspace, table).stream()
            .map(tableRecord -> Jsons.jsonNode(tableRecord.getData()))
            .collect(Collectors.toList());
    }

}
