/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import static io.airbyte.protocol.models.v0.CatalogHelpers.fieldsToJsonSchema;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Contains utilities and helper classes for discovering schemas in database sources.
 */
public class DbSourceDiscoverUtil {

  private static final Logger LOGGER = LoggerFactory.getLogger(DbSourceDiscoverUtil.class);

  // In case of user manually modified source table schema but did not refresh it and save into the
  // catalog - it can lead to sync failure. This method compare actual schema vs catalog schema
  public static <DataType> void logSourceSchemaChange(final Map<String, TableInfo<CommonField<DataType>>> fullyQualifiedTableNameToInfo,
                                                      final ConfiguredAirbyteCatalog catalog,
                                                      final Function<DataType, JsonSchemaType> airbyteTypeConverter) {
    for (final ConfiguredAirbyteStream airbyteStream : catalog.getStreams()) {
      final AirbyteStream stream = airbyteStream.getStream();
      final String fullyQualifiedTableName = DbSourceDiscoverUtil.getFullyQualifiedTableName(stream.getNamespace(),
          stream.getName());
      if (!fullyQualifiedTableNameToInfo.containsKey(fullyQualifiedTableName)) {
        continue;
      }
      final TableInfo<CommonField<DataType>> table = fullyQualifiedTableNameToInfo.get(fullyQualifiedTableName);
      final List<Field> fields = table.getFields()
          .stream()
          .map(commonField -> toField(commonField, airbyteTypeConverter))
          .distinct()
          .collect(Collectors.toList());
      final JsonNode currentJsonSchema = fieldsToJsonSchema(fields);

      final JsonNode catalogSchema = stream.getJsonSchema();
      if (!catalogSchema.equals(currentJsonSchema)) {
        LOGGER.warn(
            "Source schema changed for table  {}! Actual schema: {}. Catalog schema:  {}",
            fullyQualifiedTableName,
            currentJsonSchema,
            catalogSchema);
      }
    }
  }

  public static <DataType> AirbyteCatalog convertTableInfosToAirbyteCatalog(final List<TableInfo<CommonField<DataType>>> tableInfos,
                                                                            final Map<String, List<String>> fullyQualifiedTableNameToPrimaryKeys,
                                                                            final Function<DataType, JsonSchemaType> airbyteTypeConverter) {
    final List<TableInfo<Field>> tableInfoFieldList = tableInfos.stream()
        .map(t -> {
          // some databases return multiple copies of the same record for a column (e.g. redshift) because
          // they have at least once delivery guarantees. we want to dedupe these, but first we check that the
          // records are actually the same and provide a good error message if they are not.
          assertColumnsWithSameNameAreSame(t.getNameSpace(), t.getName(), t.getFields());
          final List<Field> fields = t.getFields()
              .stream()
              .map(commonField -> toField(commonField, airbyteTypeConverter))
              .distinct()
              .collect(Collectors.toList());
          final String fullyQualifiedTableName = getFullyQualifiedTableName(t.getNameSpace(),
              t.getName());
          final List<String> primaryKeys = fullyQualifiedTableNameToPrimaryKeys.getOrDefault(
              fullyQualifiedTableName, Collections
                  .emptyList());
          return TableInfo.<Field>builder().nameSpace(t.getNameSpace()).name(t.getName())
              .fields(fields).primaryKeys(primaryKeys)
              .cursorFields(t.getCursorFields())
              .build();
        })
        .collect(Collectors.toList());

    final List<AirbyteStream> streams = tableInfoFieldList.stream()
        .map(tableInfo -> {
          final var primaryKeys = tableInfo.getPrimaryKeys().stream()
              .filter(Objects::nonNull)
              .map(Collections::singletonList)
              .collect(Collectors.toList());

          return CatalogHelpers
              .createAirbyteStream(tableInfo.getName(), tableInfo.getNameSpace(),
                  tableInfo.getFields())
              .withSupportedSyncModes(
                  tableInfo.getCursorFields() != null && tableInfo.getCursorFields().isEmpty()
                      ? Lists.newArrayList(SyncMode.FULL_REFRESH)
                      : Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
              .withSourceDefinedPrimaryKey(primaryKeys);
        })
        .collect(Collectors.toList());
    return new AirbyteCatalog().withStreams(streams);
  }

  public static String getFullyQualifiedTableName(final String nameSpace, final String tableName) {
    return nameSpace != null ? nameSpace + "." + tableName : tableName;
  }

  private static <DataType> Field toField(final CommonField<DataType> commonField, final Function<DataType, JsonSchemaType> airbyteTypeConverter) {
    if (airbyteTypeConverter.apply(commonField.getType()) == JsonSchemaType.OBJECT && commonField.getProperties() != null
        && !commonField.getProperties().isEmpty()) {
      final var properties = commonField.getProperties().stream().map(commField -> toField(commField, airbyteTypeConverter)).toList();
      return Field.of(commonField.getName(), airbyteTypeConverter.apply(commonField.getType()), properties);
    } else {
      return Field.of(commonField.getName(), airbyteTypeConverter.apply(commonField.getType()));
    }
  }

  private static <DataType> void assertColumnsWithSameNameAreSame(final String nameSpace,
                                                                  final String tableName,
                                                                  final List<CommonField<DataType>> columns) {
    columns.stream()
        .collect(Collectors.groupingBy(CommonField<DataType>::getName))
        .values()
        .forEach(columnsWithSameName -> {
          final CommonField<DataType> comparisonColumn = columnsWithSameName.get(0);
          columnsWithSameName.forEach(column -> {
            if (!column.equals(comparisonColumn)) {
              throw new RuntimeException(
                  String.format(
                      "Found multiple columns with same name: %s in table: %s.%s but the columns are not the same. columns: %s",
                      comparisonColumn.getName(), nameSpace, tableName, columns));
            }
          });
        });
  }

}
