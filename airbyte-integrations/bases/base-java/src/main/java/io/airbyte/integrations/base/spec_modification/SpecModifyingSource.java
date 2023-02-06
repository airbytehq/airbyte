/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.spec_modification;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConnectorSpecification;

/**
 * In some cases we want to prune or mutate the spec for an existing source. The common case is that
 * we want to remove features that are not appropriate for some reason. e.g. In cloud, we do not
 * want to allow users to send data unencrypted.
 */
public abstract class SpecModifyingSource implements Source {

  private final Source source;

  public SpecModifyingSource(final Source source) {
    this.source = source;
  }

  public abstract ConnectorSpecification modifySpec(ConnectorSpecification originalSpec) throws Exception;

  @Override
  public ConnectorSpecification spec() throws Exception {
    return modifySpec(source.spec());
  }

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    return source.check(config);
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) throws Exception {
    return source.discover(config);
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config, final ConfiguredAirbyteCatalog catalog, final JsonNode state)
      throws Exception {
    return source.read(config, catalog, state);
  }

}
