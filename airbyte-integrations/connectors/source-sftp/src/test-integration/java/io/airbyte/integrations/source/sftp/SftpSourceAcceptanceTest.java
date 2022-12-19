/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sftp;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.integrations.util.HostPortResolver;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.Collections;
import java.util.HashMap;
import org.testcontainers.containers.BindMode;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.Network;
import org.testcontainers.images.builder.ImageFromDockerfile;

public class SftpSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String USER = "sftpuser";
  private static final String FOLDER_PATH = "/home/" + USER + "/replication/2022/";
  private static final String CSV_FILE_NAME = "log-20220419.csv";
  private static final String CSV_ERROR_FILE_NAME = "error-20220419.csv";
  private static final String JSON_FILE_NAME = "log-20220420.json";

  private Network network;
  private GenericContainer sftp;

  @Override
  protected String getImageName() {
    return "airbyte/source-sftp:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    String privateKey = sftp.execInContainer("cat", "var/sftp/id_rsa").getStdout();
    JsonNode credentials = Jsons.jsonNode(ImmutableMap.builder()
        .put("auth_method", "SSH_KEY_AUTH")
        .put("auth_ssh_key", privateKey)
        .build());
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("user", USER)
        .put("host", HostPortResolver.resolveHost(sftp))
        .put("port", HostPortResolver.resolvePort(sftp))
        .put("credentials", credentials)
        .put("file_types", "csv,json")
        .put("folder_path", FOLDER_PATH)
        .put("file_pattern", "log-(\\d{4})(\\d{2})(\\d{2})")
        .build());
  }

  @Override
  protected void setupEnvironment(TestDestinationEnv environment) throws Exception {
    network = Network.SHARED;
    sftp = new GenericContainer(
        new ImageFromDockerfile("sftp-test")
            .withFileFromClasspath("Dockerfile", "sftp/Dockerfile"))
                .withNetwork(network)
                .withExposedPorts(22)
                .withClasspathResourceMapping("sftp/" + CSV_FILE_NAME, FOLDER_PATH + CSV_FILE_NAME, BindMode.READ_ONLY)
                .withClasspathResourceMapping("sftp/" + JSON_FILE_NAME, FOLDER_PATH + JSON_FILE_NAME, BindMode.READ_ONLY)
                .withClasspathResourceMapping("sftp/" + CSV_ERROR_FILE_NAME, FOLDER_PATH + CSV_ERROR_FILE_NAME, BindMode.READ_ONLY);
    sftp.start();
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    sftp.stop();
    network.close();
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() throws Exception {
    final ConfiguredAirbyteStream streams =
        CatalogHelpers.createConfiguredAirbyteStream(CSV_FILE_NAME, null, Field.of("value", JsonSchemaType.STRING));
    streams.setSyncMode(SyncMode.FULL_REFRESH);
    return new ConfiguredAirbyteCatalog().withStreams(Collections.singletonList(streams));
  }

  @Override
  protected JsonNode getState() throws Exception {
    return Jsons.jsonNode(new HashMap<>());
  }

}
