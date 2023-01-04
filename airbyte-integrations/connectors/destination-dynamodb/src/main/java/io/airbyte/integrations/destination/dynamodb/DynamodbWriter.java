/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
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

  public DynamodbWriter(final DynamodbDestinationConfig config,
                        final AmazonDynamoDB amazonDynamodb,
                        final ConfiguredAirbyteStream configuredStream,
                        final long uploadTimestamp) {

    this.config = config;
    this.dynamodb = new DynamoDB(amazonDynamodb);
    this.configuredStream = configuredStream;
    this.uploadTimestamp = uploadTimestamp;
    this.outputTableName = DynamodbOutputTableHelper.getOutputTableName(config.getTableNamePrefix(), configuredStream.getStream());

    final DestinationSyncMode syncMode = configuredStream.getDestinationSyncMode();
    if (syncMode == null) {
      throw new IllegalStateException("Undefined destination sync mode");
    }

    final boolean isAppendMode = syncMode != DestinationSyncMode.OVERWRITE;
    final boolean tableExist = true;

    try {
      if (!isAppendMode) {
        final Table table = dynamodb.getTable(outputTableName);

        if (isTableExist(table)) {
          table.delete();
          table.waitForDelete();
        }
      }

      final var table = createTableIfNotExists(amazonDynamodb, outputTableName);
      table.waitForActive();
    } catch (final Exception e) {
      LOGGER.error(e.getMessage(), e);
    }

    this.tableWriteItems = new TableWriteItems(outputTableName);
  }

  private static boolean isTableExist(final Table table) {
    try {
      table.describe();
    } catch (final ResourceNotFoundException e) {
      return false;
    }
    return true;
  }

  private Table createTableIfNotExists(final AmazonDynamoDB amazonDynamodb, final String tableName) throws Exception {
    final AttributeDefinition partitionKeyDefinition = new AttributeDefinition()
        .withAttributeName(JavaBaseConstants.COLUMN_NAME_AB_ID)
        .withAttributeType(ScalarAttributeType.S);
    final AttributeDefinition sortKeyDefinition = new AttributeDefinition()
        .withAttributeName("sync_time")
        .withAttributeType(ScalarAttributeType.N);
    final KeySchemaElement partitionKeySchema = new KeySchemaElement()
        .withAttributeName(JavaBaseConstants.COLUMN_NAME_AB_ID)
        .withKeyType(KeyType.HASH);
    final KeySchemaElement sortKeySchema = new KeySchemaElement()
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

  public void write(final UUID id, final AirbyteRecordMessage recordMessage) {

    final ObjectMapper mapper = new ObjectMapper();
    final Map<String, Object> dataMap = mapper.convertValue(recordMessage.getData(), new TypeReference<Map<String, Object>>() {});

    final var item = new Item()
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
      } catch (final Exception e) {
        LOGGER.error(e.getMessage(), e);
      }
    }
  }

  public void close(final boolean hasFailed) throws IOException {
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
      } catch (final Exception e) {
        LOGGER.error(e.getMessage(), e);
      }
      LOGGER.info("Data writing completed for DynamoDB.");
    }
  }

}
