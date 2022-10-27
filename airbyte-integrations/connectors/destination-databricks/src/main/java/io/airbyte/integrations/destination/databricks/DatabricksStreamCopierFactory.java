/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;

public interface DatabricksStreamCopierFactory extends StreamCopierFactory<DatabricksDestinationConfig> {

}
