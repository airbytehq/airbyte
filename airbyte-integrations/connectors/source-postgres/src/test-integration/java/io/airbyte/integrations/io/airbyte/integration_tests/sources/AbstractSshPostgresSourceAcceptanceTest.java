/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
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

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
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
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import java.nio.file.Path;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;

public abstract class AbstractSshPostgresSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String STREAM_NAME = "public.id_and_name";
  private static final String STREAM_NAME2 = "public.starships";

  private JsonNode config;

  public abstract Path getConfigFilePath();

  // todo (cgardens) - dynamically create data by generating a database with a random name instead of
  // requiring data to already be in place.
  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    final JsonNode secretsConfig = Jsons.deserialize(IOs.readFile(getConfigFilePath()));
    System.out.println("secretsConfig = " + secretsConfig);
    final JsonNode tunnelMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("tunnel_method", secretsConfig.get("tunnel_method").get("tunnel_method"))
        .put("tunnel_host", secretsConfig.get("tunnel_method").get("tunnel_host"))
        .put("tunnel_ssh_port", secretsConfig.get("tunnel_method").get("tunnel_ssh_port"))
        .put("tunnel_username", secretsConfig.get("tunnel_method").get("tunnel_username"))
        .put("tunnel_userpass", Jsons.getOptional(secretsConfig, "tunnel_method", "tunnel_userpass").map(JsonNode::asText).orElse(""))
        .put("tunnel_user_ssh_key", Jsons.getOptional(secretsConfig, "tunnel_method", "tunnel_user_ssh_key").map(JsonNode::asText).orElse(""))
        .put("tunnel_db_remote_host", secretsConfig.get("tunnel_method").get("tunnel_db_remote_host"))
        .put("tunnel_db_remote_port", secretsConfig.get("tunnel_method").get("tunnel_db_remote_port"))
        .put("tunnel_local_port", secretsConfig.get("tunnel_method").get("tunnel_local_port"))
        .build());

    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "Standard")
        .build());
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", secretsConfig.get("host"))
        .put("port", secretsConfig.get("port"))
        .put("username", secretsConfig.get("username"))
        .put("password", secretsConfig.get("password"))
        .put("database", secretsConfig.get("database"))
        .put("tunnel_method", tunnelMethod)
        .put("ssl", false)
        .put("replication_method", replicationMethod)
        .build());
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {

  }

  @Override
  protected String getImageName() {
    return "airbyte/source-postgres:dev";
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
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME,
                Field.of("id", JsonSchemaPrimitive.NUMBER),
                Field.of("name", JsonSchemaPrimitive.STRING))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                STREAM_NAME2,
                Field.of("id", JsonSchemaPrimitive.NUMBER),
                Field.of("name", JsonSchemaPrimitive.STRING))
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
