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
import io.airbyte.config.DataType;
import io.airbyte.config.Field;
import io.airbyte.config.Schema;
import io.airbyte.config.Stream;
import java.util.List;
import java.util.stream.Collectors;

// todo (cgardens) - update this before merging.
public class SchemaConverter {

  public static Schema toPersistenceSchema(SourceSchema sourceSchema) {
    final List<Stream> persistenceStreams =
        sourceSchema.getStreams().stream()
            .map(
                apiStream -> {
                  final List<Field> persistenceFields =
                      apiStream.getFields().stream()
                          .map(
                              apiField -> {
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
                              })
                          .collect(Collectors.toList());

                  return new Stream()
                      .withName(apiStream.getName())
                      .withFields(persistenceFields)
                      .withSelected(persistenceFields.stream().anyMatch(Field::getSelected));
                })
            .collect(Collectors.toList());

    return new Schema().withStreams(persistenceStreams);
  }

  public static SourceSchema toApiSchema(Schema persistenceSchema) {
    final List<SourceSchemaStream> persistenceStreams =
        persistenceSchema.getStreams().stream()
            .map(
                persistenceStream -> {
                  final List<SourceSchemaField> apiFields =
                      persistenceStream.getFields().stream()
                          .map(
                              persistenceField -> {
                                final SourceSchemaField field = new SourceSchemaField()
                                    .name(persistenceField.getName())
                                    .selected(persistenceField.getSelected());
                                // todo (cgardens) - this is a hack to handle complex types (e.g. anyOf). they will not have a type
                                // field set, so we just call them "object". we need to revisit this ASAP.
                                if (persistenceField.getDataType() != null) {
                                  field.dataType(Enums.convertTo(persistenceField.getDataType(), io.airbyte.api.model.DataType.class));
                                } else {
                                  field.dataType(io.airbyte.api.model.DataType.OBJECT);
                                }
                                return field;
                              })
                          .collect(Collectors.toList());

                  return new SourceSchemaStream()
                      .name(persistenceStream.getName())
                      .fields(apiFields);
                })
            .collect(Collectors.toList());

    return new SourceSchema().streams(persistenceStreams);
  }

}
