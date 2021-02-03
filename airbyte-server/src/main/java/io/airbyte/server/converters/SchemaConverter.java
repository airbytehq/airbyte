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

package io.airbyte.server.converters;

import io.airbyte.api.model.SourceSchema;
import io.airbyte.api.model.SourceSchemaField;
import io.airbyte.api.model.SourceSchemaStream;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.text.Names;
import io.airbyte.config.DataType;
import io.airbyte.config.Field;
import io.airbyte.config.Schema;
import io.airbyte.config.Stream;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Convert classes between io.airbyte.protocol.models and io.airbyte.api.model
 */
public class SchemaConverter {

  public static io.airbyte.api.model.AirbyteStream convertTo(final io.airbyte.protocol.models.AirbyteStream stream) {
    return new io.airbyte.api.model.AirbyteStream()
        .name(stream.getName())
        .jsonSchema(stream.getJsonSchema())
        .supportedSyncModes(Enums.convertListTo(stream.getSupportedSyncModes(), io.airbyte.api.model.SyncMode.class))
        .sourceDefinedCursor(stream.getSourceDefinedCursor())
        .defaultCursorField(stream.getDefaultCursorField());
  }

  public static io.airbyte.protocol.models.AirbyteStream convertTo(final io.airbyte.api.model.AirbyteStream stream) {
    return new io.airbyte.protocol.models.AirbyteStream()
        .withName(stream.getName())
        .withJsonSchema(stream.getJsonSchema())
        .withSupportedSyncModes(Enums.convertListTo(stream.getSupportedSyncModes(), io.airbyte.protocol.models.SyncMode.class))
        .withSourceDefinedCursor(stream.getSourceDefinedCursor())
        .withDefaultCursorField(stream.getDefaultCursorField());
  }

  public static io.airbyte.api.model.AirbyteCatalog convertTo(final io.airbyte.protocol.models.AirbyteCatalog catalog) {
    return new io.airbyte.api.model.AirbyteCatalog()
        .streams(catalog.getStreams()
            .stream()
            .map(SchemaConverter::convertTo)
            .collect(Collectors.toList()));
  }

  public static io.airbyte.protocol.models.AirbyteCatalog convertTo(final io.airbyte.api.model.AirbyteCatalog catalog) {
    return new io.airbyte.protocol.models.AirbyteCatalog()
        .withStreams(catalog.getStreams()
            .stream()
            .map(SchemaConverter::convertTo)
            .collect(Collectors.toList()));
  }

  public static io.airbyte.api.model.ConfiguredAirbyteCatalog convertTo(final io.airbyte.protocol.models.ConfiguredAirbyteCatalog catalog) {
    final List<io.airbyte.api.model.AirbyteStreamAndConfiguration> persistenceStreams = catalog.getStreams()
        .stream()
        .map(configuredStream -> {
          final List<io.airbyte.api.model.AirbyteStreamFieldConfiguration> fields = new ArrayList<>();
          // TODO extract fields
          final io.airbyte.api.model.AirbyteStreamConfiguration configuration = new io.airbyte.api.model.AirbyteStreamConfiguration()
              .syncMode(Enums.convertTo(configuredStream.getSyncMode(), io.airbyte.api.model.SyncMode.class))
              .cursorField(configuredStream.getCursorField())
              // TODO cleanedName?
              .selected(true)
              .fields(fields);
          return new io.airbyte.api.model.AirbyteStreamAndConfiguration()
              .stream(convertTo(configuredStream.getStream()))
              ._configuration(configuration);
        })
        .collect(Collectors.toList());
    return new io.airbyte.api.model.ConfiguredAirbyteCatalog().streams(persistenceStreams);
  }

  public static io.airbyte.protocol.models.ConfiguredAirbyteCatalog convertTo(final io.airbyte.api.model.ConfiguredAirbyteCatalog catalog) {
    return new io.airbyte.protocol.models.ConfiguredAirbyteCatalog().withStreams(catalog.getStreams()
        .stream()
        .map(pair -> new io.airbyte.protocol.models.ConfiguredAirbyteStream()
            .withStream(convertTo(pair.getStream()))
            .withSyncMode(Enums.convertTo(pair.getConfiguration().getSyncMode(), io.airbyte.protocol.models.SyncMode.class))
            .withCursorField(pair.getConfiguration().getCursorField()))
        // TODO filter selected?
        .collect(Collectors.toList()));
  }

  // TODO DEPRECATE BELOW

  public static Schema toPersistenceSchema(SourceSchema sourceSchema) {
    final List<Stream> persistenceStreams =
        sourceSchema.getStreams()
            .stream()
            .map(apiStream -> {
              final List<Field> persistenceFields = apiStream.getFields()
                  .stream()
                  .map(SchemaConverter::toPersistenceField)
                  .collect(Collectors.toList());

              return new Stream()
                  // immutable
                  // todo (cgardens) - not great that we just trust the API to not mutate these.
                  .withName(apiStream.getName())
                  .withFields(persistenceFields)
                  .withSupportedSyncModes(apiStream.getSupportedSyncModes()
                      .stream()
                      .map(e -> Enums.convertTo(e, io.airbyte.config.SyncMode.class))
                      .collect(Collectors.toList()))
                  .withSourceDefinedCursor(apiStream.getSourceDefinedCursor())
                  .withDefaultCursorField(apiStream.getDefaultCursorField())
                  // configurable
                  .withSyncMode(Enums.convertTo(apiStream.getSyncMode(), io.airbyte.config.SyncMode.class))
                  .withCursorField(apiStream.getCursorField())
                  .withSelected(persistenceFields.stream().anyMatch(Field::getSelected));
            })
            .collect(Collectors.toList());

    return new Schema().withStreams(persistenceStreams);
  }

  private static Field toPersistenceField(SourceSchemaField apiField) {
    final Field field = new Field()
        .withName(apiField.getName())
        .withSelected(apiField.getSelected());
    // todo (cgardens) - this is a hack to handle complex types (e.g. anyOf). they will not have a type
    // field set, so we just call them "object". we need to revisit this ASAP.
    if (apiField.getDataType() != null) {
      field.withDataType(Enums.convertTo(apiField.getDataType(), DataType.class));
    } else {
      field.withDataType(DataType.OBJECT);
    }
    return field;
  }

  public static SourceSchema toApiSchema(Schema persistenceSchema) {
    final List<SourceSchemaStream> persistenceStreams = persistenceSchema.getStreams()
        .stream()
        .map(persistenceStream -> {
          final List<SourceSchemaField> apiFields = persistenceStream.getFields()
              .stream()
              .map(SchemaConverter::toApiField)
              .collect(Collectors.toList());

          return new SourceSchemaStream()
              // immutable
              .name(persistenceStream.getName())
              .cleanedName(Names.toAlphanumericAndUnderscore(persistenceStream.getName()))
              .fields(apiFields)
              .supportedSyncModes(persistenceStream.getSupportedSyncModes()
                  .stream().map(e -> Enums.convertTo(e, io.airbyte.api.model.SyncMode.class))
                  .collect(Collectors.toList()))
              .sourceDefinedCursor(persistenceStream.getSourceDefinedCursor())
              .defaultCursorField(persistenceStream.getDefaultCursorField())
              // configurable
              .syncMode(Enums.convertTo(persistenceStream.getSyncMode(), io.airbyte.api.model.SyncMode.class))
              .cursorField(persistenceStream.getCursorField());
        })
        .collect(Collectors.toList());

    return new SourceSchema().streams(persistenceStreams);
  }

  private static SourceSchemaField toApiField(Field persistenceField) {
    final SourceSchemaField field = new SourceSchemaField()
        .name(persistenceField.getName())
        .cleanedName(Names.toAlphanumericAndUnderscore(persistenceField.getName()))
        .selected(persistenceField.getSelected());
    // todo (cgardens) - this is a hack to handle complex types (e.g. anyOf). they will not have a type
    // field set, so we just call them "object". we need to revisit this ASAP.
    if (persistenceField.getDataType() != null) {
      field.dataType(Enums.convertTo(persistenceField.getDataType(), io.airbyte.api.model.DataType.class));
    } else {
      field.dataType(io.airbyte.api.model.DataType.OBJECT);
    }
    return field;
  }

}
