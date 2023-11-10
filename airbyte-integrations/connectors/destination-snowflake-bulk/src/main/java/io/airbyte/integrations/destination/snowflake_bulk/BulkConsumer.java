/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake_bulk;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperations;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BulkConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BulkConsumer.class);

  private static final String CONFIG_STAGE_KEY = "snowflake_stage_name";
  private static final String CONFIG_FORMAT_KEY = "snowflake_file_format";
  private static final int MAX_BULK_FILES = 5; // TODO: 1000
                                               // https://docs.snowflake.com/en/sql-reference/sql/copy-into-table#optional-parameters

  private final JsonNode config;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final SqlOperations sqlOperations;

  private final String configStaging;
  private final String configFormat;
  private final List<AirbyteRecordMessage> messageList;

  // same as JdbcBufferedConsumerFactory
  public BulkConsumer(final Consumer<AirbyteMessage> outputRecordCollector,
      final JdbcDatabase database,
      final SqlOperations sqlOperations,
      final NamingConventionTransformer namingResolver,
      final JsonNode config,
      final ConfiguredAirbyteCatalog catalog) {

    this.config = config;
    this.outputRecordCollector = outputRecordCollector;
    this.sqlOperations = sqlOperations;

    this.configStaging = config.get(CONFIG_STAGE_KEY).asText();
    this.configFormat = config.get(CONFIG_FORMAT_KEY).asText();
    this.messageList = new ArrayList<>();
  }

  @Override
  public void start() {
    LOGGER.info("start staging:{} format:{}", this.configStaging, this.configFormat);
    // todo: ensure table
  }

  @Override
  public void accept(final AirbyteMessage message) {
    if (message.getType() == Type.STATE) {
      LOGGER.info("Emitting state: {}", message);
      outputRecordCollector.accept(message);
      return;
    } else if (message.getType() != Type.RECORD) {
      return;
    }

    final AirbyteRecordMessage recordMessage = message.getRecord();

    LOGGER.info("record: {}", recordMessage);

    this.messageList.add(recordMessage);
    if (this.messageList.size() >= MAX_BULK_FILES) {
      // upload now
      this.flush();
    }
  }

  private void flush() {
    if (this.messageList.size() == 0) {
      return;
    }
    LOGGER.info("uploading {} files", this.messageList.size());

    final String tableName = "testing";

    final String sql = getSqlForMessages(tableName, this.configStaging, this.configFormat, this.messageList);
    LOGGER.info("runSql {}", sql);
    this.messageList.clear();
  }

  @Override
  public void close() {
    LOGGER.info("sync close");
    this.flush();
    LOGGER.info("sync complete");
  }

  private static String getSqlForMessages(
      final String tableName, final String stagingName, final String formatName,
      final List<AirbyteRecordMessage> messages) {
    final StringBuffer sb = new StringBuffer();
    sb.append("COPY INTO ");
    sb.append(tableName); // todo: escape
    sb.append(" FROM @");
    sb.append(stagingName); // todo: escape
    sb.append(" FILE_FORMAT = ");
    sb.append(formatName); // todo: escape
    sb.append(" FILES = (");
    for (int i = 0; i < messages.size(); i++) {
      final String fileName = messages.get(i).getData().get("file_name").asText();
      if (i > 0) {
        sb.append(", ");
      }
      sb.append("'");
      sb.append(fileName);
      sb.append("'");
    }
    sb.append(");");
    return sb.toString();
  }
}
