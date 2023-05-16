/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.configoss.specs;

import static io.airbyte.configoss.specs.ConnectorSpecMaskDownloader.MASK_FILE;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.yaml.Yamls;
import java.io.File;
import java.nio.charset.Charset;
import java.util.List;
import org.apache.commons.io.FileUtils;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link ConnectorSpecMaskDownloader} class.
 */
class ConnectorSpecMaskDownloaderTest {

  @Test
  void testConnectorSpecMaskDownloader() throws Exception {
    final String directory = "src/test/resources/seed";
    final File outputFile = new File(directory, MASK_FILE);
    final String[] args = {"--specs-root", directory};
    ConnectorSpecMaskDownloader.main(args);
    assertTrue(outputFile.exists());

    final JsonNode maskContents = Yamls.deserialize(FileUtils.readFileToString(outputFile, Charset.defaultCharset()));
    final JsonNode propertiesNode = maskContents.get("properties");
    final List<String> propertiesList = Jsons.object(propertiesNode, new TypeReference<>() {});

    // Assert the properties list is greater than 50.
    // This is a rough sanity check to ensure that the mask file is not empty.
    assertTrue(propertiesList.size() > 50);

  }

}
