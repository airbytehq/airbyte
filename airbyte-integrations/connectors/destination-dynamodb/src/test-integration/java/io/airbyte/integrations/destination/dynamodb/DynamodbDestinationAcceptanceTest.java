/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dynamodb;

import com.amazonaws.ClientConfiguration;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.document.*;
import com.amazonaws.services.dynamodbv2.document.spec.ScanSpec;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.io.IOException;
import java.math.BigDecimal;
import java.nio.file.Path;
import java.util.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DynamodbDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(DynamodbDestinationAcceptanceTest.class);

  protected final String secretFilePath = "secrets/config.json";
  protected JsonNode configJson;
  protected DynamodbDestinationConfig config;
  protected AmazonDynamoDB client;

  protected JsonNode getBaseConfigJson() {
    return Jsons.deserialize(IOs.readFile(Path.of(secretFilePath)));
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-dynamodb:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return configJson;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode baseJson = getBaseConfigJson();
    final JsonNode failCheckJson = Jsons.clone(baseJson);
    // invalid credential
    ((ObjectNode) failCheckJson).put("access_key_id", "fake-key");
    ((ObjectNode) failCheckJson).put("secret_access_key", "fake-secret");
    return failCheckJson;
  }

  /**
   * Helper method to retrieve all synced objects inside the configured bucket path.
   */
  protected List<Item> getAllSyncedObjects(final String streamName, final String namespace) {
    final var dynamodb = new DynamoDB(this.client);
    final var tableName = DynamodbOutputTableHelper.getOutputTableName(this.config.getTableNamePrefix(), streamName, namespace);
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
      LOGGER.error(e.getMessage(), e);
    }

    items.sort(Comparator.comparingLong(o -> ((BigDecimal) o.get(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)).longValue()));

    return items;
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

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    final JsonNode baseConfigJson = getBaseConfigJson();
    // Set a random s3 bucket path for each integration test
    final JsonNode configJson = Jsons.clone(baseConfigJson);
    this.configJson = configJson;
    this.config = DynamodbDestinationConfig.getDynamodbDestinationConfig(configJson);

    final var endpoint = config.getEndpoint();
    final var region = config.getRegion();
    final var accessKeyId = config.getAccessKeyId();
    final var secretAccessKey = config.getSecretAccessKey();

    final var awsCreds = new BasicAWSCredentials(accessKeyId, secretAccessKey);

    if (endpoint.isEmpty()) {
      this.client = AmazonDynamoDBClientBuilder.standard()
          .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
          .withRegion(config.getRegion())
          .build();

    } else {
      final ClientConfiguration clientConfiguration = new ClientConfiguration();
      clientConfiguration.setSignerOverride("AWSDynamodbSignerType");

      this.client = AmazonDynamoDBClientBuilder
          .standard()
          .withEndpointConfiguration(new AwsClientBuilder.EndpointConfiguration(endpoint, region))
          .withClientConfiguration(clientConfiguration)
          .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
          .build();
    }
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    final var dynamodb = new DynamoDB(this.client);
    final List<String> tables = new ArrayList<String>();
    dynamodb.listTables().forEach(o -> {
      if (o.getTableName().startsWith(this.config.getTableNamePrefix()))
        tables.add(o.getTableName());
    });

    try {
      for (final var tableName : tables) {
        final Table table = dynamodb.getTable(tableName);
        table.delete();
        table.waitForDelete();
        LOGGER.info(String.format("Delete table %s", tableName));
      }
    } catch (final Exception e) {
      LOGGER.error(e.getMessage(), e);
    }
  }

}
