package io.airbyte.integrations.destination.elasticsearch;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.util.List;
import org.testcontainers.containers.Network;
import org.testcontainers.elasticsearch.ElasticsearchContainer;

public abstract class SshElasticsearchDestinationAcceptanceTest  extends DestinationAcceptanceTest {
  private static final Network network = Network.newNetwork();
  private final SshBastionContainer bastion = new SshBastionContainer();
  private static ElasticsearchContainer container;
  private ObjectMapper mapper = new ObjectMapper();
  public static String ELASTIC_PASSWORD = "MagicWord";

  public abstract SshTunnel.TunnelMethod getTunnelMethod();

  @Override
  protected String getImageName() {
    return "airbyte/destination-elasticsearch:dev";
  }

  @Override
  protected int getMaxRecordValueLimit() {
    return 2000000;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected boolean supportsNormalization() {
    return false;
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    // TODO: Enable supportArrayDataTypeTest after ticket 14568 will be done
    return false;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new AdvancedTestDataComparator();
  }

  private String getEndPoint() {
    return String.format("http://%s:%d",
        container.getContainerInfo().getNetworkSettings()
            .getNetworks()
            .entrySet().stream().findFirst().get().getValue().getIpAddress(),
        container.getExposedPorts().get(0));
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return bastion.getTunnelConfig(getTunnelMethod(), ImmutableMap.builder().put("endpoint", getEndPoint())
        .put("upsert", false)
        .put("authenticationMethod", Jsons.jsonNode(ImmutableMap.builder().put("method", "basic")
            .put("username", "elastic")
            .put("password", ELASTIC_PASSWORD).build())));
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    // should result in a failed connection check
    return bastion.getTunnelConfig(getTunnelMethod(), ImmutableMap.builder().put("endpoint", getEndPoint())
        .put("upsert", true)
        .put("authenticationMethod", Jsons.jsonNode(ImmutableMap.builder().put("method", "basic")
            .put("username", "elastic")
            .put("password", "wrongpassword").build())));
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
      String streamName,
      String namespace,
      JsonNode streamSchema)
      throws Exception {
    // Records returned from this method will be compared against records provided to the connector
    // to verify they were written correctly
    final String indexName = new ElasticsearchWriteConfig()
        .setNamespace(namespace)
        .setStreamName(streamName)
        .getIndexName();

    ElasticsearchConnection connection = new ElasticsearchConnection(mapper.convertValue(getConfig(), ConnectorConfiguration.class));
    return connection.getRecords(indexName);
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws Exception {
    bastion.initAndStartBastion(network);
    container = new ElasticsearchContainer("docker.elastic.co/elasticsearch/elasticsearch:7.15.1")
        .withNetwork(network)
        .withPassword(ELASTIC_PASSWORD);
    container.start();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    ElasticsearchConnection connection = new ElasticsearchConnection(mapper.convertValue(getConfig(), ConnectorConfiguration.class));
    connection.allIndices().forEach(connection::deleteIndexIfPresent);
    connection.close();
    container.stop();
    container.close();
    bastion.getContainer().stop();
    bastion.getContainer().close();
  }
}
