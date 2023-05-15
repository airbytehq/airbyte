/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import io.airbyte.integrations.destination.jdbc.copy.StreamCopierFactory;

public interface StarburstGalaxyStreamCopierFactory
    extends StreamCopierFactory<StarburstGalaxyDestinationConfig> {

}
