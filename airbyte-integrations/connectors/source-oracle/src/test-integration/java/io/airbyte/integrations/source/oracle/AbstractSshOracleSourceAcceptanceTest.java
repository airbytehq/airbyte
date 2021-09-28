/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.ssh.SshHelpers;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import java.nio.file.Path;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;

public abstract class AbstractSshOracleSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String STREAM_NAME = "JDBC_SPACE.ID_AND_NAME";
  private static final String STREAM_NAME2 = "JDBC_SPACE.STARSHIPS";

  private JsonNode config;

  public abstract Path getConfigFilePath();

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    config = Jsons.deserialize(IOs.readFile(getConfigFilePath()));
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {

  }

  @Override
  protected String getImageName() {
    return "airbyte/source-oracle:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return SshHelpers.getSpecAndInjectSsh();
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("ID"))
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME,
                Field.of("ID", JsonSchemaPrimitive.NUMBER),
                Field.of("NAME", JsonSchemaPrimitive.STRING),
                Field.of("POWER", JsonSchemaPrimitive.NUMBER))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("ID"))
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2,
                Field.of("ID", JsonSchemaPrimitive.NUMBER),
                Field.of("NAME", JsonSchemaPrimitive.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

  @Override
  protected List<String> getRegexTests() {
    return Collections.emptyList();
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

}
