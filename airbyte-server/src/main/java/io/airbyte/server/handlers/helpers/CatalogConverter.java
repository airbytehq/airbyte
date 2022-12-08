/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers.helpers;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.api.model.generated.AirbyteCatalog;
import io.airbyte.api.model.generated.AirbyteStream;
import io.airbyte.api.model.generated.AirbyteStreamAndConfiguration;
import io.airbyte.api.model.generated.AirbyteStreamConfiguration;
import io.airbyte.api.model.generated.SelectedFieldInfo;
import io.airbyte.api.model.generated.StreamDescriptor;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.text.Names;
import io.airbyte.config.FieldSelectionData;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.validation.json.JsonValidationException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Convert classes between io.airbyte.protocol.models and io.airbyte.api.model.generated
 */
public class CatalogConverter {

  private static final Logger LOGGER = LoggerFactory.getLogger(CatalogConverter.class);

  private static io.airbyte.api.model.generated.AirbyteStream toApi(final io.airbyte.protocol.models.AirbyteStream stream) {
    return new io.airbyte.api.model.generated.AirbyteStream()
        .name(stream.getName())
        .jsonSchema(stream.getJsonSchema())
        .supportedSyncModes(Enums.convertListTo(stream.getSupportedSyncModes(), io.airbyte.api.model.generated.SyncMode.class))
        .sourceDefinedCursor(stream.getSourceDefinedCursor())
        .defaultCursorField(stream.getDefaultCursorField())
        .sourceDefinedPrimaryKey(stream.getSourceDefinedPrimaryKey())
        .namespace(stream.getNamespace());
  }

  @SuppressWarnings("PMD.AvoidLiteralsInIfCondition")
  private static io.airbyte.protocol.models.AirbyteStream toProtocol(final AirbyteStream stream, AirbyteStreamConfiguration config)
      throws JsonValidationException {
    if (config.getFieldSelectionEnabled() != null && config.getFieldSelectionEnabled()) {
      // Validate the selected field paths.
      if (config.getSelectedFields() == null) {
        throw new JsonValidationException("Requested field selection but no selected fields provided");
      }
      final JsonNode properties = stream.getJsonSchema().findValue("properties");
      if (properties == null || !properties.isObject()) {
        throw new JsonValidationException("Requested field selection but no properties node found");
      }
      for (final var selectedFieldInfo : config.getSelectedFields()) {
        if (selectedFieldInfo.getFieldPath() == null || selectedFieldInfo.getFieldPath().isEmpty()) {
          throw new JsonValidationException("Selected field path cannot be empty");
        }
        if (selectedFieldInfo.getFieldPath().size() > 1) {
          // TODO(mfsiega-airbyte): support nested fields.
          throw new UnsupportedOperationException("Nested field selection not supported");
        }
      }
      // Only include the selected fields.
      List<String> selectedFieldNames = config.getSelectedFields().stream().map((field) -> field.getFieldPath().get(0)).collect(Collectors.toList());
      for (final String selectedFieldName : selectedFieldNames) {
        if (!properties.has(selectedFieldName)) {
          throw new JsonValidationException(String.format("Requested selected field %s not found in JSON schema", selectedFieldName));
        }
      }
      ((ObjectNode) properties).retain(selectedFieldNames);
    }
    return new io.airbyte.protocol.models.AirbyteStream()
        .withName(stream.getName())
        .withJsonSchema(stream.getJsonSchema())
        .withSupportedSyncModes(Enums.convertListTo(stream.getSupportedSyncModes(), io.airbyte.protocol.models.SyncMode.class))
        .withSourceDefinedCursor(stream.getSourceDefinedCursor())
        .withDefaultCursorField(stream.getDefaultCursorField())
        .withSourceDefinedPrimaryKey(Optional.ofNullable(stream.getSourceDefinedPrimaryKey()).orElse(Collections.emptyList()))
        .withNamespace(stream.getNamespace());
  }

  public static io.airbyte.api.model.generated.AirbyteCatalog toApi(final io.airbyte.protocol.models.AirbyteCatalog catalog) {
    return new io.airbyte.api.model.generated.AirbyteCatalog()
        .streams(catalog.getStreams()
            .stream()
            .map(CatalogConverter::toApi)
            .map(s -> new io.airbyte.api.model.generated.AirbyteStreamAndConfiguration()
                .stream(s)
                .config(generateDefaultConfiguration(s)))
            .collect(Collectors.toList()));
  }

  private static io.airbyte.api.model.generated.AirbyteStreamConfiguration generateDefaultConfiguration(final io.airbyte.api.model.generated.AirbyteStream stream) {
    final io.airbyte.api.model.generated.AirbyteStreamConfiguration result = new io.airbyte.api.model.generated.AirbyteStreamConfiguration()
        .aliasName(Names.toAlphanumericAndUnderscore(stream.getName()))
        .cursorField(stream.getDefaultCursorField())
        .destinationSyncMode(io.airbyte.api.model.generated.DestinationSyncMode.APPEND)
        .primaryKey(stream.getSourceDefinedPrimaryKey())
        .selected(true);
    if (stream.getSupportedSyncModes().size() > 0) {
      result.setSyncMode(stream.getSupportedSyncModes().get(0));
    } else {
      result.setSyncMode(io.airbyte.api.model.generated.SyncMode.INCREMENTAL);
    }
    return result;
  }

  public static io.airbyte.api.model.generated.AirbyteCatalog toApi(final ConfiguredAirbyteCatalog catalog, FieldSelectionData fieldSelectionData) {
    final List<io.airbyte.api.model.generated.AirbyteStreamAndConfiguration> streams = catalog.getStreams()
        .stream()
        .map(configuredStream -> {
          final var streamDescriptor = new StreamDescriptor()
              .name(configuredStream.getStream().getName())
              .namespace(configuredStream.getStream().getNamespace());
          final io.airbyte.api.model.generated.AirbyteStreamConfiguration configuration =
              new io.airbyte.api.model.generated.AirbyteStreamConfiguration()
                  .syncMode(Enums.convertTo(configuredStream.getSyncMode(), io.airbyte.api.model.generated.SyncMode.class))
                  .cursorField(configuredStream.getCursorField())
                  .destinationSyncMode(
                      Enums.convertTo(configuredStream.getDestinationSyncMode(), io.airbyte.api.model.generated.DestinationSyncMode.class))
                  .primaryKey(configuredStream.getPrimaryKey())
                  .aliasName(Names.toAlphanumericAndUnderscore(configuredStream.getStream().getName()))
                  .selected(true)
                  .fieldSelectionEnabled(getStreamHasFieldSelectionEnabled(fieldSelectionData, streamDescriptor));
          if (configuration.getFieldSelectionEnabled()) {
            final List<String> selectedColumns = new ArrayList<>();
            // TODO(mfsiega-airbyte): support nested fields here.
            configuredStream.getStream().getJsonSchema().findValue("properties").fieldNames().forEachRemaining((name) -> selectedColumns.add(name));
            configuration.setSelectedFields(
                selectedColumns.stream().map((fieldName) -> new SelectedFieldInfo().addFieldPathItem(fieldName)).collect(Collectors.toList()));
          }
          return new io.airbyte.api.model.generated.AirbyteStreamAndConfiguration()
              .stream(toApi(configuredStream.getStream()))
              .config(configuration);
        })
        .collect(Collectors.toList());
    return new io.airbyte.api.model.generated.AirbyteCatalog().streams(streams);
  }

  private static Boolean getStreamHasFieldSelectionEnabled(FieldSelectionData fieldSelectionData, StreamDescriptor streamDescriptor) {
    if (fieldSelectionData == null
        || fieldSelectionData.getAdditionalProperties().get(streamDescriptorToStringForFieldSelection(streamDescriptor)) == null) {
      return false;
    }

    return fieldSelectionData.getAdditionalProperties().get(streamDescriptorToStringForFieldSelection(streamDescriptor));
  }

  /**
   * Converts the API catalog model into a protocol catalog. Note: returns all streams, regardless of
   * selected status. See
   * {@link CatalogConverter#toProtocol(AirbyteStream, AirbyteStreamConfiguration)} for context.
   *
   * @param catalog api catalog
   * @return protocol catalog
   */
  public static io.airbyte.protocol.models.ConfiguredAirbyteCatalog toProtocolKeepAllStreams(
                                                                                             final io.airbyte.api.model.generated.AirbyteCatalog catalog)
      throws JsonValidationException {
    final AirbyteCatalog clone = Jsons.clone(catalog);
    clone.getStreams().forEach(stream -> stream.getConfig().setSelected(true));
    return toProtocol(clone);
  }

  /**
   * Converts the API catalog model into a protocol catalog. Note: only streams marked as selected
   * will be returned. This is included in this converter as the API model always carries all the
   * streams it has access to and then marks the ones that should not be used as not selected, while
   * the protocol version just uses the presence of the streams as evidence that it should be
   * included.
   *
   * @param catalog api catalog
   * @return protocol catalog
   */
  public static io.airbyte.protocol.models.ConfiguredAirbyteCatalog toProtocol(final io.airbyte.api.model.generated.AirbyteCatalog catalog)
      throws JsonValidationException {
    final ArrayList<JsonValidationException> errors = new ArrayList<>();
    final List<io.airbyte.protocol.models.ConfiguredAirbyteStream> streams = catalog.getStreams()
        .stream()
        .filter(s -> s.getConfig().getSelected())
        .map(s -> {
          try {
            return new io.airbyte.protocol.models.ConfiguredAirbyteStream()
                .withStream(toProtocol(s.getStream(), s.getConfig()))
                .withSyncMode(Enums.convertTo(s.getConfig().getSyncMode(), io.airbyte.protocol.models.SyncMode.class))
                .withCursorField(s.getConfig().getCursorField())
                .withDestinationSyncMode(Enums.convertTo(s.getConfig().getDestinationSyncMode(),
                    io.airbyte.protocol.models.DestinationSyncMode.class))
                .withPrimaryKey(Optional.ofNullable(s.getConfig().getPrimaryKey()).orElse(Collections.emptyList()));
          } catch (JsonValidationException e) {
            LOGGER.error("Error parsing catalog: {}", e);
            errors.add(e);
            return null;
          }
        })
        .collect(Collectors.toList());
    if (!errors.isEmpty()) {
      throw errors.get(0);
    }
    return new io.airbyte.protocol.models.ConfiguredAirbyteCatalog()
        .withStreams(streams);
  }

  /**
   * Generate the map from StreamDescriptor to indicator of whether field selection is enabled for
   * that stream.
   *
   * @param syncCatalog the catalog
   * @return the map as a FieldSelectionData object
   */
  public static FieldSelectionData getFieldSelectionData(final AirbyteCatalog syncCatalog) {
    if (syncCatalog == null) {
      return null;
    }
    final var fieldSelectionData = new FieldSelectionData();
    for (final AirbyteStreamAndConfiguration streamAndConfig : syncCatalog.getStreams()) {
      final var streamDescriptor = new StreamDescriptor()
          .name(streamAndConfig.getStream().getName())
          .namespace(streamAndConfig.getStream().getNamespace());
      final boolean fieldSelectionEnabled =
          streamAndConfig.getConfig().getFieldSelectionEnabled() == null ? false : streamAndConfig.getConfig().getFieldSelectionEnabled();
      fieldSelectionData.setAdditionalProperty(streamDescriptorToStringForFieldSelection(streamDescriptor), fieldSelectionEnabled);
    }
    return fieldSelectionData;
  }

  // Return a string representation of a stream descriptor that's convenient to use as a key for the
  // field selection data.
  private static String streamDescriptorToStringForFieldSelection(final StreamDescriptor streamDescriptor) {
    return String.format("%s/%s", streamDescriptor.getNamespace(), streamDescriptor.getName());
  }

}
