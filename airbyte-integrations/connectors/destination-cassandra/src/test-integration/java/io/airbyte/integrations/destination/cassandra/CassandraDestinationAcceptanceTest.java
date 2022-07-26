/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.util.HostPortResolver;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeAll;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CassandraDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private JsonNode configJson;

  private CassandraCqlProvider cassandraCqlProvider;

  private CassandraNameTransformer cassandraNameTransformer;

  private static CassandraContainerInitializr.ConfiguredCassandraContainer cassandraContainer;

  @BeforeAll
  static void initContainer() {
    cassandraContainer = CassandraContainerInitializr.initContainer();
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    configJson = TestDataFactory.createJsonConfig(
        cassandraContainer.getUsername(),
        cassandraContainer.getPassword(),
        HostPortResolver.resolveHost(cassandraContainer),
        HostPortResolver.resolvePort(cassandraContainer));
    var cassandraConfig = new CassandraConfig(configJson);
    cassandraCqlProvider = new CassandraCqlProvider(cassandraConfig);
    cassandraNameTransformer = new CassandraNameTransformer(cassandraConfig);
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    cassandraCqlProvider.retrieveMetadata().forEach(meta -> {
      var keyspace = meta.value1();
      meta.value2().forEach(table -> cassandraCqlProvider.truncate(keyspace, table));
    });
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
        8080);
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema) {
    var keyspace = cassandraNameTransformer.outputKeyspace(namespace);
    var table = cassandraNameTransformer.outputTable(streamName);
    return cassandraCqlProvider.select(keyspace, table).stream()
        .sorted(Comparator.comparing(CassandraRecord::getTimestamp))
        .map(CassandraRecord::getData)
        .map(Jsons::deserialize)
        .collect(Collectors.toList());
  }

}
