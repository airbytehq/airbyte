/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.objects;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.AdvancedAuth;
import io.airbyte.protocol.models.AuthSpecification;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.net.URI;
import java.util.List;

public interface ConnectorSpecification {

  URI getDocumentationUrl();

  URI getChangelogUrl();

  JsonNode getConnectorSpecification();

  Boolean isSupportingIncremental();

  Boolean isSupportingNormalization();

  Boolean isSupportingDBT();

  // TODO should be a new Enum
  List<DestinationSyncMode> getSupportedDestinationSyncModes();

  // TODO we should introduce specific interfaces
  AuthSpecification getAuthSpecification();

  AdvancedAuth getAdvancedAuth();

  // TODO Temp hack to avoid having to migrate all the code to this interface at once
  io.airbyte.protocol.models.ConnectorSpecification getRaw();

}
