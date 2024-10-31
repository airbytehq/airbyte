/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.jupiter.api.Test;

class MongoDbCdcSavedInfoFetcherTest {

  private static final String DATABASE = "test-database";
  private static final String RESUME_TOKEN = "8264BEB9F3000000012B0229296E04";

  @Test
  void testRetrieveSavedOffsetState() {
    final JsonNode offset = MongoDbDebeziumStateUtil.formatState(DATABASE, RESUME_TOKEN);
    final MongoDbCdcState offsetState = new MongoDbCdcState(offset);
    final MongoDbCdcSavedInfoFetcher cdcSavedInfoFetcher = new MongoDbCdcSavedInfoFetcher(offsetState);
    assertEquals(offsetState.state(), cdcSavedInfoFetcher.getSavedOffset());
  }

  @Test
  void testRetrieveSchemaHistory() {
    final JsonNode offset = MongoDbDebeziumStateUtil.formatState(DATABASE, RESUME_TOKEN);
    final MongoDbCdcState offsetState = new MongoDbCdcState(offset);
    final MongoDbCdcSavedInfoFetcher cdcSavedInfoFetcher = new MongoDbCdcSavedInfoFetcher(offsetState);
    assertThrows(RuntimeException.class, () -> cdcSavedInfoFetcher.getSavedSchemaHistory());
  }

}
