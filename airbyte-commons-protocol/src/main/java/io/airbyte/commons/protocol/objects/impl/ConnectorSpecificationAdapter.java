/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.objects.impl;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.protocol.objects.ConnectorSpecification;
import io.airbyte.protocol.models.AdvancedAuth;
import io.airbyte.protocol.models.AuthSpecification;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.net.URI;
import java.util.List;
import lombok.EqualsAndHashCode;

@EqualsAndHashCode
public class ConnectorSpecificationAdapter implements ConnectorSpecification {

  final io.airbyte.protocol.models.ConnectorSpecification connectorSpecification;

  public ConnectorSpecificationAdapter(final io.airbyte.protocol.models.ConnectorSpecification connectorSpecification) {
    this.connectorSpecification = connectorSpecification;
  }

  @Override
  public URI getDocumentationUrl() {
    return connectorSpecification.getDocumentationUrl();
  }

  @Override
  public URI getChangelogUrl() {
    return connectorSpecification.getChangelogUrl();
  }

  @Override
  public JsonNode getConnectorSpecification() {
    return connectorSpecification.getConnectionSpecification();
  }

  @Override
  public Boolean isSupportingIncremental() {
    return connectorSpecification.getSupportsIncremental();
  }

  @Override
  public Boolean isSupportingNormalization() {
    return connectorSpecification.getSupportsNormalization();
  }

  @Override
  public Boolean isSupportingDBT() {
    return connectorSpecification.getSupportsDBT();
  }

  @Override
  public List<DestinationSyncMode> getSupportedDestinationSyncModes() {
    return connectorSpecification.getSupportedDestinationSyncModes();
  }

  @Override
  public AuthSpecification getAuthSpecification() {
    return connectorSpecification.getAuthSpecification();
  }

  @Override
  public AdvancedAuth getAdvancedAuth() {
    return connectorSpecification.getAdvancedAuth();
  }

  @Override
  public io.airbyte.protocol.models.ConnectorSpecification getRaw() {
    return connectorSpecification;
  }

}
