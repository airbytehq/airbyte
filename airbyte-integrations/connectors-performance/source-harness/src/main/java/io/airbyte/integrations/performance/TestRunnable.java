package io.airbyte.integrations.performance;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.workers.RecordSchemaValidator;
import io.airbyte.workers.WorkerMetricReporter;
import io.airbyte.workers.internal.AirbyteDestination;
import io.airbyte.workers.internal.AirbyteMapper;
import io.airbyte.workers.internal.AirbyteSource;
import io.airbyte.workers.internal.book_keeping.MessageTracker;
import io.airbyte.workers.internal.exception.DestinationException;
import io.airbyte.workers.internal.exception.SourceException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.apache.logging.log4j.core.config.Configurator;
import org.slf4j.MDC;

@Slf4j
public class TestRunnable {
  public static Runnable readFromSrcAndWriteToDstRunnable(final AirbyteSource source,
      final AirbyteDestination destination,
      final ConfiguredAirbyteCatalog catalog,
      final AtomicBoolean cancelled,
      final AirbyteMapper mapper,
      final MessageTracker messageTracker,
      final Map<String, String> mdc,
      final RecordSchemaValidator recordSchemaValidator,
//      final WorkerMetricReporter metricReporter,
      final ThreadedTimeTracker timeHolder,
      final UUID sourceId,
      final boolean fieldSelectionEnabled) {
    return () -> {
      MDC.setContextMap(mdc);
      log.info("Replication thread started.");
      long recordsRead = 0L;
      /*
       * validationErrors must be a ConcurrentHashMap as it may potentially be updated and read in
       * different threads concurrently depending on the {@link
       * io.airbyte.featureflag.PerfBackgroundJsonValidation} feature-flag.
       */
      final ConcurrentHashMap<AirbyteStreamNameNamespacePair, ImmutablePair<Set<String>, Integer>> validationErrors = new ConcurrentHashMap<>();
      final Map<AirbyteStreamNameNamespacePair, List<String>> streamToSelectedFields = new HashMap<>();
      final Map<AirbyteStreamNameNamespacePair, Set<String>> streamToAllFields = new HashMap<>();
      final Map<AirbyteStreamNameNamespacePair, Set<String>> unexpectedFields = new HashMap<>();
      if (fieldSelectionEnabled) {
        populatedStreamToSelectedFields(catalog, streamToSelectedFields);
      }
      populateStreamToAllFields(catalog, streamToAllFields);
      try {
        while (!cancelled.get() && !source.isFinished()) {
          final Optional<AirbyteMessage> messageOptional;
          try {
            messageOptional = source.attemptRead();
          } catch (final Exception e) {
            throw new SourceException("Source process read attempt failed", e);
          }

          if (messageOptional.isPresent()) {
            final AirbyteMessage airbyteMessage = messageOptional.get();
            if (fieldSelectionEnabled) {
              filterSelectedFields(streamToSelectedFields, airbyteMessage);
            }
            validateSchema(recordSchemaValidator, streamToAllFields, unexpectedFields, validationErrors, airbyteMessage);
            final AirbyteMessage message = mapper.mapMessage(airbyteMessage);

            messageTracker.acceptFromSource(message);

//            try {
//              if (message.getType() == Type.CONTROL) {
//                acceptSrcControlMessage(sourceId, message.getControl(), connectorConfigUpdater);
//              }
//            } catch (final Exception e) {
//              log.error("Error updating source configuration", e);
//            }

            try {
              if (message.getType() == Type.RECORD || message.getType() == Type.STATE) {
                destination.accept(message);
              }
            } catch (final Exception e) {
              throw new DestinationException("Destination process message delivery failed", e);
            }

            recordsRead += 1;

            if (recordsRead % 1000 == 0) {
              log.info("Records read: {} ({})", recordsRead, FileUtils.byteCountToDisplaySize(messageTracker.getSyncStatsTracker().getTotalBytesEmitted()));
            }
          } else {
            log.info("Source has no more messages, closing connection.");
            try {
              source.close();
            } catch (final Exception e) {
              throw new SourceException("Source didn't exit properly - check the logs!", e);
            }
          }
        }
        timeHolder.trackSourceReadEndTime();
        log.info("Total records read: {} ({})", recordsRead, FileUtils.byteCountToDisplaySize(messageTracker.getSyncStatsTracker().getTotalBytesEmitted()));
        if (!validationErrors.isEmpty()) {
          validationErrors.forEach((stream, errorPair) -> {
            log.warn("Schema validation errors found for stream {}. Error messages: {}", stream, errorPair.getLeft());
//            metricReporter.trackSchemaValidationError(stream);
          });
        }
        unexpectedFields.forEach((stream, unexpectedFieldNames) -> {
          if (!unexpectedFieldNames.isEmpty()) {
            log.warn("Source {} has unexpected fields [{}] in stream {}", sourceId, String.join(", ", unexpectedFieldNames), stream);
            // TODO(mfsiega-airbyte): publish this as a metric.
          }
        });

        try {
          destination.notifyEndOfInput();
        } catch (final Exception e) {
          throw new DestinationException("Destination process end of stream notification failed", e);
        }
        if (!cancelled.get() && source.getExitValue() != 0) {
          throw new SourceException("Source process exited with non-zero exit code " + source.getExitValue());
        }
      } catch (final Exception e) {
        if (!cancelled.get()) {
          // Although this thread is closed first, it races with the source's closure and can attempt one
          // final read after the source is closed before it's terminated.
          // This read will fail and throw an exception. Because of this, throw exceptions only if the worker
          // was not cancelled.

          if (e instanceof SourceException || e instanceof DestinationException) {
            // Surface Source and Destination exceptions directly so that they can be classified properly by the
            // worker
            throw e;
          } else {
            throw new RuntimeException(e);
          }
        }
      }
    };
  }

  private static void populateStreamToAllFields(final ConfiguredAirbyteCatalog catalog,
      final Map<AirbyteStreamNameNamespacePair, Set<String>> streamToAllFields) {
    final Iterator var2 = catalog.getStreams().iterator();

    while (var2.hasNext()) {
      final ConfiguredAirbyteStream s = (ConfiguredAirbyteStream) var2.next();
      final Set<String> fields = new HashSet();
      final JsonNode propertiesNode = s.getStream().getJsonSchema().findPath("properties");
      if (!propertiesNode.isObject()) {
        throw new RuntimeException("No properties node in stream schema");
      }

      propertiesNode.fieldNames().forEachRemaining((fieldName) -> {
        fields.add(fieldName);
      });
      streamToAllFields.put(AirbyteStreamNameNamespacePair.fromConfiguredAirbyteSteam(s), fields);
    }

  }

  private static void populatedStreamToSelectedFields(final ConfiguredAirbyteCatalog catalog,
      final Map<AirbyteStreamNameNamespacePair, List<String>> streamToSelectedFields) {
    for (final var s : catalog.getStreams()) {
      final List<String> selectedFields = new ArrayList<>();
      final JsonNode propertiesNode = s.getStream().getJsonSchema().findPath("properties");
      if (propertiesNode.isObject()) {
        propertiesNode.fieldNames().forEachRemaining((fieldName) -> selectedFields.add(fieldName));
      } else {
        throw new RuntimeException("No properties node in stream schema");
      }
      streamToSelectedFields.put(AirbyteStreamNameNamespacePair.fromConfiguredAirbyteSteam(s), selectedFields);
    }
  }

  private static void filterSelectedFields(final Map<AirbyteStreamNameNamespacePair, List<String>> streamToSelectedFields,
      final AirbyteMessage airbyteMessage) {
    final AirbyteRecordMessage record = airbyteMessage.getRecord();

    if (record == null) {
      // This isn't a record message, so we don't need to do any filtering.
      return;
    }

    final AirbyteStreamNameNamespacePair messageStream = AirbyteStreamNameNamespacePair.fromRecordMessage(record);
    final List<String> selectedFields = streamToSelectedFields.getOrDefault(messageStream, Collections.emptyList());
    final JsonNode data = record.getData();
    if (data.isObject()) {
      ((ObjectNode) data).retain(selectedFields);
    } else {
      throw new RuntimeException(String.format("Unexpected data in record: %s", data.toString()));
    }
  }


  private static void validateSchema(final RecordSchemaValidator recordSchemaValidator,
      final Map<AirbyteStreamNameNamespacePair, Set<String>> streamToAllFields,
      final Map<AirbyteStreamNameNamespacePair, Set<String>> unexpectedFields,
      final ConcurrentHashMap<AirbyteStreamNameNamespacePair, ImmutablePair<Set<String>, Integer>> validationErrors,
      final AirbyteMessage message) {
    if (message.getRecord() != null) {
      final AirbyteRecordMessage record = message.getRecord();
      final AirbyteStreamNameNamespacePair messageStream = AirbyteStreamNameNamespacePair.fromRecordMessage(record);
      final boolean streamHasLessThenTenErrs =
          validationErrors.get(messageStream) == null || (Integer) ((ImmutablePair) validationErrors.get(messageStream)).getRight() < 10;
      if (streamHasLessThenTenErrs) {
        recordSchemaValidator.validateSchema(record, messageStream, validationErrors);
        final Set<String> unexpectedFieldNames = (Set) unexpectedFields.getOrDefault(messageStream, new HashSet());
        populateUnexpectedFieldNames(record, (Set) streamToAllFields.get(messageStream), unexpectedFieldNames);
        unexpectedFields.put(messageStream, unexpectedFieldNames);
      }

    }
  }

  private static void populateUnexpectedFieldNames(final AirbyteRecordMessage record,
      final Set<String> fieldsInCatalog,
      final Set<String> unexpectedFieldNames) {
    final JsonNode data = record.getData();
    if (data.isObject()) {
      final Iterator<String> fieldNamesInRecord = data.fieldNames();

      while (fieldNamesInRecord.hasNext()) {
        final String fieldName = (String) fieldNamesInRecord.next();
        if (!fieldsInCatalog.contains(fieldName)) {
          unexpectedFieldNames.add(fieldName);
        }
      }
    }

  }

  public static void main(String[] args) {
    var logger = Configurator.initialize(null, "rando.xml");
    System.out.println("Hi!");
  }

}
