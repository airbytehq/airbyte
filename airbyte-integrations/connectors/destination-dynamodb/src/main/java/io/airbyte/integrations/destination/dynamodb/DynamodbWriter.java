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

import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.document.*;
import com.amazonaws.services.dynamodbv2.model.*;
import com.amazonaws.services.dynamodbv2.util.TableUtils;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.io.IOException;
import java.util.Map;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DynamodbWriter {

  protected static final Logger LOGGER = LoggerFactory.getLogger(DynamodbWriter.class);

  private static final ObjectMapper MAPPER = MoreMappers.initMapper();
  private static final ObjectWriter WRITER = MAPPER.writer();

  private final DynamodbDestinationConfig config;
  private final DynamoDB dynamodb;
  private final ConfiguredAirbyteStream configuredStream;
  private final long uploadTimestamp;
  private TableWriteItems tableWriteItems;
  private final String outputTableName;
  private final int batchSize = 25;

  public DynamodbWriter(DynamodbDestinationConfig config,
                        AmazonDynamoDB amazonDynamodb,
                        ConfiguredAirbyteStream configuredStream,
                        long uploadTimestamp) {

    this.config = config;
    this.dynamodb = new DynamoDB(amazonDynamodb);
    this.configuredStream = configuredStream;
    this.uploadTimestamp = uploadTimestamp;
    this.outputTableName = DynamodbOutputTableHelper.getOutputTableName(config.getTableName(), configuredStream.getStream());

    final DestinationSyncMode syncMode = configuredStream.getDestinationSyncMode();
    if (syncMode == null) {
      throw new IllegalStateException("Undefined destination sync mode");
    }

    final boolean isAppendMode = syncMode != DestinationSyncMode.OVERWRITE;
    boolean tableExist = true;

    try {
      if (!isAppendMode) {
        Table table = dynamodb.getTable(outputTableName);

        if (isTableExist(table)) {
          table.delete();
          table.waitForDelete();
        }
      }

      var table = createTableIfNotExists(amazonDynamodb, outputTableName);
      table.waitForActive();
    } catch (Exception e) {
      LOGGER.error(e.getMessage());
    }

    this.tableWriteItems = new TableWriteItems(outputTableName);
  }

  private static boolean isTableExist(Table table) {
    try {
      table.describe();
    } catch (ResourceNotFoundException e) {
      return false;
    }
    return true;
  }

  private Table createTableIfNotExists(AmazonDynamoDB amazonDynamodb, String tableName) throws Exception {
    AttributeDefinition partitionKeyDefinition = new AttributeDefinition()
        .withAttributeName(JavaBaseConstants.COLUMN_NAME_AB_ID)
        .withAttributeType(ScalarAttributeType.S);
    AttributeDefinition sortKeyDefinition = new AttributeDefinition()
        .withAttributeName("sync_time")
        .withAttributeType(ScalarAttributeType.N);
    KeySchemaElement partitionKeySchema = new KeySchemaElement()
        .withAttributeName(JavaBaseConstants.COLUMN_NAME_AB_ID)
        .withKeyType(KeyType.HASH);
    KeySchemaElement sortKeySchema = new KeySchemaElement()
        .withAttributeName("sync_time")
        .withKeyType(KeyType.RANGE);

    TableUtils.createTableIfNotExists(amazonDynamodb, new CreateTableRequest()
        .withTableName(tableName)
        .withAttributeDefinitions(partitionKeyDefinition)
        .withKeySchema(partitionKeySchema)
        .withAttributeDefinitions(sortKeyDefinition)
        .withKeySchema(sortKeySchema)
        .withBillingMode(BillingMode.PAY_PER_REQUEST));
    return new DynamoDB(amazonDynamodb).getTable(tableName);
  }

  public void write(UUID id, AirbyteRecordMessage recordMessage) {

    ObjectMapper mapper = new ObjectMapper();
    Map<String, Object> dataMap = mapper.convertValue(recordMessage.getData(), new TypeReference<Map<String, Object>>() {});

    var item = new Item()
        .withPrimaryKey(JavaBaseConstants.COLUMN_NAME_AB_ID, UUID.randomUUID().toString(), "sync_time", uploadTimestamp)
        .withMap(JavaBaseConstants.COLUMN_NAME_DATA, dataMap)
        .withLong(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, recordMessage.getEmittedAt());
    tableWriteItems.addItemToPut(item);
    BatchWriteItemOutcome outcome;
    if (tableWriteItems.getItemsToPut().size() >= batchSize) {
      try {
        int maxRetries = 5;
        outcome = dynamodb.batchWriteItem(tableWriteItems);
        tableWriteItems = new TableWriteItems(this.outputTableName);

        while (outcome.getUnprocessedItems().size() > 0 && maxRetries > 0) {
          outcome = dynamodb.batchWriteItemUnprocessed(outcome.getUnprocessedItems());
          maxRetries--;
        }

        if (maxRetries == 0) {
          LOGGER.warn(String.format("Unprocessed items count after retry %d times: %s", 5, Integer.toString(outcome.getUnprocessedItems().size())));
        }
      } catch (Exception e) {
        LOGGER.error(e.getMessage());
      }
    }
  }

  public void close(boolean hasFailed) throws IOException {
    if (hasFailed) {
      LOGGER.warn("Failure in writing data to DynamoDB. Aborting...");
    } else {
      try {
        int maxRetries = 5;
        if (tableWriteItems.getItemsToPut().size() > 0) {
          var outcome = dynamodb.batchWriteItem(tableWriteItems);
          while (outcome.getUnprocessedItems().size() > 0 && maxRetries > 0) {
            outcome = dynamodb.batchWriteItemUnprocessed(outcome.getUnprocessedItems());
            maxRetries--;
          }
          if (maxRetries == 0) {
            LOGGER.warn(String.format("Unprocessed items count after retry %d times: %s", 5, Integer.toString(outcome.getUnprocessedItems().size())));
          }
        }
      } catch (Exception e) {
        LOGGER.error(e.getMessage());
      }
      LOGGER.info("Data writing completed for DynamoDB.");
    }
  }

}
