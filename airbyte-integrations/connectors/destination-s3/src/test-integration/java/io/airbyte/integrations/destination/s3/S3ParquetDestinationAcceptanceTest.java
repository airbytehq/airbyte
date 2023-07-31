/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.standardtest.destination.ProtocolVersion;
import io.airbyte.integrations.standardtest.destination.argproviders.DataArgumentsProvider;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

public class S3ParquetDestinationAcceptanceTest extends S3BaseParquetDestinationAcceptanceTest {

  @Override
  public ProtocolVersion getProtocolVersion() {
    return ProtocolVersion.V1;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new S3AvroParquetTestDataComparator();
  }

  @Override
  protected JsonNode getBaseConfigJson() {
    return S3DestinationTestUtils.getBaseConfigJsonFilePath();
  }

  /**
   * Quick and dirty test to verify that lzo compression works. Probably has some blind spots related
   * to cpu architecture.
   * <p>
   * Only verifies that it runs successfully, which is sufficient to catch any issues with installing
   * the lzo libraries.
   */
  @Test
  public void testLzoCompression() throws Exception {
    final JsonNode config = getConfig().deepCopy();
    ((ObjectNode) config.get("format")).put("compression_codec", "LZO");

    final AirbyteCatalog catalog = Jsons.deserialize(
        MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.getCatalogFileVersion(ProtocolVersion.V0)), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    final List<AirbyteMessage> messages =
        MoreResources.readResource(DataArgumentsProvider.EXCHANGE_RATE_CONFIG.getMessageFileVersion(ProtocolVersion.V0)).lines()
            .map(record -> Jsons.deserialize(record, AirbyteMessage.class))
            .collect(Collectors.toList());

    runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false);
  }

}
