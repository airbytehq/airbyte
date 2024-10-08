/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.debezium.CdcMetadataInjector;
import io.airbyte.cdk.integrations.debezium.internals.ChangeEventWithMetadata;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.time.Instant;
import java.util.Set;
import java.util.stream.Collectors;

public class MongoDbDebeziumEventConverter implements DebeziumEventConverter {

  private final CdcMetadataInjector cdcMetadataInjector;
  private final ConfiguredAirbyteCatalog configuredAirbyteCatalog;
  private final Instant emittedAt;
  private final JsonNode config;

  public MongoDbDebeziumEventConverter(
                                       CdcMetadataInjector cdcMetadataInjector,
                                       ConfiguredAirbyteCatalog configuredAirbyteCatalog,
                                       Instant emittedAt,
                                       JsonNode config) {
    this.cdcMetadataInjector = cdcMetadataInjector;
    this.configuredAirbyteCatalog = configuredAirbyteCatalog;
    this.emittedAt = emittedAt;
    this.config = config;
  }

  @Override
  public AirbyteMessage toAirbyteMessage(ChangeEventWithMetadata event) {
    final JsonNode debeziumEventKey = event.getEventKeyAsJson();
    final JsonNode debeziumEvent = event.getEventValueAsJson();
    final JsonNode before = debeziumEvent.get(DebeziumEventConverter.BEFORE_EVENT);
    final JsonNode after = debeziumEvent.get(DebeziumEventConverter.AFTER_EVENT);
    final JsonNode source = debeziumEvent.get(DebeziumEventConverter.SOURCE_EVENT);
    final String operation = debeziumEvent.get(DebeziumEventConverter.OPERATION_FIELD).asText();
    final boolean isEnforceSchema = MongoDbCdcEventUtils.isEnforceSchema(config);

    final Set<String> configuredFields = isEnforceSchema ? getConfiguredMongoDbCollectionFields(source, configuredAirbyteCatalog, cdcMetadataInjector)
        : null;

    /*
     * Delete events need to be handled separately from other CrUD events, as depending on the version
     * of the MongoDB server, the contents Debezium event data will be different. See
     * #formatMongoDbDeleteDebeziumData() for more details.
     */
    final JsonNode data = switch (operation) {
      case "c", "i", "u" -> formatMongoDbDebeziumData(
          before, after, source, debeziumEventKey, cdcMetadataInjector, configuredFields, isEnforceSchema);
      case "d" -> formatMongoDbDeleteDebeziumData(before, debeziumEventKey, source, cdcMetadataInjector, configuredFields, isEnforceSchema);
      default -> throw new IllegalArgumentException("Unsupported MongoDB change event operation '" + operation + "'.");
    };

    return DebeziumEventConverter.buildAirbyteMessage(source, cdcMetadataInjector, emittedAt, data);
  }

  private static JsonNode formatMongoDbDebeziumData(final JsonNode before,
                                                    final JsonNode after,
                                                    final JsonNode source,
                                                    final JsonNode debeziumEventKey,
                                                    final CdcMetadataInjector cdcMetadataInjector,
                                                    final Set<String> configuredFields,
                                                    final boolean isEnforceSchema) {

    if ((before == null || before.isNull()) && (after == null || after.isNull())) {
      // In case a mongodb document was updated and then deleted, the update change event will not have
      // any information ({after: null})
      // We are going to treat it as a delete.
      return formatMongoDbDeleteDebeziumData(before, debeziumEventKey, source, cdcMetadataInjector, configuredFields, isEnforceSchema);
    } else {
      final String eventJson = (after.isNull() ? before : after).asText();
      return DebeziumEventConverter.addCdcMetadata(
          isEnforceSchema
              ? MongoDbCdcEventUtils.transformDataTypes(eventJson, configuredFields)
              : MongoDbCdcEventUtils.transformDataTypesNoSchema(eventJson),
          source, cdcMetadataInjector, false);
    }
  }

  private static JsonNode formatMongoDbDeleteDebeziumData(final JsonNode before,
                                                          final JsonNode debeziumEventKey,
                                                          final JsonNode source,
                                                          final CdcMetadataInjector cdcMetadataInjector,
                                                          final Set<String> configuredFields,
                                                          final boolean isEnforceSchema) {
    final String eventJson;

    /*
     * The change events produced by MongoDB differ based on the server version. For version BEFORE 6.x,
     * the event does not contain the before document. Therefore, the only data that can be extracted is
     * the object ID of the deleted document, which is stored in the event key. Otherwise, if the server
     * is version 6.+ AND the pre-image support has been enabled on the collection, we can use the
     * "before" document from the event to represent the deleted document.
     *
     * See
     * https://www.mongodb.com/docs/manual/reference/change-events/delete/#document-pre--and-post-images
     * for more details.
     */
    if (!before.isNull()) {
      eventJson = before.asText();
    } else {
      eventJson = MongoDbCdcEventUtils.generateObjectIdDocument(debeziumEventKey);
    }

    return DebeziumEventConverter.addCdcMetadata(
        isEnforceSchema
            ? MongoDbCdcEventUtils.transformDataTypes(eventJson, configuredFields)
            : MongoDbCdcEventUtils.transformDataTypesNoSchema(eventJson),
        source, cdcMetadataInjector, true);
  }

  private static Set<String> getConfiguredMongoDbCollectionFields(final JsonNode source,
                                                                  final ConfiguredAirbyteCatalog configuredAirbyteCatalog,
                                                                  final CdcMetadataInjector cdcMetadataInjector) {
    final String streamNamespace = cdcMetadataInjector.namespace(source);
    final String streamName = cdcMetadataInjector.name(source);
    return configuredAirbyteCatalog.getStreams().stream()
        .filter(s -> streamName.equals(s.getStream().getName()) && streamNamespace.equals(s.getStream().getNamespace()))
        .map(CatalogHelpers::getTopLevelFieldNames)
        .flatMap(Set::stream)
        .collect(Collectors.toSet());
  }

}
