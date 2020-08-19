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
  public static Schema toPersistenceSchema(SourceSchema api) {
    final List<Table> persistenceTables =
        api.getTables().stream()
            .map(
                apiTable -> {
                  final List<Column> persistenceColumns =
                      apiTable.getColumns().stream()
                          .map(
                              apiColumn -> {
                                final Column persistenceColumn = new Column();
                                persistenceColumn.setName(apiColumn.getName());
                                persistenceColumn.setDataType(
                                    toPersistenceDataType(apiColumn.getDataType()));
                                return persistenceColumn;
                              })
                          .collect(Collectors.toList());

                  final Table persistenceTable = new Table();
                  persistenceTable.setName(apiTable.getName());
                  persistenceTable.setColumns(persistenceColumns);

                  return persistenceTable;
                })
            .collect(Collectors.toList());

    final Schema persistenceSchema = new Schema();
    persistenceSchema.setTables(persistenceTables);
    return persistenceSchema;
  }

  public static SourceSchema toApiSchema(Schema persistenceSchema) {

    final List<SourceSchemaTable> persistenceTables =
        persistenceSchema.getTables().stream()
            .map(
                persistenceTable -> {
                  final List<SourceSchemaColumn> apiColumns =
                      persistenceTable.getColumns().stream()
                          .map(
                              persistenceColumn -> {
                                final SourceSchemaColumn apiColumn = new SourceSchemaColumn();
                                apiColumn.setName(persistenceColumn.getName());
                                apiColumn.setDataType(
                                    toApiDataType(persistenceColumn.getDataType()));
                                return apiColumn;
                              })
                          .collect(Collectors.toList());

                  final SourceSchemaTable apiTable = new SourceSchemaTable();
                  apiTable.setName(persistenceTable.getName());
                  apiTable.setColumns(apiColumns);

                  return apiTable;
                })
            .collect(Collectors.toList());

    final SourceSchema apiSchema = new SourceSchema();
    apiSchema.setTables(persistenceTables);
    return apiSchema;
  }

  public static DataType toPersistenceDataType(io.dataline.api.model.DataType apiDataType) {
    return Enums.convertTo(apiDataType, DataType.class);
  }

  public static io.dataline.api.model.DataType toApiDataType(DataType persistenceDataType) {
    return Enums.convertTo(persistenceDataType, io.dataline.api.model.DataType.class);
  }
}
