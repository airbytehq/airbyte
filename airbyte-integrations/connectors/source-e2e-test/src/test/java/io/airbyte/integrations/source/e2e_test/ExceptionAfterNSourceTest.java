/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.SyncMode;
import java.time.Instant;
import org.junit.jupiter.api.Test;

class ExceptionAfterNSourceTest {

  @SuppressWarnings("Convert2MethodRef")
  @Test
  void test() {
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(ExceptionAfterNSource.CATALOG);
    configuredCatalog.getStreams().get(0).setSyncMode(SyncMode.INCREMENTAL);

    final JsonNode config = Jsons.jsonNode(ImmutableMap.of("throw_after_n_records", 10));
    final AutoCloseableIterator<AirbyteMessage> read = new ExceptionAfterNSource().read(config, configuredCatalog, null);
    assertEquals(getStateMessage(0L).getState().getData(), read.next().getState().getData());
    assertEquals(getRecordMessage(1L).getRecord().getData(), read.next().getRecord().getData());
    assertEquals(getRecordMessage(2L).getRecord().getData(), read.next().getRecord().getData());
    assertEquals(getRecordMessage(3L).getRecord().getData(), read.next().getRecord().getData());
    assertEquals(getRecordMessage(4L).getRecord().getData(), read.next().getRecord().getData());
    assertEquals(getRecordMessage(5L).getRecord().getData(), read.next().getRecord().getData());
    assertEquals(getStateMessage(5L).getState().getData(), read.next().getState().getData());
    assertEquals(getRecordMessage(6L).getRecord().getData(), read.next().getRecord().getData());
    assertEquals(getRecordMessage(7L).getRecord().getData(), read.next().getRecord().getData());
    assertEquals(getRecordMessage(8L).getRecord().getData(), read.next().getRecord().getData());
    assertEquals(getRecordMessage(9L).getRecord().getData(), read.next().getRecord().getData());
    assertEquals(getRecordMessage(10L).getRecord().getData(), read.next().getRecord().getData());
    assertEquals(getStateMessage(10L).getState().getData(), read.next().getState().getData());
    assertThrows(IllegalStateException.class, read::next);
  }

  private static AirbyteMessage getRecordMessage(long i) {
    return new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream("data")
            .withEmittedAt(Instant.now().toEpochMilli())
            .withData(Jsons.jsonNode(ImmutableMap.of("column1", i))));
  }

  private static AirbyteMessage getStateMessage(long i) {
    return new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of("column1", i))));
  }

}
