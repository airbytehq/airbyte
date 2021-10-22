/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols;

import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

public interface Mapper<T> {

  ConfiguredAirbyteCatalog mapCatalog(ConfiguredAirbyteCatalog catalog);

  T mapMessage(T message);

}
