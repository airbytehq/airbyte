/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.helpers;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class ConnectorSpecificationHelpers {

  public static ConnectorSpecification generateConnectorSpecification() throws IOException {

    final Path path = Paths.get(ConnectorSpecificationHelpers.class.getClassLoader().getResource("json/TestSpecification.json").getPath());

    try {
      return new ConnectorSpecification()
          .withDocumentationUrl(new URI("https://airbyte.io"))
          .withConnectionSpecification(Jsons.deserialize(Files.readString(path)))
          .withSupportsDBT(false)
          .withSupportsNormalization(false);
    } catch (final URISyntaxException e) {
      throw new RuntimeException(e);
    }
  }

}
