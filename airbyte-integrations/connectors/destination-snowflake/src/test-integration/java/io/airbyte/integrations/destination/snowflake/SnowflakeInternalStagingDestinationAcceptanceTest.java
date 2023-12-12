/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataArgumentsProvider;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.configoss.StandardCheckConnectionOutput;
import io.airbyte.configoss.StandardCheckConnectionOutput.Status;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ArgumentsSource;

@Disabled
public class SnowflakeInternalStagingDestinationAcceptanceTest extends SnowflakeInsertDestinationAcceptanceTest {

  public JsonNode getStaticConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/internal_staging_config.json")));
  }

  @Disabled("See README for why this test is disabled")
  @Test
  public void testCheckWithNoProperStagingPermissionConnection() throws Exception {
    // Config to user (creds) that has no permission to write
    final JsonNode config = Jsons.deserialize(IOs.readFile(
        Path.of("secrets/copy_insufficient_staging_roles_config.json")));

    final StandardCheckConnectionOutput standardCheckConnectionOutput = runCheck(config);

    assertEquals(Status.FAILED, standardCheckConnectionOutput.getStatus());
    assertThat(standardCheckConnectionOutput.getMessage()).contains(NO_USER_PRIVILEGES_ERR_MSG);
  }

  @Disabled("See README for why this test is disabled")
  @Test
  public void testCheckWithNoActiveWarehouseConnection() throws Exception {
    // Config to user(creds) that has no warehouse assigned
    final JsonNode config = Jsons.deserialize(IOs.readFile(
        Path.of("secrets/internal_staging_config_no_active_warehouse.json")));

    final StandardCheckConnectionOutput standardCheckConnectionOutput = runCheck(config);

    assertEquals(Status.FAILED, standardCheckConnectionOutput.getStatus());
    assertThat(standardCheckConnectionOutput.getMessage()).contains(NO_ACTIVE_WAREHOUSE_ERR_MSG);
  }

  @ParameterizedTest
  @ArgumentsSource(DataArgumentsProvider.class)
  public void testSyncWithNormalizationWithKeyPairAuth(final String messagesFilename, final String catalogFilename) throws Exception {
    testSyncWithNormalizationWithKeyPairAuth(messagesFilename, catalogFilename, "secrets/config_key_pair.json");
  }

  @ParameterizedTest
  @ArgumentsSource(DataArgumentsProvider.class)
  public void testSyncWithNormalizationWithKeyPairEncrypt(final String messagesFilename, final String catalogFilename) throws Exception {
    testSyncWithNormalizationWithKeyPairAuth(messagesFilename, catalogFilename, "secrets/config_key_pair_encrypted.json");
  }

  private void testSyncWithNormalizationWithKeyPairAuth(final String messagesFilename, final String catalogFilename, final String configName)
      throws Exception {
    if (!normalizationFromDefinition()) {
      return;
    }

    final AirbyteCatalog catalog = Jsons.deserialize(MoreResources.readResource(catalogFilename), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    final List<AirbyteMessage> messages = MoreResources.readResource(messagesFilename).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());

    final JsonNode config = Jsons.deserialize(IOs.readFile(Path.of(configName)));
    runSyncAndVerifyStateOutput(config, messages, configuredCatalog, true);

    final String defaultSchema = getDefaultSchema(config);
    final List<AirbyteRecordMessage> actualMessages = retrieveNormalizedRecords(catalog, defaultSchema);
    assertSameMessages(messages, actualMessages, true);
  }

}
