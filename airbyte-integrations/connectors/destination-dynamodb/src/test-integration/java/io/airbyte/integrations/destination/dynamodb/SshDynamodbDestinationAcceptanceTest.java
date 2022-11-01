/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dynamodb;

import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder.EndpointConfiguration;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.document.DynamoDB;
import com.amazonaws.services.dynamodbv2.document.Item;
import com.amazonaws.services.dynamodbv2.document.ItemCollection;
import com.amazonaws.services.dynamodbv2.document.ScanOutcome;
import com.amazonaws.services.dynamodbv2.document.spec.ScanSpec;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.ssh.SshBastionContainer;
import io.airbyte.integrations.base.ssh.SshTunnel;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.util.HostPortResolver;
import java.io.IOException;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import org.testcontainers.containers.Network;

public abstract class SshDynamodbDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final SshBastionContainer bastion = new SshBastionContainer();
  private static final Network network = Network.newNetwork();
  private static final DynamoDBContainer dynamoDBContainer = new DynamoDBContainer();
  protected AmazonDynamoDB client;
  private JsonNode configJson;
  private AWSCredentials credentials;
  private EndpointConfiguration endpointConfiguration;


  private String getEndPoint() {
    return String.format("http://%s:%d",
        HostPortResolver.resolveIpAddress(dynamoDBContainer),
        dynamoDBContainer.getExposedPorts().get(0));
  }


  @Override
  protected void setup(final TestDestinationEnv testEnv) throws Exception {
    dynamoDBContainer
        .withNetwork(network);
    dynamoDBContainer.start();
    bastion.initAndStartBastion(network);

    final var endpointUrl = getEndPoint();
    client = dynamoDBContainer.getClient();
    credentials = dynamoDBContainer.getCredentials().getCredentials();

    configJson = bastion.getTunnelConfig(getTunnelMethod(), ImmutableMap.builder()
        .put("dynamodb_endpoint", endpointUrl)
        .put("dynamodb_region", "us-east-2")
        .put("dynamodb_table_name_prefix", "test")
        .put("access_key_id", credentials.getAWSAccessKeyId())
        .put("secret_access_key", credentials.getAWSSecretKey()));

  }


  public abstract SshTunnel.TunnelMethod getTunnelMethod();


  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    dynamoDBContainer.stop();
    dynamoDBContainer.close();
    bastion.getContainer().stop();
    bastion.getContainer().close();
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-dynamodb:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return configJson;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode failCheckJson = Jsons.clone(configJson);
    // invalid credential
    ((ObjectNode) failCheckJson).put("dynamodb_endpoint", "fake-endpoint");
    return failCheckJson;
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
      final String streamName,
      final String namespace,
      final JsonNode streamSchema)
      throws IOException {
    final List<Item> items = getAllSyncedObjects(streamName, namespace);
    final List<JsonNode> jsonRecords = new LinkedList<>();

    for (final var item : items) {
      final var itemJson = item.toJSON();
      jsonRecords.add(Jsons.deserialize(itemJson).get(JavaBaseConstants.COLUMN_NAME_DATA));
    }

    return jsonRecords;
  }

  protected List<Item> getAllSyncedObjects(final String streamName, final String namespace) {
    final var dynamodb = new DynamoDB(client);
    final var tableName = DynamodbOutputTableHelper.getOutputTableName("test", streamName, namespace);
    final var table = dynamodb.getTable(tableName);
    final List<Item> items = new ArrayList<Item>();
    Long maxSyncTime = 0L;

    try {
      final ItemCollection<ScanOutcome> scanItems = table.scan(new ScanSpec());

      final Iterator<Item> iter = scanItems.iterator();
      while (iter.hasNext()) {

        final Item item = iter.next();
        items.add(item);
        maxSyncTime = Math.max(maxSyncTime, ((BigDecimal) item.get("sync_time")).longValue());
      }
    } catch (final Exception e) {
//      LOGGER.error(e.getMessage(), e);
    }

    items.sort(Comparator.comparingLong(o -> ((BigDecimal) o.get(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)).longValue()));

    return items;
  }


}
