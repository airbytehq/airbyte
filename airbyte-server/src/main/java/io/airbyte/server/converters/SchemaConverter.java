/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

public class SchemaConverter {

  public static Schema toPersistenceSchema(SourceSchema sourceSchema) {
    final List<Stream> persistenceStreams =
        sourceSchema.getStreams().stream()
            .map(
                apiStream -> {
                  final List<Field> persistenceFields =
                      apiStream.getFields().stream()
                          .map(
                              apiField -> new Field()
                                  .withName(apiField.getName())
                                  .withDataType(Enums.convertTo(apiField.getDataType(), DataType.class))
                                  .withSelected(apiField.getSelected()))
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
                              persistenceField -> new SourceSchemaField()
                                  .name(persistenceField.getName())
                                  .dataType(Enums.convertTo(persistenceField.getDataType(), io.airbyte.api.model.DataType.class))
                                  .selected(persistenceField.getSelected()))
                          .collect(Collectors.toList());

                  return new SourceSchemaStream()
                      .name(persistenceStream.getName())
                      .fields(apiFields);
                })
            .collect(Collectors.toList());

    return new SourceSchema().streams(persistenceStreams);
  }

}
