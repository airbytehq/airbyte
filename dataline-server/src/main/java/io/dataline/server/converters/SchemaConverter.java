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

package io.dataline.server.converters;

import io.dataline.api.model.SourceSchema;
import io.dataline.api.model.SourceSchemaColumn;
import io.dataline.api.model.SourceSchemaTable;
import io.dataline.commons.enums.Enums;
import io.dataline.config.Column;
import io.dataline.config.DataType;
import io.dataline.config.Schema;
import io.dataline.config.Table;
import java.util.List;
import java.util.stream.Collectors;

public class SchemaConverter {

  public static Schema toPersistenceSchema(SourceSchema sourceSchema) {
    final List<Table> persistenceTables =
        sourceSchema.getTables().stream()
            .map(
                apiTable -> {
                  final List<Column> persistenceColumns =
                      apiTable.getColumns().stream()
                          .map(
                              apiColumn -> new Column()
                                  .withName(apiColumn.getName())
                                  .withDataType(toPersistenceDataType(apiColumn.getDataType()))
                                  .withSelected(apiColumn.getSelected()))
                          .collect(Collectors.toList());

                  return new Table()
                      .withName(apiTable.getName())
                      .withColumns(persistenceColumns)
                      .withSelected(persistenceColumns.stream().anyMatch(Column::getSelected));
                })
            .collect(Collectors.toList());

    return new Schema().withTables(persistenceTables);
  }

  public static SourceSchema toApiSchema(Schema persistenceSchema) {
    final List<SourceSchemaTable> persistenceTables =
        persistenceSchema.getTables().stream()
            .map(
                persistenceTable -> {
                  final List<SourceSchemaColumn> apiColumns =
                      persistenceTable.getColumns().stream()
                          .map(
                              persistenceColumn -> new SourceSchemaColumn()
                                  .name(persistenceColumn.getName())
                                  .dataType(toApiDataType(persistenceColumn.getDataType()))
                                  .selected(persistenceColumn.getSelected()))
                          .collect(Collectors.toList());

                  return new SourceSchemaTable()
                      .name(persistenceTable.getName())
                      .columns(apiColumns);
                })
            .collect(Collectors.toList());

    return new SourceSchema().tables(persistenceTables);
  }

  public static DataType toPersistenceDataType(io.dataline.api.model.DataType apiDataType) {
    return Enums.convertTo(apiDataType, DataType.class);
  }

  public static io.dataline.api.model.DataType toApiDataType(DataType persistenceDataType) {
    return Enums.convertTo(persistenceDataType, io.dataline.api.model.DataType.class);
  }

}
