package io.airbyte.integrations.source.debezium;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.commons.util.CompositeIterator;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource.TableInfoInternal;
import io.airbyte.integrations.source.jdbc.JdbcStateManager;
import io.airbyte.integrations.source.jdbc.models.CdcState;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.debezium.engine.ChangeEvent;
import java.time.Instant;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.function.Supplier;

public class DebeziumInit {

  private final Map<String, String> connectorProperties;

  public DebeziumInit(Map<String, String> connectorProperties,
      ) {
    this.connectorProperties = connectorProperties;

  }

  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(JsonNode config,
      JdbcDatabase database,
      ConfiguredAirbyteCatalog catalog,
      Map<String, TableInfoInternal> tableNameToTable,
      JdbcStateManager stateManager,
      Instant emittedAt) {
    if (isCdc(config) && shouldUseCDC(catalog)) {
      LOGGER.info("using CDC: {}", true);
      // TODO: Figure out how to set the isCDC of stateManager to true. Its always false
      final AirbyteFileOffsetBackingStore offsetManager = initializeState(stateManager);
      AirbyteSchemaHistoryStorage schemaHistoryManager = initializeDBHistory(stateManager);
      FilteredFileDatabaseHistory.setDatabaseName(config.get("database").asText());
      /**
       * We use 10000 as capacity cause the default queue size and batch size of debezium is :
       * {@link io.debezium.config.CommonConnectorConfig#DEFAULT_MAX_BATCH_SIZE} is 2048
       * {@link io.debezium.config.CommonConnectorConfig#DEFAULT_MAX_QUEUE_SIZE} is 8192
       */
      final LinkedBlockingQueue<ChangeEvent<String, String>> queue = new LinkedBlockingQueue<>(10000);
      final DebeziumRecordPublisher publisher = new DebeziumRecordPublisher(config, catalog, offsetManager, schemaHistoryManager);
      publisher.start(queue);

      Optional<TargetFilePosition> targetFilePosition = TargetFilePosition
          .targetFilePosition(database);

      // handle state machine around pub/sub logic.
      final AutoCloseableIterator<ChangeEvent<String, String>> eventIterator = new DebeziumRecordIterator(
          queue,
          targetFilePosition,
          publisher::hasClosed,
          publisher::close);

      // convert to airbyte message.
      final AutoCloseableIterator<AirbyteMessage> messageIterator = AutoCloseableIterators
          .transform(
              eventIterator,
              (event) -> DebeziumEventUtils.toAirbyteMessage(event, emittedAt));

      // our goal is to get the state at the time this supplier is called (i.e. after all message records
      // have been produced)
      final Supplier<AirbyteMessage> stateMessageSupplier = () -> {
        Map<String, String> offset = offsetManager.readMap();
        String dbHistory = schemaHistoryManager.read();

        Map<String, Object> state = new HashMap<>();
        state.put(MYSQL_CDC_OFFSET, offset);
        state.put(MYSQL_DB_HISTORY, dbHistory);

        final JsonNode asJson = Jsons.jsonNode(state);

        LOGGER.info("debezium state: {}", asJson);

        CdcState cdcState = new CdcState().withState(asJson);
        stateManager.getCdcStateManager().setCdcState(cdcState);
        final AirbyteStateMessage stateMessage = stateManager.emit();
        return new AirbyteMessage().withType(Type.STATE).withState(stateMessage);

      };

      // wrap the supplier in an iterator so that we can concat it to the message iterator.
      final Iterator<AirbyteMessage> stateMessageIterator = MoreIterators
          .singletonIteratorFromSupplier(stateMessageSupplier);

      // this structure guarantees that the debezium engine will be closed, before we attempt to emit the
      // state file. we want this so that we have a guarantee that the debezium offset file (which we use
      // to produce the state file) is up-to-date.
      final CompositeIterator<AirbyteMessage> messageIteratorWithStateDecorator = AutoCloseableIterators
          .concatWithEagerClose(messageIterator,
              AutoCloseableIterators.fromIterator(stateMessageIterator));

      return Collections.singletonList(messageIteratorWithStateDecorator);
    } else {
      LOGGER.info("using CDC: {}", false);
      return super.getIncrementalIterators(config, database, catalog, tableNameToTable, stateManager,
          emittedAt);
    }
  }

}
