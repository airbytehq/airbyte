/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.cdc;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcProperties.ExcludedField;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.Test;

class MongoDbDebeziumFieldsUtilTest {

  private static final String COLLECTION1 = "collection1";
  private static final String COLLECTION2 = "collection2";
  private static final String COLLECTION3 = "collection3";

  private static final String FIELD1 = "field1";
  private static final String FIELD2 = "field2";
  private static final String FIELD3 = "field3";
  private static final String FIELD4 = "field4";
  private static final String FIELD5 = "field5";

  private static final String DATABASE = "database";

  @Test
  void getFieldsNotIncludedInCatalogTest() {
    // source
    final AirbyteStream sourceAirbyteStream1 = CatalogHelpers.createAirbyteStream(COLLECTION1, DATABASE,
        Field.of(FIELD1, JsonSchemaType.STRING),
        Field.of(FIELD2, JsonSchemaType.STRING));
    final AirbyteStream sourceAirbyteStream2 = CatalogHelpers.createAirbyteStream(COLLECTION2, DATABASE,
        Field.of(FIELD2, JsonSchemaType.STRING),
        Field.of(FIELD3, JsonSchemaType.STRING));
    final AirbyteStream sourceAirbyteStream3 = CatalogHelpers.createAirbyteStream(COLLECTION3, DATABASE,
        Field.of(FIELD4, JsonSchemaType.STRING),
        Field.of(FIELD5, JsonSchemaType.STRING));

    // configured
    final AirbyteStream configuredAirbyteStream1 = CatalogHelpers.createAirbyteStream(COLLECTION2, DATABASE,
        Field.of(FIELD2, JsonSchemaType.STRING));
    final AirbyteStream configuredAirbyteStream2 = CatalogHelpers.createAirbyteStream(COLLECTION3, DATABASE,
        Field.of(FIELD4, JsonSchemaType.STRING),
        Field.of(FIELD5, JsonSchemaType.STRING));
    final ConfiguredAirbyteCatalog configuredAirbyteCatalog = new ConfiguredAirbyteCatalog().withStreams(
        List.of(new ConfiguredAirbyteStream().withStream(configuredAirbyteStream1),
            new ConfiguredAirbyteStream().withStream(configuredAirbyteStream2)));

    final Set<ExcludedField> fieldsNotIncludedInCatalog =
        MongoDbDebeziumFieldsUtil.getFieldsNotIncludedInConfiguredStreams(
            configuredAirbyteCatalog,
            List.of(sourceAirbyteStream1, sourceAirbyteStream2, sourceAirbyteStream3));

    final Set<ExcludedField> expectedFieldsNotIncludedInCatalog = Set.of(
        new ExcludedField(DATABASE, COLLECTION1, FIELD1),
        new ExcludedField(DATABASE, COLLECTION1, FIELD2),
        new ExcludedField(DATABASE, COLLECTION2, FIELD3));

    assertEquals(expectedFieldsNotIncludedInCatalog, fieldsNotIncludedInCatalog);
  }

}
