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

import io.dataline.config.Column;
import io.dataline.config.DataType;
import io.dataline.config.Schema;
import io.dataline.config.SingerCatalog;
import io.dataline.config.SingerColumn;
import io.dataline.config.SingerMetadata;
import io.dataline.config.SingerMetadataChild;
import io.dataline.config.SingerStream;
import io.dataline.config.SingerType;
import io.dataline.config.Table;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class SingerCatalogConverters {

  /**
   * Takes in a singer catalog and a dataline schema. It then applies the dataline configuration to
   * that catalog. e.g. If dataline says that a certain column should or should not be included in
   * the sync, this method applies that to the catalog. Thus we produce a valid singer catalog that
   * contains configurations stored in dataline.
   *
   * @param catalog - singer catalog
   * @param schema - dataline schema
   * @return singer catalog with dataline schema applied to it.
   */
  public static SingerCatalog applySchemaToDiscoveredCatalog(SingerCatalog catalog, Schema schema) {
    Map<String, Table> tableNameToTable =
        schema.getTables().stream().collect(Collectors.toMap(Table::getName, table -> table));

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
                      table.getColumns().stream()
                          .collect(Collectors.toMap(Column::getName, column -> column));

                  final List<SingerMetadata> newMetadata =
                      stream.getMetadata().stream()
                          .map(
                              metadata -> {
                                final SingerMetadata newSingerMetadata =
                                    cloneSingerMetadata(metadata);
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
                                  newSingerMetadata
                                      .getMetadata()
                                      .setReplicationMethod(
                                          SingerMetadataChild.ReplicationMethod.FULL_TABLE);
                                  newSingerMetadata.getMetadata().setSelected(table.getSelected());
                                }
                                return newSingerMetadata;
                              })
                          .collect(Collectors.toList());

                  final SingerStream newSingerStream = new SingerStream();
                  newSingerStream.setStream(stream.getStream());
                  newSingerStream.setTableName(stream.getTableName());
                  newSingerStream.setTapStreamId(stream.getTapStreamId());
                  // TODO
                  newSingerStream.setMetadata(newMetadata);
                  // todo (cgardens) - this will not work for legacy catalogs. want to handle this
                  //   in a subsequent PR, because handling this is going to require doing another
                  //   one of these monster map tasks.
                  newSingerStream.setSchema(stream.getSchema());

                  return newSingerStream;
                })
            .collect(Collectors.toList());

    final SingerCatalog outputCatalog = new SingerCatalog();
    outputCatalog.setStreams(updatedStreams);

    return outputCatalog;
  }

  // assumes discoverable input only.
  public static Schema toDatalineSchema(SingerCatalog catalog) {
    Map<String, List<SingerMetadata>> tableNameToMetadata =
        getTableNameToMetadataList(catalog.getStreams());

    List<Table> tables =
        catalog.getStreams().stream()
            .map(
                stream -> {
                  final Map<String, SingerMetadataChild> columnNameToMetadata =
                      getColumnMetadataForTable(tableNameToMetadata, stream.getStream());
                  final SingerMetadata tableMetadata =
                      tableNameToMetadata.get(stream.getStream()).stream()
                          .filter(metadata -> metadata.getBreadcrumb().equals(new ArrayList<>()))
                          .findFirst()
                          .orElseThrow(() -> new RuntimeException("Could not find table metadata"));
                  final Table table = new Table();
                  table.setName(stream.getStream());
                  table.setSelected(
                      tableMetadata.getMetadata().getSelectedByDefault() == null
                          ? false
                          : tableMetadata.getMetadata().getSelectedByDefault());
                  table.setColumns(
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
                                column.setName(columnName);
                                column.setDataType(singerTypesToDataType(singerColumn.getType()));
                                // in discovery, you can find columns that are replicated by
                                // default. we set those to selected. the rest are not.
                                column.setSelected(singerColumnMetadata.getSelectedByDefault());
                                return column;
                              })
                          .collect(Collectors.toList()));
                  return table;
                })
            .collect(Collectors.toList());

    final Schema schema = new Schema();
    schema.setTables(tables);
    return schema;
  }

  private static Map<String, List<SingerMetadata>> getTableNameToMetadataList(
      List<SingerStream> streams) {
    // todo (cgardens) - figure out if it's stream or stream id or table name.
    return streams.stream()
        .collect(Collectors.toMap(SingerStream::getStream, SingerStream::getMetadata));
  }

  private static Map<String, SingerMetadataChild> getColumnMetadataForTable(
      Map<String, List<SingerMetadata>> tableNameToMetadata, String tableName) {
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
   * Singer tends to have 2 types for columns one of which is null. The null is pretty irrelevant,
   * so look at types and find the first non-null one and use that.
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
   * Singer doesn't seem to have an official list of the data types that they support, so we will
   * have to do our best here as we discover them. If it becomes too awful, we can just map types we
   * don't recognize to string.
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
        //noinspection DuplicateBranchesInSwitch
        return DataType.STRING; // todo (cgardens) - hackasaurus rex
      case BOOLEAN:
        return DataType.BOOLEAN;
      default:
        throw new RuntimeException(
            String.format("could not map SingerType: %s to DataType", singerType));
    }
  }

  private static SingerMetadata cloneSingerMetadata(SingerMetadata toClone) {
    // bad variable name. tradeoff to keep stuff on one line.
    SingerMetadataChild toClone2 = toClone.getMetadata();
    final SingerMetadataChild singerMetadataChild = new SingerMetadataChild();
    singerMetadataChild.setSelected(toClone2.getSelected());
    singerMetadataChild.setReplicationMethod(toClone2.getReplicationMethod());
    singerMetadataChild.setReplicationKey(toClone2.getReplicationKey());
    singerMetadataChild.setViewKeyProperties(toClone2.getViewKeyProperties());
    singerMetadataChild.setInclusion(toClone2.getInclusion());
    singerMetadataChild.setSelectedByDefault(toClone2.getSelectedByDefault());
    singerMetadataChild.setValidReplicationKeys(toClone2.getValidReplicationKeys());
    singerMetadataChild.setForcedReplicationMethod(toClone2.getForcedReplicationMethod());
    singerMetadataChild.setTableKeyProperties(toClone2.getTableKeyProperties());
    singerMetadataChild.setSchemaName(toClone2.getSchemaName());
    singerMetadataChild.setIsView(toClone2.getIsView());
    singerMetadataChild.setRowCount(toClone2.getRowCount());
    singerMetadataChild.setDatabaseName(toClone2.getDatabaseName());
    singerMetadataChild.setSqlDatatype(toClone2.getSqlDatatype());

    final SingerMetadata singerMetadata = new SingerMetadata();
    singerMetadata.setBreadcrumb(new ArrayList<>(toClone.getBreadcrumb()));
    singerMetadata.setMetadata(singerMetadataChild);

    return singerMetadata;
  }
}
