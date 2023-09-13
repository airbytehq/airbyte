/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static io.airbyte.integrations.source.mongodb.MongoConstants.ID_FIELD;
import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.integrations.source.mongodb.MongoCatalogHelper;
import io.airbyte.integrations.source.mongodb.MongoField;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcProperties.ExcludedField;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteStream;
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
    final AirbyteStream sourceAirbyteStream1 = MongoCatalogHelper.buildAirbyteStream(COLLECTION1, DATABASE,
        List.of(MongoField.of(ID_FIELD, JsonSchemaType.STRING),
            MongoField.of(FIELD1, JsonSchemaType.STRING),
            MongoField.of(FIELD2, JsonSchemaType.STRING)));
    final AirbyteStream sourceAirbyteStream2 = MongoCatalogHelper.buildAirbyteStream(COLLECTION2, DATABASE,
        List.of(MongoField.of(ID_FIELD, JsonSchemaType.STRING),
            MongoField.of(FIELD2, JsonSchemaType.STRING),
            MongoField.of(FIELD3, JsonSchemaType.STRING)));
    final AirbyteStream sourceAirbyteStream3 = MongoCatalogHelper.buildAirbyteStream(COLLECTION3, DATABASE,
        List.of(MongoField.of(ID_FIELD, JsonSchemaType.STRING),
            MongoField.of(FIELD4, JsonSchemaType.STRING),
            MongoField.of(FIELD5, JsonSchemaType.STRING)));

    // configured
    final AirbyteStream configuredAirbyteStream1 = MongoCatalogHelper.buildAirbyteStream(COLLECTION2, DATABASE,
        List.of(MongoField.of(FIELD2, JsonSchemaType.STRING)));
    final AirbyteStream configuredAirbyteStream2 = MongoCatalogHelper.buildAirbyteStream(COLLECTION3, DATABASE,
        List.of(MongoField.of(FIELD4, JsonSchemaType.STRING), MongoField.of(FIELD5, JsonSchemaType.STRING)));
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
