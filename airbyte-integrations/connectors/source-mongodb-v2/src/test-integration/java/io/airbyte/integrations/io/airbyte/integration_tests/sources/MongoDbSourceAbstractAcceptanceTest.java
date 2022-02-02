/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import java.util.HashMap;
import java.util.List;

public abstract class MongoDbSourceAbstractAcceptanceTest extends SourceAcceptanceTest {

  protected static final String DATABASE_NAME = "test";
  protected static final String COLLECTION_NAME = "acceptance_test";

  protected JsonNode config;
  protected MongoDatabase database;

  @Override
  protected String getImageName() {
    return "airbyte/source-mongodb-v2:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return config;
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() throws Exception {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("_id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withCursorField(List.of("_id"))
            .withStream(CatalogHelpers.createAirbyteStream(
                DATABASE_NAME + "." + COLLECTION_NAME,
                Field.of("_id", JsonSchemaPrimitive.STRING),
                Field.of("id", JsonSchemaPrimitive.STRING),
                Field.of("name", JsonSchemaPrimitive.STRING),
                Field.of("test", JsonSchemaPrimitive.STRING),
                Field.of("test_array", JsonSchemaPrimitive.ARRAY),
                Field.of("empty_test", JsonSchemaPrimitive.STRING),
                Field.of("double_test", JsonSchemaPrimitive.NUMBER),
                Field.of("int_test", JsonSchemaPrimitive.NUMBER))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.INCREMENTAL))
                .withDefaultCursorField(List.of("_id")))));
  }

  @Override
  protected JsonNode getState() throws Exception {
    return Jsons.jsonNode(new HashMap<>());
  }

}
