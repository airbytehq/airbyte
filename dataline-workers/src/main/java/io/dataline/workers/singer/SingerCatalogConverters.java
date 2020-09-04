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

package io.dataline.workers.singer;

import io.dataline.commons.json.Jsons;
import io.dataline.config.Column;
import io.dataline.config.DataType;
import io.dataline.config.Schema;
import io.dataline.config.Table;
import io.dataline.singer.SingerCatalog;
import io.dataline.singer.SingerColumn;
import io.dataline.singer.SingerMetadata;
import io.dataline.singer.SingerMetadataChild;
import io.dataline.singer.SingerStream;
import io.dataline.singer.SingerType;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class SingerCatalogConverters {

  /**
   * Takes in a singer catalog and a dataline schema. It then applies the dataline configuration to
   * that catalog. e.g. If dataline says that a certain column should or should not be included in the
   * sync, this method applies that to the catalog. Thus we produce a valid singer catalog that
   * contains configurations stored in dataline.
   *
   * @param catalog - singer catalog
   * @param schema - dataline schema
   * @return singer catalog with dataline schema applied to it.
   */
  public static SingerCatalog applySchemaToDiscoveredCatalog(SingerCatalog catalog, Schema schema) {
    Map<String, Table> tableNameToTable = schema.getTables()
        .stream()
        .collect(Collectors.toMap(Table::getName, table -> table));

    final List<SingerStream> updatedStreams =
        catalog.getStreams().stream()
            .map(
                stream -> {

                  // recourse here is probably to run discovery again and update sync
                  // configuration. this method just outputs the original metadata.
                  if (!tableNameToTable.containsKey(stream.getStream())) {
                    return stream;
                  }
                  final Table table = tableNameToTable.get(stream.getStream());
                  final Map<String, Column> columnNameToColumn =
                      table.getColumns()
                          .stream()
                          .collect(Collectors.toMap(Column::getName, column -> column));

                  final List<SingerMetadata> newMetadata =
                      stream.getMetadata().stream()
                          .map(
                              metadata -> {
                                final SingerMetadata newSingerMetadata = Jsons.clone(metadata);
                                if (isColumnMetadata(metadata)) {
                                  // column metadata
                                  final String columnName = getColumnName(metadata);
                                  // recourse here is probably to run discovery again and update
                                  // sync configuration. this method just outputs the original
                                  // metadata.
                                  if (!columnNameToColumn.containsKey(columnName)) {
                                    return metadata;
                                  }
                                  final Column column = columnNameToColumn.get(columnName);

                                  newSingerMetadata.getMetadata().setSelected(column.getSelected());
                                } else {
                                  // table metadata
                                  // TODO HACK set replication mode to full_refresh on every stream
                                  // to unblock some other dev work. Needs to be fixed ASAP. Sherif
                                  // is working on this.
                                  newSingerMetadata.getMetadata()
                                      .withReplicationMethod(SingerMetadataChild.ReplicationMethod.FULL_TABLE)
                                      .withSelected(table.getSelected());
                                }
                                return newSingerMetadata;
                              })
                          .collect(Collectors.toList());

                  return new SingerStream()
                      .withStream(stream.getStream())
                      .withTableName(stream.getTableName())
                      .withTapStreamId(stream.getTapStreamId())
                      // TODO
                      .withMetadata(newMetadata)
                      // todo (cgardens) - this will not work for legacy catalogs. want to handle this
                      // in a subsequent PR, because handling this is going to require doing another
                      // one of these monster map tasks.
                      .withSchema(stream.getSchema());
                })
            .collect(Collectors.toList());

    return new SingerCatalog().withStreams(updatedStreams);
  }

  // assumes discoverable input only.
  public static Schema toDatalineSchema(SingerCatalog catalog) {
    Map<String, List<SingerMetadata>> tableNameToMetadata =
        getTableNameToMetadataList(catalog.getStreams());

    List<Table> tables = catalog.getStreams()
        .stream()
        .map(
            stream -> {
              final Map<String, SingerMetadataChild> columnNameToMetadata =
                  getColumnMetadataForTable(tableNameToMetadata, stream.getStream());
              final SingerMetadata tableMetadata = tableNameToMetadata.get(stream.getStream())
                  .stream()
                  .filter(metadata -> metadata.getBreadcrumb().equals(new ArrayList<>()))
                  .findFirst()
                  .orElseThrow(() -> new RuntimeException("Could not find table metadata"));
              return new Table()
                  .withName(stream.getStream())
                  .withSelected(isSelected(tableMetadata.getMetadata()))
                  .withColumns(
                      stream
                          .getSchema()
                          .getProperties()
                          .getAdditionalProperties()
                          .entrySet()
                          .stream()
                          .map(
                              entry -> {
                                final String columnName = entry.getKey();
                                final SingerColumn singerColumn = entry.getValue();
                                final SingerMetadataChild singerColumnMetadata =
                                    columnNameToMetadata.get(columnName);

                                final Column column = new Column();
                                column.withName(columnName);
                                column.withDataType(singerTypesToDataType(singerColumn.getType()));
                                // in discovery, you can find columns that are replicated by
                                // default. we set those to selected. the rest are not.
                                column.withSelected(isSelected(singerColumnMetadata));
                                return column;
                              })
                          .collect(Collectors.toList()));
            })
        .collect(Collectors.toList());

    return new Schema().withTables(tables);
  }

  private static boolean isSelected(SingerMetadataChild metadataChild) {
    Boolean selected = metadataChild.getSelected();
    if (selected != null) {
      return metadataChild.getSelected();
    }
    Boolean selectedByDefault = metadataChild.getSelectedByDefault();
    if (selectedByDefault != null) {
      return selectedByDefault;
    }

    // absent of a default, don't replicate by default.
    return false;
  }

  private static Map<String, List<SingerMetadata>> getTableNameToMetadataList(List<SingerStream> streams) {
    // todo (cgardens) - figure out if it's stream or stream id or table name.
    return streams.stream()
        .collect(Collectors.toMap(SingerStream::getStream, SingerStream::getMetadata));
  }

  private static Map<String, SingerMetadataChild> getColumnMetadataForTable(Map<String, List<SingerMetadata>> tableNameToMetadata,
                                                                            String tableName) {
    if (!tableNameToMetadata.containsKey(tableName)) {
      throw new RuntimeException("could not find metadata for table: " + tableName);
    }
    return tableNameToMetadata.get(tableName).stream()
        // singer breadcrumb is empty if it is table metadata and it it has two
        // items if it is column metadata. the first item is "properties" and
        // the second item is the column name.
        .filter(SingerCatalogConverters::isColumnMetadata)
        .collect(
            Collectors.toMap(
                metadata -> metadata.getBreadcrumb().get(1), SingerMetadata::getMetadata));
  }

  private static boolean isColumnMetadata(SingerMetadata metadata) {
    // column metadata must have 2 breadcrumb entries
    if (metadata.getBreadcrumb().size() != 2) {
      return false;
    }
    // column metadata must have first breadcrumb be property
    return !metadata.getBreadcrumb().get(0).equals("property");
  }

  private static String getColumnName(SingerMetadata metadata) {
    if (!isColumnMetadata(metadata)) {
      throw new RuntimeException("Cannot get column name for non-column metadata");
    }

    return metadata.getBreadcrumb().get(1);
  }

  /**
   * Singer tends to have 2 types for columns one of which is null. The null is pretty irrelevant, so
   * look at types and find the first non-null one and use that.
   *
   * @param singerTypes - list of types discovered by singer.
   * @return reduce down to one type which best matches the column's data type
   */
  private static DataType singerTypesToDataType(List<SingerType> singerTypes) {
    return singerTypes.stream()
        .filter(singerType -> !SingerType.NULL.equals(singerType))
        .map(SingerCatalogConverters::singerTypeToDataType)
        .findFirst()
        .orElse(DataType.STRING);
  }

  /**
   * Singer doesn't seem to have an official list of the data types that they support, so we will have
   * to do our best here as we discover them. If it becomes too awful, we can just map types we don't
   * recognize to string.
   *
   * @param singerType - singer's column data type
   * @return best match for our own data type
   */
  private static DataType singerTypeToDataType(SingerType singerType) {
    switch (singerType) {
      case STRING:
        return DataType.STRING;
      case INTEGER:
        return DataType.NUMBER;
      case NULL:
        // noinspection DuplicateBranchesInSwitch
        return DataType.STRING; // todo (cgardens) - hackasaurus rex
      case BOOLEAN:
        return DataType.BOOLEAN;
      default:
        throw new RuntimeException(
            String.format("could not map SingerType: %s to DataType", singerType));
    }
  }

}
