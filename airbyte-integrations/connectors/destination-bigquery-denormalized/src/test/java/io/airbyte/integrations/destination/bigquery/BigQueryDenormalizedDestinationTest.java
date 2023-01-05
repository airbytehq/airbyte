/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static com.google.cloud.bigquery.Field.Mode.REPEATED;
import static io.airbyte.integrations.destination.bigquery.util.BigQueryDenormalizedTestSchemaUtils.getSchema;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.core.IsInstanceOf.instanceOf;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.FieldList;
import com.google.cloud.bigquery.LegacySQLTypeName;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.Table;
import com.google.cloud.bigquery.TableDefinition;
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.DefaultBigQueryDenormalizedRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.GcsBigQueryDenormalizedRecordFormatter;
import io.airbyte.integrations.destination.bigquery.formatter.arrayformater.LegacyArrayFormatter;
import io.airbyte.integrations.destination.bigquery.uploader.AbstractBigQueryUploader;
import io.airbyte.integrations.destination.bigquery.uploader.BigQueryDirectUploader;
import io.airbyte.integrations.destination.bigquery.uploader.BigQueryUploaderFactory;
import io.airbyte.integrations.destination.bigquery.uploader.UploaderType;
import io.airbyte.integrations.destination.bigquery.uploader.config.UploaderConfig;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockedStatic;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class BigQueryDenormalizedDestinationTest {

  @Mock
  UploaderConfig uploaderConfigMock;
  @Mock
  ConfiguredAirbyteStream configuredStreamMock;
  @Mock
  AirbyteStream airbyteStreamMock;
  @Mock
  DefaultBigQueryDenormalizedRecordFormatter bigQueryRecordFormatterMock;
  @Mock
  BigQuery bigQueryMock;

  MockedStatic<BigQueryUploaderFactory> uploaderFactoryMock;

  @InjectMocks
  BigQueryDenormalizedDestination bqdd;

  final ObjectMapper mapper = new ObjectMapper();

  @BeforeEach
  void init() {
    uploaderFactoryMock = Mockito.mockStatic(BigQueryUploaderFactory.class, Mockito.CALLS_REAL_METHODS);
    uploaderFactoryMock.when(() -> BigQueryUploaderFactory.getUploader(any(UploaderConfig.class))).thenReturn(mock(BigQueryDirectUploader.class));
  }

  @AfterEach
  public void teardown() {
    uploaderFactoryMock.close();
  }

  @Test
  void getFormatterMap() {
    final JsonNode jsonNodeSchema = getSchema();
    final Map<UploaderType, BigQueryRecordFormatter> formatterMap = bqdd.getFormatterMap(jsonNodeSchema);
    assertEquals(2, formatterMap.size());
    assertTrue(formatterMap.containsKey(UploaderType.AVRO));
    assertTrue(formatterMap.containsKey(UploaderType.STANDARD));
    assertThat(formatterMap.get(UploaderType.AVRO), instanceOf(GcsBigQueryDenormalizedRecordFormatter.class));
    assertThat(formatterMap.get(UploaderType.STANDARD), instanceOf(DefaultBigQueryDenormalizedRecordFormatter.class));
  }

  @Test
  void isDefaultAirbyteTmpTableSchema() {
    assertFalse(bqdd.isDefaultAirbyteTmpTableSchema());
  }

  @Test
  void getRecordFormatterCreator() {
    final BigQuerySQLNameTransformer nameTransformerMock = mock(BigQuerySQLNameTransformer.class);
    final BigQueryRecordFormatter resultFormatter = bqdd.getRecordFormatterCreator(nameTransformerMock)
        .apply(mapper.createObjectNode());

    assertThat(resultFormatter, instanceOf(GcsBigQueryDenormalizedRecordFormatter.class));
  }

  @Test
  void putStreamIntoUploaderMap_compareSchemas_expectedIsNotNullExistingIsNull() throws IOException {
    final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap = new HashMap<>();
    final String streamName = "stream_name";
    final String nameSpace = "name_space";
    final Table tableMock = mock(Table.class);
    final Schema schemaMock = mock(Schema.class);
    final TableDefinition tableDefinitionMock = mock(TableDefinition.class);

    mockBigqueryStream();
    when(tableMock.getDefinition()).thenReturn(tableDefinitionMock);
    when(uploaderConfigMock.getTargetTableName()).thenReturn("target_table");
    when(airbyteStreamMock.getNamespace()).thenReturn(nameSpace);
    when(airbyteStreamMock.getName()).thenReturn(streamName);
    when(bigQueryMock.getTable(anyString(), anyString())).thenReturn(tableMock);

    // expected schema is not null
    when(bigQueryRecordFormatterMock.getBigQuerySchema()).thenReturn(schemaMock);
    // existing schema is null
    when(tableDefinitionMock.getSchema()).thenReturn(null);
    // run test
    bqdd.putStreamIntoUploaderMap(airbyteStreamMock, uploaderConfigMock, uploaderMap);
    // should use LegacyArrayFormatter
    verify(bigQueryRecordFormatterMock, times(1)).setArrayFormatter(any(LegacyArrayFormatter.class));
  }

  @Test
  void putStreamIntoUploaderMap_compareSchemas_existingAndExpectedAreNull() throws IOException {
    final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap = new HashMap<>();
    final Table tableMock = mock(Table.class);
    final TableDefinition tableDefinitionMock = mock(TableDefinition.class);

    mockBigqueryStream();
    when(uploaderConfigMock.getTargetTableName()).thenReturn("target_table");
    when(airbyteStreamMock.getNamespace()).thenReturn("name_space");
    when(airbyteStreamMock.getName()).thenReturn("stream_name");
    when(bigQueryMock.getTable(anyString(), anyString())).thenReturn(tableMock);
    when(tableMock.getDefinition()).thenReturn(tableDefinitionMock);

    // expected schema is null
    when(bigQueryRecordFormatterMock.getBigQuerySchema()).thenReturn(null);
    // existing schema is null
    when(tableDefinitionMock.getSchema()).thenReturn(null);
    // run test
    bqdd.putStreamIntoUploaderMap(airbyteStreamMock, uploaderConfigMock, uploaderMap);
    // should not use LegacyArrayFormatter
    verify(bigQueryRecordFormatterMock, times(0)).setArrayFormatter(any(LegacyArrayFormatter.class));
  }

  @Test
  void putStreamIntoUploaderMap_compareSchemas_expectedSchemaIsNull() throws IOException {
    final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap = new HashMap<>();
    final Table tableMock = mock(Table.class);
    final Schema schemaMock = mock(Schema.class);
    final TableDefinition tableDefinitionMock = mock(TableDefinition.class);

    mockBigqueryStream();
    when(tableMock.getDefinition()).thenReturn(tableDefinitionMock);
    when(uploaderConfigMock.getTargetTableName()).thenReturn("target_table");
    when(bigQueryMock.getTable(anyString(), anyString())).thenReturn(tableMock);
    when(airbyteStreamMock.getNamespace()).thenReturn("name_space");
    when(airbyteStreamMock.getName()).thenReturn("stream_name");
    when(bigQueryMock.getTable(anyString(), anyString())).thenReturn(tableMock);

    // expected schema is null
    when(bigQueryRecordFormatterMock.getBigQuerySchema()).thenReturn(null);
    // existing schema is not null
    when(tableDefinitionMock.getSchema()).thenReturn(schemaMock);
    // run test
    bqdd.putStreamIntoUploaderMap(airbyteStreamMock, uploaderConfigMock, uploaderMap);
    // should use LegacyArrayFormatter
    verify(bigQueryRecordFormatterMock, times(1)).setArrayFormatter(any(LegacyArrayFormatter.class));
  }

  @Test
  void putStreamIntoUploaderMap_isDifferenceBetweenFields_equalType() throws IOException {
    final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap = new HashMap<>();
    final Table tableMock = mock(Table.class);
    final TableDefinition tableDefinitionMock = mock(TableDefinition.class);
    final Schema existingSchemaMock = mock(Schema.class);
    final Schema expectedSchemaMock = mock(Schema.class);

    mockBigqueryStream();
    when(tableMock.getDefinition()).thenReturn(tableDefinitionMock);
    when(tableDefinitionMock.getSchema()).thenReturn(existingSchemaMock);
    when(bigQueryRecordFormatterMock.getBigQuerySchema()).thenReturn(expectedSchemaMock);
    when(uploaderConfigMock.getTargetTableName()).thenReturn("target_table");
    when(airbyteStreamMock.getNamespace()).thenReturn("name_space");
    when(bigQueryMock.getTable(anyString(), anyString())).thenReturn(tableMock);

    final FieldList existingFields = FieldList.of(Field.newBuilder("name", StandardSQLTypeName.STRING).build());
    final FieldList expectedFields = FieldList.of(Field.newBuilder("name", StandardSQLTypeName.STRING).build());
    when(existingSchemaMock.getFields()).thenReturn(existingFields);
    when(expectedSchemaMock.getFields()).thenReturn(expectedFields);

    // run test
    bqdd.putStreamIntoUploaderMap(airbyteStreamMock, uploaderConfigMock, uploaderMap);
    // equal type should not use LegacyArrayFormatter
    verify(bigQueryRecordFormatterMock, times(0)).setArrayFormatter(any(LegacyArrayFormatter.class));
  }

  @Test
  void putStreamIntoUploaderMap_isDifferenceBetweenFields_notEqualType() throws IOException {
    final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap = new HashMap<>();
    final Table tableMock = mock(Table.class);
    final TableDefinition tableDefinitionMock = mock(TableDefinition.class);
    final Schema existingSchemaMock = mock(Schema.class);
    final Schema expectedSchemaMock = mock(Schema.class);

    mockBigqueryStream();
    when(tableMock.getDefinition()).thenReturn(tableDefinitionMock);
    when(tableDefinitionMock.getSchema()).thenReturn(existingSchemaMock);
    when(bigQueryRecordFormatterMock.getBigQuerySchema()).thenReturn(expectedSchemaMock);
    when(uploaderConfigMock.getTargetTableName()).thenReturn("target_table");
    when(airbyteStreamMock.getNamespace()).thenReturn("name_space");
    when(bigQueryMock.getTable(anyString(), anyString())).thenReturn(tableMock);

    final FieldList existingFields = FieldList.of(Field.newBuilder("name", StandardSQLTypeName.DATE).build());
    final FieldList expectedFields = FieldList.of(Field.newBuilder("name", StandardSQLTypeName.STRING).build());
    when(existingSchemaMock.getFields()).thenReturn(existingFields);
    when(expectedSchemaMock.getFields()).thenReturn(expectedFields);

    // run test
    bqdd.putStreamIntoUploaderMap(airbyteStreamMock, uploaderConfigMock, uploaderMap);

    // equal type should not use LegacyArrayFormatter
    verify(bigQueryRecordFormatterMock, times(1)).setArrayFormatter(any(LegacyArrayFormatter.class));
  }

  @Test
  void putStreamIntoUploaderMap_isDifferenceBetweenFields_existingFieldIsNull() throws IOException {
    final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap = new HashMap<>();
    final Table tableMock = mock(Table.class);
    final TableDefinition tableDefinitionMock = mock(TableDefinition.class);
    final Schema existingSchemaMock = mock(Schema.class);
    final Schema expectedSchemaMock = mock(Schema.class);

    mockBigqueryStream();
    when(tableMock.getDefinition()).thenReturn(tableDefinitionMock);
    when(tableDefinitionMock.getSchema()).thenReturn(existingSchemaMock);
    when(bigQueryRecordFormatterMock.getBigQuerySchema()).thenReturn(expectedSchemaMock);
    when(uploaderConfigMock.getTargetTableName()).thenReturn("target_table");
    when(airbyteStreamMock.getNamespace()).thenReturn("name_space");
    when(bigQueryMock.getTable(anyString(), anyString())).thenReturn(tableMock);

    final FieldList expectedFields = FieldList.of(Field.newBuilder("name", StandardSQLTypeName.STRING).build());
    final FieldList existingFields = mock(FieldList.class);
    when(existingSchemaMock.getFields()).thenReturn(existingFields);
    when(expectedSchemaMock.getFields()).thenReturn(expectedFields);
    when(existingFields.get(anyString())).thenReturn(null);

    // run test
    bqdd.putStreamIntoUploaderMap(airbyteStreamMock, uploaderConfigMock, uploaderMap);

    // equal type should not use LegacyArrayFormatter
    verify(bigQueryRecordFormatterMock, times(1)).setArrayFormatter(any(LegacyArrayFormatter.class));
  }

  @Test
  void putStreamIntoUploaderMap_compareRepeatedMode_isEqual() throws IOException {
    final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap = new HashMap<>();
    final Table tableMock = mock(Table.class);
    final TableDefinition tableDefinitionMock = mock(TableDefinition.class);
    final Schema existingSchemaMock = mock(Schema.class);
    final Schema expectedSchemaMock = mock(Schema.class);

    when(tableMock.getDefinition()).thenReturn(tableDefinitionMock);
    when(tableDefinitionMock.getSchema()).thenReturn(existingSchemaMock);
    when(bigQueryRecordFormatterMock.getBigQuerySchema()).thenReturn(expectedSchemaMock);
    mockBigqueryStream();
    when(uploaderConfigMock.getTargetTableName()).thenReturn("target_table");
    when(airbyteStreamMock.getNamespace()).thenReturn("name_space");
    when(airbyteStreamMock.getName()).thenReturn("stream_name");
    when(bigQueryMock.getTable(anyString(), anyString())).thenReturn(tableMock);

    final FieldList existingFields = FieldList.of(Field.newBuilder("name", StandardSQLTypeName.STRING).setMode(REPEATED).build());
    final FieldList expectedFields = FieldList.of(Field.newBuilder("name", StandardSQLTypeName.STRING).setMode(REPEATED).build());
    when(existingSchemaMock.getFields()).thenReturn(existingFields);
    when(expectedSchemaMock.getFields()).thenReturn(expectedFields);
    // run test
    bqdd.putStreamIntoUploaderMap(airbyteStreamMock, uploaderConfigMock, uploaderMap);
    // equal mode should not use LegacyArrayFormatter
    verify(bigQueryRecordFormatterMock, times(0)).setArrayFormatter(any(LegacyArrayFormatter.class));
  }

  @Test
  void putStreamIntoUploaderMap_compareSubFields_equalType() throws IOException {
    final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap = new HashMap<>();
    final String streamName = "stream_name";
    final String nameSpace = "name_space";
    final Table tableMock = mock(Table.class);
    final TableDefinition tableDefinitionMock = mock(TableDefinition.class);
    final Schema existingSchemaMock = mock(Schema.class);
    final Schema expectedSchemaMock = mock(Schema.class);

    when(tableMock.getDefinition()).thenReturn(tableDefinitionMock);
    when(tableDefinitionMock.getSchema()).thenReturn(existingSchemaMock);
    when(bigQueryRecordFormatterMock.getBigQuerySchema()).thenReturn(expectedSchemaMock);
    mockBigqueryStream();
    when(uploaderConfigMock.getTargetTableName()).thenReturn("target_table");
    when(airbyteStreamMock.getNamespace()).thenReturn(nameSpace);
    when(airbyteStreamMock.getName()).thenReturn(streamName);
    when(bigQueryMock.getTable(anyString(), anyString())).thenReturn(tableMock);

    final FieldList expectedSubField = FieldList.of(Field.newBuilder("sub_field_name", StandardSQLTypeName.STRING).build());
    final FieldList existingSubField = FieldList.of(Field.newBuilder("sub_field_name", StandardSQLTypeName.STRING).build());
    final Field existingField = Field.newBuilder("field_name", LegacySQLTypeName.RECORD, existingSubField).build();
    final Field expectedField = Field.newBuilder("field_name", LegacySQLTypeName.RECORD, expectedSubField).build();
    when(existingSchemaMock.getFields()).thenReturn(FieldList.of(existingField));
    when(expectedSchemaMock.getFields()).thenReturn(FieldList.of(expectedField));
    // run test
    bqdd.putStreamIntoUploaderMap(airbyteStreamMock, uploaderConfigMock, uploaderMap);
    // equal subfield type should not use LegacyArrayFormatter
    verify(bigQueryRecordFormatterMock, times(0)).setArrayFormatter(any(LegacyArrayFormatter.class));
  }

  @Test
  void putStreamIntoUploaderMap_compareSubFields_notEqualType() throws IOException {
    final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap = new HashMap<>();
    final String streamName = "stream_name";
    final String nameSpace = "name_space";
    final Table tableMock = mock(Table.class);
    final TableDefinition tableDefinitionMock = mock(TableDefinition.class);
    final Schema existingSchemaMock = mock(Schema.class);
    final Schema expectedSchemaMock = mock(Schema.class);

    when(tableMock.getDefinition()).thenReturn(tableDefinitionMock);
    when(tableDefinitionMock.getSchema()).thenReturn(existingSchemaMock);
    when(bigQueryRecordFormatterMock.getBigQuerySchema()).thenReturn(expectedSchemaMock);
    mockBigqueryStream();
    when(uploaderConfigMock.getTargetTableName()).thenReturn("target_table");
    when(airbyteStreamMock.getNamespace()).thenReturn(nameSpace);
    when(airbyteStreamMock.getName()).thenReturn(streamName);
    when(bigQueryMock.getTable(anyString(), anyString())).thenReturn(tableMock);

    final FieldList expectedSubField = FieldList.of(Field.newBuilder("sub_field_name", StandardSQLTypeName.DATE).build());
    final FieldList existingSubField = FieldList.of(Field.newBuilder("sub_field_name", StandardSQLTypeName.STRING).build());
    final Field existingField = Field.newBuilder("field_name", LegacySQLTypeName.RECORD, existingSubField).build();
    final Field expectedField = Field.newBuilder("field_name", LegacySQLTypeName.RECORD, expectedSubField).build();
    when(existingSchemaMock.getFields()).thenReturn(FieldList.of(existingField));
    when(expectedSchemaMock.getFields()).thenReturn(FieldList.of(expectedField));
    // run test
    bqdd.putStreamIntoUploaderMap(airbyteStreamMock, uploaderConfigMock, uploaderMap);
    // not equal subfield type should use LegacyArrayFormatter
    verify(bigQueryRecordFormatterMock, times(1)).setArrayFormatter(any(LegacyArrayFormatter.class));
  }

  @Test
  void putStreamIntoUploaderMap_existingTableIsNull() throws IOException {
    final Map<AirbyteStreamNameNamespacePair, AbstractBigQueryUploader<?>> uploaderMap = new HashMap<>();
    final String streamName = "stream_name";
    final String nameSpace = "name_space";
    final String targetTableName = "target_table";
    final AirbyteStreamNameNamespacePair expectedResult = new AirbyteStreamNameNamespacePair(streamName, nameSpace);

    mockBigqueryStream();
    when(uploaderConfigMock.getTargetTableName()).thenReturn(targetTableName);
    when(airbyteStreamMock.getNamespace()).thenReturn(nameSpace);
    when(airbyteStreamMock.getName()).thenReturn(streamName);
    // existing table is null
    when(bigQueryMock.getTable(anyString(), anyString())).thenReturn(null);

    // run test
    bqdd.putStreamIntoUploaderMap(airbyteStreamMock, uploaderConfigMock, uploaderMap);

    verify(bigQueryRecordFormatterMock, times(0)).setArrayFormatter(any(LegacyArrayFormatter.class));
    assertTrue(uploaderMap.containsKey(expectedResult));
  }

  private void mockBigqueryStream() {
    when(uploaderConfigMock.getConfigStream()).thenReturn(configuredStreamMock);
    when(uploaderConfigMock.getBigQuery()).thenReturn(bigQueryMock);
    when(uploaderConfigMock.getFormatter()).thenReturn(bigQueryRecordFormatterMock);
    when(configuredStreamMock.getStream()).thenReturn(airbyteStreamMock);
  }

}
