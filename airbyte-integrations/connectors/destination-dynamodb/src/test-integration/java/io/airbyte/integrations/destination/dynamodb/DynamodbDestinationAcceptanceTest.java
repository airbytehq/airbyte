/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.jackson.MoreMappers;
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
  protected static final ObjectMapper MAPPER = MoreMappers.initMapper();

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
    JsonNode baseJson = getBaseConfigJson();
    JsonNode failCheckJson = Jsons.clone(baseJson);
    // invalid credential
    ((ObjectNode) failCheckJson).put("access_key_id", "fake-key");
    ((ObjectNode) failCheckJson).put("secret_access_key", "fake-secret");
    return failCheckJson;
  }

  /**
   * Helper method to retrieve all synced objects inside the configured bucket path.
   */
  protected List<Item> getAllSyncedObjects(String streamName, String namespace) {
    var dynamodb = new DynamoDB(this.client);
    var tableName = DynamodbOutputTableHelper.getOutputTableName(this.config.getTableName(), streamName, namespace);
    var table = dynamodb.getTable(tableName);
    List<Item> items = new ArrayList<Item>();
    List<Item> resultItems = new ArrayList<Item>();
    Long maxSyncTime = 0L;

    try {
      ItemCollection<ScanOutcome> scanItems = table.scan(new ScanSpec());

      Iterator<Item> iter = scanItems.iterator();
      while (iter.hasNext()) {

        Item item = iter.next();
        items.add(item);
        maxSyncTime = Math.max(maxSyncTime, ((BigDecimal) item.get("sync_time")).longValue());
      }
    } catch (Exception e) {
      LOGGER.error(e.getMessage());
    }

    Long finalMaxSyncTime = maxSyncTime;
    items.sort(Comparator.comparingLong(o -> ((BigDecimal) o.get(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)).longValue()));

    return items;
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
      throws IOException {
    List<Item> items = getAllSyncedObjects(streamName, namespace);
    List<JsonNode> jsonRecords = new LinkedList<>();

    for (var item : items) {
      var itemJson = item.toJSON();
      jsonRecords.add(Jsons.deserialize(itemJson).get(JavaBaseConstants.COLUMN_NAME_DATA));
    }

    return jsonRecords;
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    JsonNode baseConfigJson = getBaseConfigJson();
    // Set a random s3 bucket path for each integration test
    JsonNode configJson = Jsons.clone(baseConfigJson);
    this.configJson = configJson;
    this.config = DynamodbDestinationConfig.getDynamodbDestinationConfig(configJson);

    var endpoint = config.getEndpoint();
    var region = config.getRegion();
    var accessKeyId = config.getAccessKeyId();
    var secretAccessKey = config.getSecretAccessKey();

    var awsCreds = new BasicAWSCredentials(accessKeyId, secretAccessKey);

    if (endpoint.isEmpty()) {
      this.client = AmazonDynamoDBClientBuilder.standard()
          .withCredentials(new AWSStaticCredentialsProvider(awsCreds))
          .withRegion(config.getRegion())
          .build();

    } else {
      ClientConfiguration clientConfiguration = new ClientConfiguration();
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
  protected void tearDown(TestDestinationEnv testEnv) {
    var dynamodb = new DynamoDB(this.client);
    List<String> tables = new ArrayList<String>();
    dynamodb.listTables().forEach(o -> {
      if (o.getTableName().startsWith(this.config.getTableName()))
        tables.add(o.getTableName());
    });

    try {
      for (var tableName : tables) {
        Table table = dynamodb.getTable(tableName);
        table.delete();
        table.waitForDelete();
        LOGGER.info(String.format("Delete table %s", tableName));
      }
    } catch (Exception e) {
      LOGGER.error(e.getMessage());
    }
  }

}
