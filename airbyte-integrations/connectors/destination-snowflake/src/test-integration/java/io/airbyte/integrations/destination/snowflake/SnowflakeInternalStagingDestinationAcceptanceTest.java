/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.standardtest.destination.argproviders.DataArgumentsProvider;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ArgumentsSource;

public class SnowflakeInternalStagingDestinationAcceptanceTest extends SnowflakeInsertDestinationAcceptanceTest {

  public JsonNode getStaticConfig() {
    final JsonNode internalStagingConfig = Jsons.deserialize(IOs.readFile(Path.of("secrets/internal_staging_config.json")));
    Preconditions.checkArgument(!SnowflakeDestinationResolver.isS3Copy(internalStagingConfig));
    Preconditions.checkArgument(!SnowflakeDestinationResolver.isGcsCopy(internalStagingConfig));
    return internalStagingConfig;
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

  private void testSyncWithNormalizationWithKeyPairAuth(String messagesFilename, String catalogFilename, String configName) throws Exception {
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
