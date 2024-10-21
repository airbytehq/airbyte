/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.dynamodb;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.Disabled;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.PutItemRequest;

@Disabled
public class DynamodbSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String TABLE_NAME = "airbyte_table";

  private JsonNode config;

  private DynamodbContainer dynamodbContainer;

  private DynamoDbClient dynamoDbClient;

  @Override
  protected void setupEnvironment(final TestDestinationEnv testEnv) {
    dynamodbContainer = DynamodbContainer.createWithStart();

    config = DynamodbDataFactory.createJsonConfig(dynamodbContainer);

    dynamoDbClient = DynamodbUtils.createDynamoDbClient(DynamodbConfig.createDynamodbConfig(config));

    var createTableRequests = DynamodbDataFactory.createTables(TABLE_NAME, 1);
    var createTableResponse = dynamoDbClient.createTable(createTableRequests.get(0));
    String tableName = createTableResponse.tableDescription().tableName();

    PutItemRequest putItemRequest = DynamodbDataFactory.putItemRequest(tableName, Map.of(
        "attr_1", AttributeValue.builder().s("str_4").build(),
        "attr_2", AttributeValue.builder().s("str_5").build(),
        "attr_3", AttributeValue.builder().n("1234.25").build(),
        "attr_timestamp", AttributeValue.builder().n("1572268323").build()));

    dynamoDbClient.putItem(putItemRequest);

  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    dynamoDbClient.close();
    dynamodbContainer.stop();
    dynamodbContainer.close();
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-dynamodb:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return DynamodbDataFactory.createConfiguredAirbyteCatalog(TABLE_NAME + 1);
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

}
