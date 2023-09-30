/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium.internals;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage.SchemaHistory;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import java.io.IOException;
import java.util.Optional;
import org.junit.jupiter.api.Test;

public class AirbyteSchemaHistoryStorageTest {

  @Test
  public void testForContentBiggerThan3MBLimit() throws IOException {
    final String contentReadDirectlyFromFile = MoreResources.readResource("dbhistory_greater_than_3_mb.dat");

    final AirbyteSchemaHistoryStorage schemaHistoryStorageFromUncompressedContent = AirbyteSchemaHistoryStorage.initializeDBHistory(
        new SchemaHistory<>(Optional.of(Jsons.jsonNode(contentReadDirectlyFromFile)),
            false),
        true);
    final SchemaHistory<String> schemaHistoryFromUncompressedContent = schemaHistoryStorageFromUncompressedContent.read();

    assertTrue(schemaHistoryFromUncompressedContent.isCompressed());
    assertNotNull(schemaHistoryFromUncompressedContent.schema());
    assertEquals(contentReadDirectlyFromFile, schemaHistoryStorageFromUncompressedContent.readUncompressed());

    final AirbyteSchemaHistoryStorage schemaHistoryStorageFromCompressedContent = AirbyteSchemaHistoryStorage.initializeDBHistory(
        new SchemaHistory<>(Optional.of(Jsons.jsonNode(schemaHistoryFromUncompressedContent.schema())),
            true),
        true);
    final SchemaHistory<String> schemaHistoryFromCompressedContent = schemaHistoryStorageFromCompressedContent.read();

    assertTrue(schemaHistoryFromCompressedContent.isCompressed());
    assertNotNull(schemaHistoryFromCompressedContent.schema());
    assertEquals(schemaHistoryFromUncompressedContent.schema(), schemaHistoryFromCompressedContent.schema());
  }

  @Test
  public void sizeTest() throws IOException {
    assertEquals(5.881045341491699,
        AirbyteSchemaHistoryStorage.calculateSizeOfStringInMB(MoreResources.readResource("dbhistory_greater_than_3_mb.dat")));
    assertEquals(0.0038671493530273438,
        AirbyteSchemaHistoryStorage.calculateSizeOfStringInMB(MoreResources.readResource("dbhistory_less_than_3_mb.dat")));
  }

  @Test
  public void testForContentLessThan3MBLimit() throws IOException {
    final String contentReadDirectlyFromFile = MoreResources.readResource("dbhistory_less_than_3_mb.dat");

    final AirbyteSchemaHistoryStorage schemaHistoryStorageFromUncompressedContent = AirbyteSchemaHistoryStorage.initializeDBHistory(
        new SchemaHistory<>(Optional.of(Jsons.jsonNode(contentReadDirectlyFromFile)),
            false),
        true);
    final SchemaHistory<String> schemaHistoryFromUncompressedContent = schemaHistoryStorageFromUncompressedContent.read();

    assertFalse(schemaHistoryFromUncompressedContent.isCompressed());
    assertNotNull(schemaHistoryFromUncompressedContent.schema());
    assertEquals(contentReadDirectlyFromFile, schemaHistoryFromUncompressedContent.schema());

    final AirbyteSchemaHistoryStorage schemaHistoryStorageFromCompressedContent = AirbyteSchemaHistoryStorage.initializeDBHistory(
        new SchemaHistory<>(Optional.of(Jsons.jsonNode(schemaHistoryFromUncompressedContent.schema())),
            false),
        true);
    final SchemaHistory<String> schemaHistoryFromCompressedContent = schemaHistoryStorageFromCompressedContent.read();

    assertFalse(schemaHistoryFromCompressedContent.isCompressed());
    assertNotNull(schemaHistoryFromCompressedContent.schema());
    assertEquals(schemaHistoryFromUncompressedContent.schema(), schemaHistoryFromCompressedContent.schema());
  }

}
